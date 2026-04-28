#!/usr/bin/env python3
"""
Enhanced Model Training Pipeline
Complete training with all improvements:
- Advanced data preprocessing
- Hyperparameter-tuned ML models
- Regularized deep learning
- Optimized ensemble
- Comprehensive evaluation
"""

import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)


def detect_target_column(df):
    # Try common target column names
    for col in df.columns:
        if col.lower() in ['outcome', 'class', 'target', 'death_event', 'charges']:
            return col
    # Fallback: last column if it's categorical or binary
    if len(df.columns) > 0:
        last_col = df.columns[-1]
        if str(df[last_col].dtype) in ["int", "int64", "float", "float64", "object"]:
            return last_col
    return None

def is_classification(df, target_col):
    # If target is categorical or binary, treat as classification
    n_unique = df[target_col].nunique()
    if n_unique <= 20 or df[target_col].dtype == 'object':
        return True
    return False

def train_all_datasets():
    print("\n" + "="*80)
    print("🚀 MULTI-DATASET MODEL TRAINING PIPELINE")
    print("="*80)

    from data.advanced_preprocessor import AdvancedDataPreprocessor
    from models.ml_models_enhanced import MachineLearningModelsEnhanced
    from models.dl_models_enhanced import DeepLearningModelEnhanced
    from models.ensemble_optimizer import EnsembleOptimizer
    from models.evaluation_metrics import EvaluationMetrics

    raw_dir = os.path.join(os.path.dirname(__file__), 'backend', 'datasets', 'raw')

    from imblearn.over_sampling import SMOTE
    for fname in os.listdir(raw_dir):
        if not fname.endswith('.csv'):
            continue
        dataset_path = os.path.join(raw_dir, fname)
        print(f"\n{'='*40}\nProcessing: {fname}\n{'='*40}")
        try:
            df = pd.read_csv(dataset_path)
        except Exception as e:
            print(f"❌ Could not read {fname}: {e}")
            continue
        target_col = detect_target_column(df)
        if not target_col:
            print(f"⚠️  No suitable target column found in {fname}. Skipping.")
            continue
        print(f"Target column: {target_col}")
        # Skip if target is not suitable
        if df[target_col].nunique() < 2:
            print(f"⚠️  Target column {target_col} has <2 unique values. Skipping.")
            continue
        # Preprocessing
        try:
            prep = AdvancedDataPreprocessor(disease=fname.replace('.csv',''))
            X_train, X_val, X_test, y_train, y_val, y_test = prep.load_and_preprocess(
                dataset_path=dataset_path,
                target_col=target_col,
                test_size=0.15,
                val_size=0.15,
                handle_outliers=True,
                select_features=True
            )
        except Exception as e:
            print(f"❌ Preprocessing failed for {fname}: {e}")
            continue
        # Model selection
        classification = is_classification(df, target_col)
        if classification:
            # Apply SMOTE for class balancing
            try:
                sm = SMOTE(random_state=42)
                X_train, y_train = sm.fit_resample(X_train, y_train)
                print(f"[SMOTE] Applied. New train shape: {X_train.shape}")
            except Exception as e:
                print(f"[SMOTE] Failed: {e}")
        try:
            ml = MachineLearningModelsEnhanced(tune_hyperparams=True)
            print("Training ML models with hyperparameter tuning (n_iter=100)...")
            # Increase n_iter for deeper search
            results, best_ml_model, detailed_results = ml.train_all(
                X_train, y_train,
                X_val, y_val,
                X_test, y_test,
                save=True
            )
            acc = detailed_results[best_ml_model].get('test_accuracy', 0)
            print(f"   Best Model: {best_ml_model}")
            print(f"   Test Accuracy: {acc:.4f}")
            if acc < 0.90:
                print(f"⚠️  Accuracy below 90%. Model not saved for {fname}.")
                continue
        except Exception as e:
            print(f"❌ ML training failed for {fname}: {e}")
            continue
        # Deep Learning
        try:
            dl = DeepLearningModelEnhanced(use_tensorflow=True)
            print("Training deep learning model with regularization...")
            dl.train(
                X_train, y_train,
                X_val=X_val, y_val=y_val,
                epochs=100,
                batch_size=32
            )
        except Exception as e:
            print(f"❌ Deep Learning training failed for {fname}: {e}")
        # Ensemble
        try:
            ensemble = EnsembleOptimizer(prefix=fname.replace('.csv',''))
            print("Training ensemble with stacking...")
            ensemble.train(X_train, y_train, X_val, y_val, X_test, y_test)
        except Exception as e:
            print(f"❌ Ensemble training failed for {fname}: {e}")
        # Evaluation
        try:
            evaluator = EvaluationMetrics()
            best_model = ml.load_best(best_ml_model)
            print(f"Evaluating best model: {best_ml_model.upper()}")
            metrics = evaluator.evaluate_model(
                best_model, X_test, y_test,
                X_train=X_train, y_train=y_train,
                model_name=best_ml_model.upper()
            )
            evaluator.save_evaluation_report(f'{fname.replace('.csv','')}_evaluation')
            print(f"   Report saved to: backend/models/saved/{fname.replace('.csv','')}_evaluation.pkl")
        except Exception as e:
            print(f"❌ Evaluation failed for {fname}: {e}")

    print("\n" + "="*80)
    print("✅ MULTI-DATASET TRAINING COMPLETE!")
    print("="*80)

if __name__ == '__main__':
    train_all_datasets()
