"""
Prediction Service — Central Orchestrator
Combines ML ensemble, NLP, drug intelligence, and report generation.
Returns unified structured response matching API spec.
"""

from models.predictor import MultiModelPredictor
from services.drug_service import DrugIntelligenceService
from services.clinical_intelligence import ClinicalIntelligenceService

import pickle
import functools
import datetime
from typing import Tuple, Any
from utils.clinical_registry import ClinicalRegistry

def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except Exception:
        pass

# Try enhanced NLP first, fall back to basic
try:
    from nlp.processor_enhanced import NLPProcessorEnhanced as NLPProcessor
    safe_print("[OK] Using Enhanced NLP Processor")
except ImportError:
    from nlp.processor import NLPProcessor
    safe_print("[FALLBACK] Using Basic NLP Processor (enhanced not available)")

class PredictionService:
    def __init__(self):
        safe_print("Initializing PredictionService...")

        # Initialize predictors for each disease
        self.predictors = {}
        for disease in ["diabetes", "heart", "mental"]:
            try:
                self.predictors[disease] = MultiModelPredictor(disease)
            except Exception as e:
                safe_print(f"  Warning: {disease} predictor init failed: {e}")
                if "diabetes" in self.predictors:
                    self.predictors[disease] = self.predictors["diabetes"]

        self.nlp = NLPProcessor()
        self.drug_service = DrugIntelligenceService()
        self.clinical_intel = ClinicalIntelligenceService()
        safe_print("PredictionService ready.")

    @functools.lru_cache(maxsize=128)
    def _cached_predict(self, features_tuple: Tuple[float, ...], disease_type: str) -> Tuple[float, str]:
        """Cached predictor wrapper - tuple features for hashability."""
        features = list(features_tuple)
        predictor = self.predictors.get(disease_type, self.predictors.get("diabetes"))
        probability, explanation = predictor.predict(features)
        return probability, explanation

    def _build_model_metadata(self, disease_type, predictor, probability):
        manifest = getattr(predictor, "manifest", {}) or {}
        ml_accuracies = manifest.get("ml_accuracies", {})
        ensemble_results = manifest.get("ensemble_results", {}).get("ensemble", {})
        best_ml_model = manifest.get("best_ml_model")
        best_ml_accuracy = ml_accuracies.get(best_ml_model) if best_ml_model else None

        return {
            "requested_disease": disease_type,
            "trained_artifacts_available": bool(manifest),
            "model_version": manifest.get("version", "untracked"),
            "prediction_method": "ensemble_bayesian_weighted" if getattr(predictor, "use_ensemble", False) else "individual_weighted",
            "best_ml_model": best_ml_model,
            "best_ml_accuracy": round(float(best_ml_accuracy), 4) if best_ml_accuracy is not None else None,
            "ensemble_accuracy": round(float(ensemble_results.get("accuracy")), 4) if ensemble_results.get("accuracy") is not None else None,
            "ensemble_auc": round(float(ensemble_results.get("auc")), 4) if ensemble_results.get("auc") is not None else None,
            "training_samples": manifest.get("training_samples"),
            "validation_samples": manifest.get("validation_samples"),
            "test_samples": manifest.get("test_samples"),
            "features_expected": manifest.get("features_expected"),
            "ensemble_strategy": manifest.get("ensemble_strategy"),
            "calibrated_probability": round(float(probability), 4),
        }

    def handle_prediction(self, features, prescription, disease_type="diabetes", user_id=None, patient_id=None, patient_name=None, treating_doctor_id=None):
        """
        Full prediction pipeline:
        1. ML/DL ensemble prediction
        2. NLP entity extraction
        3. Drug validation
        4. Clinical Intelligence (Abnormalities, Validation, Recommendations)
        5. Unified response
        """
        if features is None or not isinstance(features, list) or len(features) == 0:
            raise ValueError("Invalid or missing features input. Patient feature array is required.")

        # 1. Prediction (ensemble) - CACHED
        # Convert features to tuple for hashing
        features_tuple = tuple(features)
        
        # Top-3 predictions (cached)
        top_3 = []
        for d_type, predictor in self.predictors.items():
            if predictor is not None:
                try:
                    prob, _ = self._cached_predict(features_tuple, d_type)
                    top_3.append({"disease": d_type, "probability": float(prob)})
                except Exception as e:
                    pass
        
        # Sort and take top 3
        top_3 = sorted(top_3, key=lambda x: x["probability"], reverse=True)[:3]

        # Primary prediction (cached)
        probability, explanation = self._cached_predict(features_tuple, disease_type)
        predictor = self.predictors.get(disease_type, self.predictors.get("diabetes"))
        if predictor is None:
            raise RuntimeError("No prediction models available. Run trainer.py first.")

        model_metadata = self._build_model_metadata(disease_type, predictor, probability)
        
        # --- PHASE 1: Combined ML Probabilitic Risk ---
        if probability > 0.70:
            risk = "High"
        elif probability > 0.40:
            risk = "Moderate"
        else:
            risk = "Low"
            
        # --- PHASE 2: Clinical AI Guardrails (The Override) ---
        # AI/Clinical Intelligence has the final word on patient safety
        risk = self._apply_clinical_guardrails(disease_type, features, risk)

        # 2. NLP Pipeline
        nlp_result = self.nlp.process_prescription(prescription if prescription else "")

        # 3. Drug Validation
        drug_insights = self.drug_service.evaluate_prescription(
            nlp_result["drugs"], disease_type
        )
        
        # 4. Clinical Intelligence (New)
        raw_prescription_text = prescription if prescription else ""
        abnormalities = self.clinical_intel.evaluate_biomarkers(disease_type, features)
        prescription_eval = self.clinical_intel.evaluate_prescription(disease_type, risk, nlp_result["drugs"], raw_prescription_text)
        # 3. Clinical Intelligence Fusion (AI Narrative)
        recommendations = self.clinical_intel.generate_recommendations(disease_type, risk, abnormalities, features)

        # 5. Structured response
        result = {
            "disclaimer": "This is not a medical diagnosis system. Consult a healthcare professional for accurate medical advice.",
            "top_3_predictions": top_3,
            "risk": risk,
            "confidence": float(probability),
            "disease": disease_type,
            "explanation": explanation,
            "model_metadata": model_metadata,
            "abnormalities": abnormalities,
            "prescription_evaluation": prescription_eval,
            "recommendations": recommendations,
            "entities": {
                "drugs": nlp_result["drugs"],
                "symptoms": nlp_result["symptoms"],
                "ner_entities": nlp_result["entities"],
                "nlp_confidence": nlp_result["confidence"],
                "prescription_valid": nlp_result["is_valid"]
            },
            "matched_drugs": drug_insights["matched_drugs"],
            "suggestions": drug_insights["suggestions"],
            "drug_interactions": drug_insights["drug_interactions"],
            "drug_details": drug_insights["drug_details"],
            "nlp_status": nlp_result["context"]
        }

        # --- MongoDB Logging (Simplified) ---
        try:
            from utils.db import db_client
            
            # Simple direct logging to ensure stability
            log_entry = {
                "patient_id": patient_id or user_id or "anonymous",
                "patient_name": patient_name or "Anonymous Patient",
                "treating_doctor_id": treating_doctor_id or user_id or "system",
                "doctor_id": treating_doctor_id or user_id or "system",
                "disease": disease_type,
                "risk": risk,
                "confidence": float(probability),
                "timestamp": datetime.datetime.utcnow().isoformat(), # Fixed "Invalid Date" via ISO string
                "date": datetime.datetime.utcnow().strftime("%Y-%m-%d"),
                "glucose": features[1] if len(features) > 1 else 0,
                "blood_pressure": features[2] if len(features) > 2 else 0,
                "bmi": features[5] if len(features) > 5 else 0,
                "auto_medications": result.get('auto_medications') or result.get('matched_drugs') or [],
                "recommendations": recommendations,
                "prescription": prescription
            }
            
            if db_client.db is not None:
                db_client.db.medical_records.insert_one(log_entry)
                db_client.db.predictions.insert_one(log_entry.copy())
        except Exception as e:
            safe_print(f"[MongoDB] Simplified logging failed: {e}")

        return result

    def _apply_clinical_guardrails(self, disease_type, features, current_risk):
        """
        AI/Clinical Fusion Guardrail:
        Escalates risk status to ensure patient safety when biomarkers are catastrophic.
        """
        if not features or len(features) < 8:
            return current_risk

        escalated_risk = current_risk
        indices = ClinicalRegistry.get_indices(disease_type)

        if disease_type == "diabetes":
            # Diabetes specific catastrophic thresholds
            glucose = features[indices["glucose"]]
            bp = features[indices["blood_pressure"]]
            bmi = features[indices["bmi"]]
            
            if glucose >= 250 or bp >= 160 or bmi >= 45:
                escalated_risk = "High"
            elif (glucose >= 170 or bp >= 110 or bmi >= 35) and current_risk == "Low":
                escalated_risk = "Moderate"

        elif disease_type == "heart":
            # Cardiac catastrophic thresholds
            rbp = features[indices["blood_pressure"]]
            chol = features[indices["cholesterol"]]
            if rbp >= 170 or chol >= 300:
                escalated_risk = "High"
            elif (rbp >= 150 or chol >= 250) and current_risk == "Low":
                escalated_risk = "Moderate"

        elif disease_type == "mental":
            # Neurological catastrophic thresholds
            stress = features[indices["stress_level"]]
            if stress >= 9:
                escalated_risk = "High"

        return escalated_risk
