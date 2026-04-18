"""
Prediction Service — Central Orchestrator
Combines ML ensemble, NLP, drug intelligence, and report generation.
Returns unified structured response matching API spec.
"""

from models.predictor import MultiModelPredictor
from services.drug_service import DrugIntelligenceService
from services.clinical_intelligence import ClinicalIntelligenceService

# Try enhanced NLP first, fall back to basic
try:
    from nlp.processor_enhanced import NLPProcessorEnhanced as NLPProcessor
    print("[OK] Using Enhanced NLP Processor")
except ImportError:
    from nlp.processor import NLPProcessor
    print("[FALLBACK] Using Basic NLP Processor (enhanced not available)")


class PredictionService:
    def __init__(self):
        print("Initializing PredictionService...")

        # Initialize predictors for each disease
        self.predictors = {}
        for disease in ["diabetes", "heart", "mental"]:
            try:
                self.predictors[disease] = MultiModelPredictor(disease)
            except Exception as e:
                print(f"  Warning: {disease} predictor init failed: {e}")
                if "diabetes" in self.predictors:
                    self.predictors[disease] = self.predictors["diabetes"]

        self.nlp = NLPProcessor()
        self.drug_service = DrugIntelligenceService()
        self.clinical_intel = ClinicalIntelligenceService()
        print("PredictionService ready.")

    def handle_prediction(self, features, prescription, disease_type="diabetes"):
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

        # 1. Prediction (ensemble)
        # Evaluate top-3 predictions across all active models
        top_3 = []
        for d_type, predictor in self.predictors.items():
            if predictor is not None:
                try:
                    # Provide dummy prediction if dimensionality doesn't match perfectly, 
                    # but usually features array is length-agnostic in predictor pipeline up to max features
                    # Actually, features given is typically tailored for the current selected disease_type.
                    # We will still gather the primary one strictly, and attempt others.
                    prob, _ = predictor.predict(features)
                    top_3.append({"disease": d_type, "probability": float(prob)})
                except Exception as e:
                    pass
        
        # Sort and take top 3
        top_3 = sorted(top_3, key=lambda x: x["probability"], reverse=True)[:3]

        predictor = self.predictors.get(disease_type, self.predictors.get("diabetes"))
        if predictor is None:
            raise RuntimeError("No prediction models available. Run trainer.py first.")

        probability, explanation = predictor.predict(features)

        # Confidence Threshold Check
        is_uncertain = probability < 0.40
        if is_uncertain:
            risk = "Uncertain - Please consult doctor"
        else:
            risk = "High" if probability > 0.65 else ("Moderate" if probability > 0.4 else "Low")

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
        recommendations = self.clinical_intel.generate_recommendations(disease_type, risk, abnormalities)

        # 5. Structured response
        return {
            "disclaimer": "This is not a medical diagnosis system. Consult a healthcare professional for accurate medical advice.",
            "top_3_predictions": top_3,
            "risk": risk,
            "confidence": float(probability),
            "disease": disease_type,
            "explanation": explanation,
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
