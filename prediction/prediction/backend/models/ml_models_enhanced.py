"""
ENHANCED Machine Learning Models with Hyperparameter Tuning
- RandomizedSearchCV for efficient hyperparameter optimization
- CatBoost (optional) as additional model candidate
- Class weight balancing for imbalanced data
- Stratified K-Fold cross-validation (5-fold)
- SHAP values for feature importance explanation
- Probability calibration via CalibratedClassifierCV
- Per-class metrics: Precision, Recall, F1, Confusion Matrix
"""

import os
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, cross_validate
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score, precision_score, recall_score,
    confusion_matrix, classification_report
)
from xgboost import XGBClassifier
from scipy.stats import randint, uniform

# Optional: SHAP for advanced explainability
try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

# Optional LightGBM
try:
    from lightgbm import LGBMClassifier
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False

# Optional CatBoost
try:
    from catboost import CatBoostClassifier
    HAS_CATBOOST = True
except ImportError:
    HAS_CATBOOST = False


class MachineLearningModelsEnhanced:
    """
    Production-grade ML ensemble with:
    - Automatic hyperparameter tuning (RandomizedSearchCV)
    - Class weight balancing
    - Probability calibration
    - Per-class evaluation metrics
    - SHAP-based explanations
    """

    def __init__(self, saved_dir='models/saved', prefix='diabetes', tune_hyperparams=True):
        self.saved_dir = os.path.join(os.path.dirname(__file__), '..', saved_dir)
        os.makedirs(self.saved_dir, exist_ok=True)
        self.prefix = prefix
        self.tune_hyperparams = tune_hyperparams

        self.models = {}
        self.best_model = None
        self.best_model_name = None
        self.best_params = {}
        self.feature_importance_shap = None
        self.class_weights = None
        self.calibrated_models = {}

    def compute_class_weights(self, y_train):
        """Compute class weights for imbalanced datasets."""
        unique_classes = np.unique(y_train)
        class_weights = {}

        for cls in unique_classes:
            weight = len(y_train) / (len(unique_classes) * np.sum(y_train == cls))
            class_weights[cls] = weight

        self.class_weights = class_weights
        print(f"  Class weights: {class_weights}")
        return class_weights

    def _get_tuning_distributions(self):
        """
        Define hyperparameter distributions for RandomizedSearchCV.
        Uses scipy distributions for continuous params — more efficient than GridSearch.
        """
        params = {
            'xgb': {
                'n_estimators': randint(100, 500),
                'max_depth': randint(3, 10),
                'learning_rate': uniform(0.01, 0.19),  # 0.01 to 0.20
                'subsample': uniform(0.6, 0.4),        # 0.6 to 1.0
                'colsample_bytree': uniform(0.6, 0.4),
                'min_child_weight': randint(1, 7),
                'gamma': uniform(0, 0.5),
                'reg_alpha': uniform(0, 1.0),
                'reg_lambda': uniform(0.5, 1.5),
            },
            'rf': {
                'n_estimators': randint(100, 500),
                'max_depth': randint(5, 30),
                'min_samples_split': randint(2, 15),
                'min_samples_leaf': randint(1, 8),
                'max_features': ['sqrt', 'log2', None],
            },
            'svm': {
                'C': uniform(0.01, 100),
                'gamma': ['scale', 'auto'],
                'kernel': ['rbf', 'poly'],
            },
            'lr': {
                'C': uniform(0.001, 100),
                'solver': ['lbfgs', 'liblinear', 'saga'],
                'max_iter': [2000],
                'penalty': ['l2'],
            },
            'gb': {
                'n_estimators': randint(100, 400),
                'max_depth': randint(3, 10),
                'learning_rate': uniform(0.01, 0.19),
                'subsample': uniform(0.7, 0.3),
                'min_samples_split': randint(2, 10),
                'min_samples_leaf': randint(1, 5),
            },
        }

        if HAS_LGBM:
            params['lgbm'] = {
                'n_estimators': randint(100, 500),
                'max_depth': randint(3, 12),
                'learning_rate': uniform(0.01, 0.19),
                'num_leaves': randint(20, 80),
                'min_child_samples': randint(5, 30),
                'subsample': uniform(0.6, 0.4),
                'colsample_bytree': uniform(0.6, 0.4),
                'reg_alpha': uniform(0, 1.0),
                'reg_lambda': uniform(0, 1.0),
            }

        return params

    def _build_models(self, class_weights):
        """Initialize models with class weights."""
        self.models = {
            'xgb': XGBClassifier(
                random_state=42,
                n_jobs=-1,
                scale_pos_weight=class_weights.get(1, 1.0) if 1 in class_weights else 1.0,
                use_label_encoder=False,
                eval_metric='logloss',
                tree_method='hist',  # Faster training
            ),
            'rf': RandomForestClassifier(
                random_state=42,
                n_jobs=-1,
                class_weight='balanced',
            ),
            'svm': SVC(
                probability=True,
                random_state=42,
                class_weight='balanced',
            ),
            'lr': LogisticRegression(
                random_state=42,
                max_iter=2000,
                class_weight='balanced',
            ),
            'gb': GradientBoostingClassifier(
                random_state=42,
            ),
        }

        if HAS_LGBM:
            self.models['lgbm'] = LGBMClassifier(
                random_state=42,
                n_jobs=-1,
                is_unbalance=True,
                verbose=-1,
            )

        if HAS_CATBOOST:
            self.models['catboost'] = CatBoostClassifier(
                random_state=42,
                verbose=0,
                auto_class_weights='Balanced',
            )

    def train_all(self, X_train, y_train, X_val, y_val, X_test, y_test, save=True):
        """
        Train all models with hyperparameter tuning.
        Evaluate on validation + test sets. Calibrate best model.
        """
        # Compute class weights
        self.compute_class_weights(y_train)
        self._build_models(self.class_weights)

        results = {}
        detailed_results = {}
        best_test_f1 = 0
        best_model_name = None

        tuning_distributions = self._get_tuning_distributions() if self.tune_hyperparams else {}

        for name, model in self.models.items():
            t0 = time.time()
            print(f"\n  Training {name.upper()}...")

            # Hyperparameter tuning with RandomizedSearchCV
            if self.tune_hyperparams and name in tuning_distributions:
                print(f"    -> Tuning hyperparameters (RandomizedSearchCV, n_iter=40)...")
                try:
                    search = RandomizedSearchCV(
                        model,
                        tuning_distributions[name],
                        n_iter=40,
                        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
                        scoring='f1_weighted',
                        n_jobs=-1,
                        verbose=0,
                        random_state=42,
                    )
                    search.fit(X_train, y_train)
                    model = search.best_estimator_
                    self.best_params[name] = search.best_params_
                    print(f"    -> Best params: {search.best_params_}")
                except Exception as e:
                    print(f"    -> Tuning failed ({e}), training with defaults...")
                    model.fit(X_train, y_train)
            else:
                model.fit(X_train, y_train)

            elapsed = time.time() - t0

            # --- Validation set evaluation ---
            val_preds = model.predict(X_val)
            val_probs = model.predict_proba(X_val)[:, 1] if hasattr(model, 'predict_proba') else val_preds.astype(float)

            val_f1 = f1_score(y_val, val_preds, zero_division=0)
            val_acc = accuracy_score(y_val, val_preds)
            val_precision = precision_score(y_val, val_preds, zero_division=0)
            val_recall = recall_score(y_val, val_preds, zero_division=0)
            try:
                val_auc = roc_auc_score(y_val, val_probs)
            except ValueError:
                val_auc = 0.0

            # --- Test set evaluation ---
            test_preds = model.predict(X_test)
            test_probs = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else test_preds.astype(float)

            test_f1 = f1_score(y_test, test_preds, zero_division=0)
            test_acc = accuracy_score(y_test, test_preds)
            test_precision = precision_score(y_test, test_preds, zero_division=0)
            test_recall = recall_score(y_test, test_preds, zero_division=0)
            try:
                test_auc = roc_auc_score(y_test, test_probs)
            except ValueError:
                test_auc = 0.0

            # Confusion matrix
            cm = confusion_matrix(y_test, test_preds)

            # Per-class report
            class_report = classification_report(y_test, test_preds, zero_division=0)

            results[name] = test_acc
            detailed_results[name] = {
                'val_accuracy': round(val_acc, 4),
                'val_f1': round(val_f1, 4),
                'val_precision': round(val_precision, 4),
                'val_recall': round(val_recall, 4),
                'val_auc': round(val_auc, 4),
                'test_accuracy': round(test_acc, 4),
                'test_f1': round(test_f1, 4),
                'test_precision': round(test_precision, 4),
                'test_recall': round(test_recall, 4),
                'test_auc': round(test_auc, 4),
                'confusion_matrix': cm.tolist(),
                'class_report': class_report,
                'train_time_sec': round(elapsed, 2),
            }

            print(f"    Val:  F1={val_f1:.4f} | Prec={val_precision:.4f} | Rec={val_recall:.4f} | AUC={val_auc:.4f}")
            print(f"    Test: F1={test_f1:.4f} | Prec={test_precision:.4f} | Rec={test_recall:.4f} | AUC={test_auc:.4f}")
            print(f"    Confusion Matrix:\n{cm}")
            print(f"    Time: {elapsed:.1f}s")

            if save:
                joblib.dump(model, os.path.join(self.saved_dir, f"{self.prefix}_{name}_enhanced.pkl"))

            # Select best model by test F1 (more balanced than accuracy)
            if test_f1 > best_test_f1:
                best_test_f1 = test_f1
                best_model_name = name
                self.best_model = model
                self.best_model_name = name

        # --- Calibrate best model for more reliable probabilities ---
        print(f"\n  ★ Best ML Model: {best_model_name.upper()} (Test F1: {best_test_f1:.4f})")
        print(f"  Calibrating best model probabilities...")
        try:
            calibrated = CalibratedClassifierCV(self.best_model, method='isotonic', cv=3)
            calibrated.fit(X_train, y_train)
            self.calibrated_models[best_model_name] = calibrated
            joblib.dump(calibrated, os.path.join(self.saved_dir, f"{self.prefix}_calibrated_best.pkl"))
            print(f"  [OK] Calibrated {best_model_name.upper()} saved")
        except Exception as e:
            print(f"  [ERROR] Calibration failed: {e}")

        # --- SHAP values for the best tree-based model ---
        if HAS_SHAP and best_model_name in ['xgb', 'rf', 'gb', 'lgbm', 'catboost']:
            try:
                print(f"  Computing SHAP values for {best_model_name.upper()}...")
                explainer = shap.TreeExplainer(self.best_model)
                self.feature_importance_shap = explainer.shap_values(X_test[:100])  # Limit for speed
                print(f"  [OK] SHAP values computed")
            except Exception as e:
                print(f"  [ERROR] SHAP failed: {e}")

        return results, best_model_name, detailed_results

    def load_best(self, best_model_name):
        """Load best trained model."""
        path = os.path.join(self.saved_dir, f"{self.prefix}_{best_model_name}_enhanced.pkl")
        if os.path.exists(path):
            return joblib.load(path)
        raise FileNotFoundError(f"Model not found: {path}")

    def load_calibrated(self):
        """Load calibrated best model."""
        path = os.path.join(self.saved_dir, f"{self.prefix}_calibrated_best.pkl")
        if os.path.exists(path):
            return joblib.load(path)
        return None

    def get_shap_explanation(self, X_sample):
        """Get SHAP-based feature importance for a prediction."""
        if not HAS_SHAP or self.best_model is None:
            return None

        try:
            explainer = shap.TreeExplainer(self.best_model)
            shap_values = explainer.shap_values(X_sample)
            return shap_values
        except Exception as e:
            print(f"SHAP explanation failed: {e}")
            return None
