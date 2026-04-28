"""
Model Info Service
Exposes model accuracy scores, training metadata, and trust metrics.
"""

import os
import json


class ModelInfoService:
    def __init__(self):
        self.manifest_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'saved')

    def get_model_info(self, disease: str = "diabetes") -> dict:
        """Return model performance data for the trust dashboard."""
        manifest_path = os.path.join(self.manifest_dir, f'{disease}_manifest.json')

        if not os.path.exists(manifest_path):
            return {
                "available": False,
                "message": f"No trained models found for {disease}.",
                "models": [],
                "best_model": None
            }

        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        accuracies = manifest.get("ml_accuracies", {})
        best = manifest.get("best_ml_model", "unknown")
        features_expected = manifest.get("features_expected", 8)
        ensemble_strategy = manifest.get("ensemble_strategy", "Unavailable")

        model_names = {
            "rf": "Random Forest",
            "xgb": "XGBoost",
            "svm": "Support Vector Machine",
            "lr": "Logistic Regression"
        }

        models = []
        for key, acc in accuracies.items():
            models.append({
                "id": key,
                "name": model_names.get(key, key.upper()),
                "accuracy": round(acc * 100, 2),
                "is_best": key == best
            })

        # Sort by accuracy descending
        models.sort(key=lambda m: m["accuracy"], reverse=True)

        return {
            "available": True,
            "disease_context": disease,
            "models": models,
            "best_model": model_names.get(best, best),
            "features_expected": features_expected,
            "ensemble_strategy": ensemble_strategy,
            "disclaimer": (
                "Model accuracy is measured on held-out test data and may not reflect "
                "real-world clinical performance. These metrics are provided for transparency "
                "and should be interpreted by qualified professionals."
            )
        }
