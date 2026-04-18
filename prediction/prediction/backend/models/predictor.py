"""
Multi-Model Predictor with Ensemble + Explainability
- Uses enhanced ML models and calibrated ANN
- Ensemble optimizer for weighted predictions
- SHAP/LIME explainability integration
- Clinical threshold analysis
"""

import os
import json
import numpy as np
import joblib
from preprocessing.pipeline import DataPipeline
from models.ml_models_enhanced import MachineLearningModelsEnhanced
from models.dl_models_enhanced import DeepLearningModelEnhanced
from models.ensemble_optimizer import EnsembleOptimizer
from models.explainability import ExplainabilityEngine


class MultiModelPredictor:
    FEATURE_NAMES = [
        'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
        'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age',
        'BMI_Category', 'Age_Group', 'Glucose_BMI', 'Glucose_Age',
        'BMI_Squared', 'Age_Squared', 'Glucose_BMI_Ratio', 'Insulin_Glucose_Ratio',
        'Insulin_Log', 'DiabetesPedigreeFunction_Log'
    ]

    FEATURE_THRESHOLDS = {
        'Glucose': {'high': 140, 'low': 70, 'unit': 'mg/dL'},
        'BloodPressure': {'high': 120, 'low': 60, 'unit': 'mmHg'},
        'BMI': {'high': 30, 'low': 18.5, 'unit': 'kg/m²'},
        'Age': {'high': 45, 'low': 0, 'unit': 'years'},
        'Insulin': {'high': 166, 'low': 16, 'unit': 'μU/mL'},
        'SkinThickness': {'high': 50, 'low': 10, 'unit': 'mm'},
    }

    def __init__(self, prefix='diabetes'):
        self.prefix = prefix
        self.pipeline = DataPipeline()

        # Enhanced model handlers
        self.ml_handler = MachineLearningModelsEnhanced(prefix=prefix)
        self.dl_handler = DeepLearningModelEnhanced(model_name=f'{prefix}_ann_enhanced.pkl')

        # Ensemble optimizer
        self.ensemble = EnsembleOptimizer(prefix=prefix)

        # Explainability
        self.explainer = None

        self.best_ml_model = None
        self.best_ml_name = None
        self.xgb_model = None
        self.calibrated_model = None
        self.manifest = {}
        self.use_ensemble = False

        self.load_models()

    def load_models(self):
        """Load all enhanced models and ensemble configuration."""
        saved_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'saved')

        # Load manifest
        manifest_path = os.path.join(saved_dir, f'{self.prefix}_manifest.json')
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                self.manifest = json.load(f)
                self.best_ml_name = self.manifest.get('best_ml_model', 'xgb')

            # Load best ML model (enhanced)
            try:
                self.best_ml_model = self.ml_handler.load_best(self.best_ml_name)
                print(f"  [OK] Loaded best ML model: {self.best_ml_name}")
            except FileNotFoundError:
                # Try non-enhanced path as fallback
                try:
                    from models.ml_models import MachineLearningModels
                    fallback = MachineLearningModels(prefix=self.prefix)
                    self.best_ml_model = fallback.load_best(self.best_ml_name)
                    print(f"  [OK] Loaded fallback ML model: {self.best_ml_name}")
                except Exception:
                    print(f"  [WARNING] Best model '{self.best_ml_name}' not found.")

            # Load calibrated model
            self.calibrated_model = self.ml_handler.load_calibrated()
            if self.calibrated_model:
                print(f"  [OK] Loaded calibrated ML model")

            # Load XGBoost for feature importance
            try:
                xgb_path = os.path.join(saved_dir, f'{self.prefix}_xgb_enhanced.pkl')
                if os.path.exists(xgb_path):
                    self.xgb_model = joblib.load(xgb_path)
                else:
                    self.xgb_model = self.best_ml_model
            except Exception:
                self.xgb_model = self.best_ml_model

            # Load ensemble configuration
            if self.ensemble.load_config():
                self.ensemble._load_base_models()
                self.use_ensemble = len(self.ensemble.individual_models) > 1
                if self.use_ensemble:
                    print(f"  [OK] Ensemble loaded with {len(self.ensemble.individual_models)} models")

            # Initialize explainability engine
            importance_model = self.xgb_model or self.best_ml_model
            if importance_model is not None:
                model_type = 'xgb' if self.xgb_model else self.best_ml_name
                self.explainer = ExplainabilityEngine(
                    model=importance_model,
                    model_type=model_type,
                    feature_names=self.FEATURE_NAMES
                )
        else:
            print(f"  [WARNING] Manifest not found for {self.prefix}. Using fallback.")

    def predict(self, raw_features):
        """
        Prediction pipeline:
        1. If ensemble available -> use Bayesian-optimized weighted voting
        2. Else -> weighted ML (60%) + ANN (40%)
        Returns (probability, explanation_dict).
        """
        X_scaled = self.pipeline.process_inference_data(raw_features)

        # --- Method 1: Ensemble prediction (preferred) ---
        if self.use_ensemble:
            try:
                ensemble_probs = self.ensemble.predict(X_scaled, method='voting')
                final_prob = float(ensemble_probs[0]) if hasattr(ensemble_probs, '__len__') else float(ensemble_probs)

                # Temperature scaling
                temperature = 1.5
                scaled_p = (final_prob ** (1.0 / temperature)) / ((final_prob ** (1.0 / temperature)) + ((1.0 - final_prob) ** (1.0 / temperature)))
                final_prob = float(scaled_p)

                explanation = self._generate_explanation(X_scaled, raw_features, final_prob)
                explanation['prediction_method'] = 'ensemble_bayesian_weighted'
                explanation['ensemble_weights'] = self.ensemble.model_weights
                explanation['threshold'] = self.ensemble.optimal_threshold

                return float(final_prob), explanation
            except Exception as e:
                print(f"Ensemble prediction failed: {e}. Falling back to individual models.")

        # --- Method 2: Individual model fallback ---
        # ML prediction (use calibrated if available)
        ml_prob = 0.0
        ml_model = self.calibrated_model or self.best_ml_model
        if ml_model is not None:
            try:
                ml_prob = float(ml_model.predict_proba(X_scaled)[0][1])
            except Exception as e:
                print(f"ML inference failed: {e}")

        # ANN prediction
        dl_prob = 0.0
        try:
            dl_prob = float(self.dl_handler.predict_proba(X_scaled))
        except Exception as e:
            print(f"ANN inference failed: {e}")

        # Weighted combination
        if ml_prob > 0 and dl_prob > 0:
            final_prob = (ml_prob * 0.6) + (dl_prob * 0.4)
        elif ml_prob > 0:
            final_prob = ml_prob
        elif dl_prob > 0:
            final_prob = dl_prob
        else:
            final_prob = 0.5
            
        # Apply Temperature Scaling (Calibration)
        # Temperature > 1 softens probabilities, pushing them closer to 0.5 if they are uncertain
        temperature = 1.5
        # Softmax over binary classes (p, 1-p) with temperature
        scaled_p = (final_prob ** (1.0 / temperature)) / ((final_prob ** (1.0 / temperature)) + ((1.0 - final_prob) ** (1.0 / temperature)))
        final_prob = float(scaled_p)

        explanation = self._generate_explanation(X_scaled, raw_features, final_prob)
        explanation['prediction_method'] = 'individual_weighted'
        explanation['ml_prob'] = round(ml_prob, 4)
        explanation['dl_prob'] = round(dl_prob, 4)

        return float(final_prob), explanation

    def _generate_explanation(self, X_scaled, raw_features, probability):
        """
        Combine model-driven feature importance with clinical threshold analysis.
        Uses SHAP if available, else model feature_importances_.
        """
        reasons = {}

        # 1. SHAP-based explanation (if available)
        if self.explainer is not None:
            try:
                shap_result = self.explainer.get_shap_explanation(X_scaled)
                if shap_result and 'contributions' in shap_result:
                    top_features = list(shap_result['contributions'].items())[:5]
                    for fname, contribution in top_features:
                        direction = "increases" if contribution > 0 else "decreases"
                        reasons[f"{fname} (SHAP)"] = f"SHAP contribution: {contribution:.4f} ({direction} risk)"
            except Exception:
                pass

        # 2. Model-driven feature importance (from XGBoost or RF)
        importance_model = self.xgb_model or self.best_ml_model
        if importance_model is not None and hasattr(importance_model, 'feature_importances_'):
            importances = importance_model.feature_importances_
            n_features = min(len(importances), len(self.FEATURE_NAMES))

            top_indices = np.argsort(importances)[::-1][:5]
            for idx in top_indices:
                if idx < n_features and importances[idx] > 0.03:
                    fname = self.FEATURE_NAMES[idx]
                    imp_pct = round(importances[idx] * 100, 1)
                    if f"{fname} (SHAP)" not in reasons:
                        reasons[f"{fname} (Impact: {imp_pct}%)"] = self._describe_feature(
                            fname, raw_features, imp_pct
                        )

        # 3. Clinical threshold analysis
        glucose = raw_features[1]
        bmi = raw_features[5]
        bp = raw_features[2]
        age = raw_features[7]
        insulin = raw_features[4]

        if glucose > 140:
            reasons["Glucose"] = f"Elevated at {glucose} mg/dL — strong diabetic indicator"
        elif glucose > 100:
            reasons["Glucose"] = f"Pre-diabetic range at {glucose} mg/dL"

        if bmi > 30:
            reasons["BMI"] = f"Obese classification at {bmi} kg/m² — significant metabolic risk"
        elif bmi > 25:
            reasons["BMI"] = f"Overweight at {bmi} kg/m² — moderate risk factor"

        if bp > 140:
            reasons["Blood Pressure"] = f"Hypertensive at {bp} mmHg — cardiovascular concern"
        elif bp > 120:
            reasons["Blood Pressure"] = f"Elevated at {bp} mmHg"

        if age > 45:
            reasons["Age"] = f"Age {int(age)} — elevated baseline risk for metabolic conditions"

        if insulin > 166:
            reasons["Insulin"] = f"Elevated at {insulin} μU/mL — possible insulin resistance"

        if not reasons:
            reasons["Assessment"] = "All features within generally normal clinical bounds."

        return reasons

    def _describe_feature(self, fname, raw_features, imp_pct):
        """Describe a feature's impact using thresholds."""
        idx_map = {
            'Pregnancies': 0, 'Glucose': 1, 'BloodPressure': 2,
            'SkinThickness': 3, 'Insulin': 4, 'BMI': 5,
            'DiabetesPedigreeFunction': 6, 'Age': 7
        }
        idx = idx_map.get(fname, -1)
        if idx >= 0 and idx < len(raw_features):
            val = raw_features[idx]
            thresh = self.FEATURE_THRESHOLDS.get(fname, {})
            unit = thresh.get('unit', '')
            high = thresh.get('high', 999)
            status = "elevated" if val > high else "within range"
            return f"Value: {val} {unit} ({status}), model weight: {imp_pct}%"
        return f"Model importance: {imp_pct}%"
