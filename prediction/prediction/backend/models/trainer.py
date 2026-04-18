"""
PRODUCTION Training Pipeline v3.0
Wires all enhanced modules into a single unified pipeline:
- AdvancedDataPreprocessor (or DataPipeline) for preprocessing
- MachineLearningModelsEnhanced with RandomizedSearchCV
- DeepLearningModelEnhanced with calibration
- EnsembleOptimizer with Bayesian weight optimization
- EvaluationMetrics for comprehensive reporting
- ExplainabilityEngine for SHAP/LIME
"""

import os
import sys
import json
import time
import numpy as np

# Add parent dir to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from preprocessing.pipeline import DataPipeline
from models.ml_models_enhanced import MachineLearningModelsEnhanced
from models.dl_models_enhanced import DeepLearningModelEnhanced
from models.ensemble_optimizer import EnsembleOptimizer
from models.evaluation_metrics import EvaluationMetrics
from sklearn.metrics import accuracy_score, f1_score, classification_report


def train_disease(disease_name, dataset_path, target_col, tune_hyperparams=True):
    """Train all models for a specific disease dataset using enhanced pipeline."""
    if not os.path.exists(dataset_path):
        print(f"  [WARNING] Dataset not found: {dataset_path}")
        return None

    t0 = time.time()

    print(f"\n{'='*60}")
    print(f"  TRAINING PIPELINE: {disease_name.upper()}")
    print(f"  Dataset: {dataset_path}")
    print(f"  Hyperparameter Tuning: {'ON' if tune_hyperparams else 'OFF'}")
    print(f"{'='*60}")

    # ═══════════════════════════════════════════════
    # 1. PREPROCESSING (with train/val/test split)
    # ═══════════════════════════════════════════════
    print("\n── Step 1: Data Preprocessing ──")
    pipeline = DataPipeline()

    result = pipeline.load_and_preprocess(dataset_path, target_col=target_col)

    # New pipeline returns 7 values (train, val, test splits + scaler)
    X_train, X_val, X_test, y_train, y_val, y_test, scaler = result

    print(f"  Class distribution (train): {dict(zip(*np.unique(y_train, return_counts=True)))}")
    print(f"  Class distribution (test):  {dict(zip(*np.unique(y_test, return_counts=True)))}")

    # ═══════════════════════════════════════════════
    # 2. ENHANCED ML MODELS
    # ═══════════════════════════════════════════════
    print("\n── Step 2: Enhanced ML Models ──")
    ml = MachineLearningModelsEnhanced(
        prefix=disease_name,
        tune_hyperparams=tune_hyperparams
    )

    ml_results, best_ml_name, ml_detailed = ml.train_all(
        X_train, y_train, X_val, y_val, X_test, y_test, save=True
    )

    # ═══════════════════════════════════════════════
    # 3. ENHANCED DEEP LEARNING (ANN)
    # ═══════════════════════════════════════════════
    print("\n── Step 3: Enhanced Deep Learning (ANN) ──")
    dl = DeepLearningModelEnhanced(model_name=f'{disease_name}_ann_enhanced.pkl')
    dl.train(X_train, y_train, X_val=X_val, y_val=y_val)

    # Evaluate ANN on test set
    ann_metrics = dl.evaluate(X_test, y_test)
    ann_acc = ann_metrics.get('accuracy', 0.0)
    ann_f1 = ann_metrics.get('f1', 0.0)
    print(f"  ANN Test: Acc={ann_acc:.4f} | F1={ann_f1:.4f}")
    print(f"  ANN Test Confusion Matrix:\n{np.array(ann_metrics.get('confusion_matrix', []))}")

    # ═══════════════════════════════════════════════
    # 4. ENSEMBLE OPTIMIZATION
    # ═══════════════════════════════════════════════
    print("\n── Step 4: Ensemble Optimization ──")
    ensemble = EnsembleOptimizer(prefix=disease_name)
    ensemble.train(X_train, y_train, X_val, y_val, X_test, y_test)

    # ═══════════════════════════════════════════════
    # 5. COMPREHENSIVE EVALUATION
    # ═══════════════════════════════════════════════
    print("\n── Step 5: Comprehensive Evaluation ──")
    evaluator = EvaluationMetrics()

    # Evaluate best ML model
    best_ml_model = ml.best_model
    if best_ml_model is not None:
        evaluator.evaluate_model(
            best_ml_model, X_test, y_test,
            X_train=X_train, y_train=y_train,
            model_name=f"ML_{best_ml_name.upper()}"
        )

    # Compare all evaluated models
    evaluator.compare_models()
    evaluator.save_evaluation_report(f'{disease_name}_evaluation')

    # ═══════════════════════════════════════════════
    # 6. SAVE ENHANCED MANIFEST
    # ═══════════════════════════════════════════════
    elapsed = time.time() - t0

    manifest = {
        "disease": disease_name,
        "version": "3.0_enhanced",
        "best_ml_model": best_ml_name,
        "ml_accuracies": ml_results,
        "ml_detailed": ml_detailed,
        "ml_best_params": ml.best_params.get(best_ml_name, {}),
        "ann_accuracy": round(ann_acc, 4),
        "ann_f1": round(ann_f1, 4),
        "ann_metrics": ann_metrics,
        "ensemble_weights": ensemble.model_weights,
        "ensemble_threshold": ensemble.optimal_threshold,
        "ensemble_results": ensemble.ensemble_results,
        "features_expected": X_train.shape[1],
        "training_samples": X_train.shape[0],
        "validation_samples": X_val.shape[0] if X_val is not None else 0,
        "test_samples": X_test.shape[0],
        "training_time_sec": round(elapsed, 1),
        "pipeline": {
            "preprocessing": "DataPipeline (RobustScaler, Winsorization, feature engineering)",
            "ml_models": "MachineLearningModelsEnhanced (RandomizedSearchCV, CalibratedClassifierCV)",
            "dl_model": "DeepLearningModelEnhanced (256-128-64-32, calibrated)",
            "ensemble": "EnsembleOptimizer (Bayesian weights, meta-learner, threshold optimization)",
            "evaluation": "EvaluationMetrics (5-fold CV, SHAP, per-class metrics)",
        },
        "ensemble_strategy": "bayesian_weighted_voting_with_stacking"
    }

    manifest_path = os.path.join(
        os.path.dirname(__file__), '..', 'models', 'saved',
        f'{disease_name}_manifest.json'
    )
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2, default=str)

    print(f"\n  [OK] Manifest saved: {manifest_path}")
    print(f"  [OK] Total training time: {elapsed:.1f}s")
    return manifest


def main():
    base_dir = os.path.join(os.path.dirname(__file__), '..')

    datasets = {
        "diabetes": {
            "path": os.path.join(base_dir, 'datasets', 'diabetes.csv'),
            "target": "Outcome"
        },
        # Add more datasets as available:
        # "heart": {"path": ..., "target": "target"},
        # "mental": {"path": ..., "target": "outcome"},
    }

    print("╔══════════════════════════════════════════════════╗")
    print("║  AI Healthcare Training Pipeline v3.0 ENHANCED  ║")
    print("║  ─ RandomizedSearchCV + Bayesian Ensemble       ║")
    print("║  ─ Probability Calibration + SHAP               ║")
    print("║  ─ Train/Val/Test Split + Threshold Tuning      ║")
    print("╚══════════════════════════════════════════════════╝")

    all_results = {}
    for name, config in datasets.items():
        result = train_disease(name, config["path"], config["target"])
        if result:
            all_results[name] = result

    # ═══════════════════════════════════════════════
    # FINAL SUMMARY
    # ═══════════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  TRAINING SUMMARY")
    print(f"{'='*60}")
    for name, res in all_results.items():
        best = res['best_ml_model']
        best_acc = res['ml_accuracies'].get(best, 0)
        best_f1 = res['ml_detailed'].get(best, {}).get('test_f1', 0)
        ann_f1 = res.get('ann_f1', 0)
        n_features = res['features_expected']
        train_time = res.get('training_time_sec', 0)

        print(f"\n  {name.upper()}:")
        print(f"    Best ML:  {best.upper()} | Acc={best_acc:.4f} | F1={best_f1:.4f}")
        print(f"    ANN:      Acc={res['ann_accuracy']:.4f} | F1={ann_f1:.4f}")
        print(f"    Ensemble: Weights={res.get('ensemble_weights', {})}")
        print(f"    Features: {n_features} | Time: {train_time:.1f}s")

        if res.get('ensemble_results', {}).get('ensemble'):
            ens = res['ensemble_results']['ensemble']
            print(f"    Ensemble: F1={ens.get('f1', 0):.4f} | AUC={ens.get('auc', 0):.4f}")

    print(f"\n  [OK] All pipelines complete. Start server with: python app.py")


if __name__ == "__main__":
    main()
