"""
Machine Learning Models
XGBoost (primary), Random Forest, SVM, Logistic Regression, LightGBM (optional).
Uses cross-validation for robust accuracy estimation.
"""

import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import cross_val_score
from xgboost import XGBClassifier

# Optional LightGBM
try:
    from lightgbm import LGBMClassifier
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False
    print("LightGBM not installed. Skipping.")


class MachineLearningModels:
    def __init__(self, saved_dir='models/saved', prefix='diabetes'):
        self.saved_dir = os.path.join(os.path.dirname(__file__), '..', saved_dir)
        os.makedirs(self.saved_dir, exist_ok=True)
        self.prefix = prefix

        self.models = {
            'xgb': XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                use_label_encoder=False,
                eval_metric='logloss',
                random_state=42
            ),
            'rf': RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            'svm': SVC(
                probability=True,
                kernel='rbf',
                C=1.0,
                gamma='scale',
                random_state=42
            ),
            'lr': LogisticRegression(
                random_state=42,
                max_iter=1000,
                C=1.0,
                solver='lbfgs'
            )
        }

        if HAS_LGBM:
            self.models['lgbm'] = LGBMClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                verbose=-1
            )

    def train_all(self, X_train, y_train, X_test, y_test, save=True):
        """Train all models, evaluate with cross-validation, select best."""
        results = {}
        detailed_results = {}
        best_acc = 0
        best_model_name = None

        for name, model in self.models.items():
            print(f"  Training {name}...")
            model.fit(X_train, y_train)

            # Test set evaluation
            preds = model.predict(X_test)
            probs = model.predict_proba(X_test)[:, 1]

            acc = accuracy_score(y_test, preds)
            f1 = f1_score(y_test, preds, zero_division=0)
            try:
                auc = roc_auc_score(y_test, probs)
            except ValueError:
                auc = 0.0

            # Cross-validation (3-fold for speed)
            cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring='accuracy')

            results[name] = acc
            detailed_results[name] = {
                'accuracy': round(acc, 4),
                'f1_score': round(f1, 4),
                'auc_roc': round(auc, 4),
                'cv_mean': round(cv_scores.mean(), 4),
                'cv_std': round(cv_scores.std(), 4)
            }

            print(f"  {name}: acc={acc:.4f} f1={f1:.4f} auc={auc:.4f} cv={cv_scores.mean():.4f}±{cv_scores.std():.4f}")

            if save:
                joblib.dump(model, os.path.join(self.saved_dir, f"{self.prefix}_{name}.pkl"))

            if acc > best_acc:
                best_acc = acc
                best_model_name = name

        print(f"  ★ Best ML Model: {best_model_name} ({best_acc:.4f})")
        return results, best_model_name, detailed_results

    def load_best(self, best_model_name):
        """Load a specific saved model."""
        path = os.path.join(self.saved_dir, f"{self.prefix}_{best_model_name}.pkl")
        if os.path.exists(path):
            return joblib.load(path)
        raise FileNotFoundError(f"Model not found: {path}")

    def load_model(self, model_name):
        """Load any saved model by key."""
        path = os.path.join(self.saved_dir, f"{self.prefix}_{model_name}.pkl")
        if os.path.exists(path):
            return joblib.load(path)
        return None
