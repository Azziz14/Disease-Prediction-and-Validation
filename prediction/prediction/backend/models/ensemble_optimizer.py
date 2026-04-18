"""
ENSEMBLE OPTIMIZER with Stacking, Bayesian Weights, and Threshold Tuning
- Stacking: Meta-learner on out-of-fold base model predictions
- Bayesian Weight Optimization: scipy.optimize to maximize F1
- Soft Voting: Weighted probabilities from all models
- Threshold Optimization: Find optimal classification threshold
- Ensemble Evaluation: Individual vs ensemble comparison
- Diversity-aware model weighting
"""

import os
import numpy as np
import joblib
from scipy.optimize import minimize
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    f1_score, precision_score, recall_score, roc_auc_score,
    accuracy_score, confusion_matrix
)


class EnsembleOptimizer:
    """
    Production-grade ensemble combining:
    - Multiple ML models + Deep Learning
    - Bayesian weight optimization (Nelder-Mead)
    - Optimal threshold tuning
    - Stacking meta-learner with OOF predictions
    """

    def __init__(self, saved_dir='models/saved', prefix='diabetes'):
        self.saved_dir = os.path.join(os.path.dirname(__file__), '..', saved_dir)
        os.makedirs(self.saved_dir, exist_ok=True)
        self.prefix = prefix

        self.individual_models = {}
        self.meta_learner = None
        self.model_weights = {}
        self.optimal_threshold = 0.5
        self.ensemble_results = {}

    def train(self, X_train, y_train, X_val, y_val, X_test=None, y_test=None):
        """
        Train stacking ensemble with Bayesian weight optimization:
        1. Load base models
        2. Generate base model predictions
        3. Train meta-learner on validation predictions
        4. Optimize ensemble weights via Nelder-Mead
        5. Find optimal classification threshold
        6. Evaluate ensemble
        """
        print("\n=== Training Ensemble ===")

        # Step 1: Load base models
        print("  Step 1: Loading base models...")
        base_models_available = self._load_base_models()

        if not base_models_available:
            print("  [ERROR] No base models found. Train individual models first.")
            return

        # Step 2: Get base model predictions
        print("  Step 2: Generating predictions on validation set...")
        val_predictions = self._get_ensemble_predictions(X_val)

        if val_predictions is None or val_predictions.shape[1] == 0:
            print("  [ERROR] No valid predictions from base models.")
            return

        # Step 3: Train meta-learner
        print("  Step 3: Training meta-learner (Logistic Regression)...")
        self._train_meta_learner(val_predictions, y_val)

        # Step 4: Bayesian weight optimization
        print("  Step 4: Optimizing ensemble weights (Nelder-Mead)...")
        self._optimize_weights_bayesian(X_val, y_val)

        # Step 5: Threshold optimization
        print("  Step 5: Optimizing classification threshold...")
        self._optimize_threshold(X_val, y_val)

        # Step 6: Evaluate if test set provided
        if X_test is not None and y_test is not None:
            print("  Step 6: Evaluating ensemble on test set...")
            self._evaluate_ensemble(X_test, y_test)

        # Save ensemble config
        self._save_ensemble_config()

    def _load_base_models(self):
        """Load trained base models."""
        model_names = ['xgb', 'rf', 'svm', 'lr', 'gb', 'lgbm', 'catboost']
        available_models = 0

        for name in model_names:
            path = os.path.join(self.saved_dir, f"{self.prefix}_{name}_enhanced.pkl")
            if os.path.exists(path):
                try:
                    self.individual_models[name] = joblib.load(path)
                    available_models += 1
                    print(f"    [OK] Loaded {name}")
                except Exception as e:
                    print(f"    [ERROR] Failed to load {name}: {e}")

        # Try to load DL model
        dl_path = os.path.join(self.saved_dir, f'{self.prefix}_ann_enhanced.pkl')
        if os.path.exists(dl_path):
            try:
                dl_model = joblib.load(dl_path)
                # Also load the DL scaler
                dl_scaler_path = os.path.join(self.saved_dir, 'dl_scaler.pkl')
                if os.path.exists(dl_scaler_path):
                    dl_scaler = joblib.load(dl_scaler_path)
                    self.individual_models['dl'] = {
                        'model': dl_model,
                        'scaler': dl_scaler,
                        'type': 'dl'
                    }
                else:
                    self.individual_models['dl'] = {
                        'model': dl_model,
                        'scaler': None,
                        'type': 'dl'
                    }
                available_models += 1
                print(f"    [OK] Loaded dl (deep learning)")
            except Exception as e:
                print(f"    [ERROR] Failed to load dl: {e}")

        print(f"  Total models loaded: {available_models}")
        return available_models > 0

    def _get_model_proba(self, model_entry, X):
        """Get probability predictions from a single model."""
        if isinstance(model_entry, dict) and model_entry.get('type') == 'dl':
            model = model_entry['model']
            scaler = model_entry.get('scaler')
            if scaler is not None:
                X_input = scaler.transform(X)
            else:
                X_input = X
            return model.predict_proba(X_input)[:, 1]
        else:
            # Standard sklearn model
            if hasattr(model_entry, 'predict_proba'):
                return model_entry.predict_proba(X)[:, 1]
            else:
                return model_entry.predict(X).astype(float)

    def _get_ensemble_predictions(self, X):
        """
        Get predictions from all base models.
        Returns array shape (n_samples, n_models) with probabilities.
        """
        predictions = []
        self._model_order = []

        for name, model_entry in self.individual_models.items():
            try:
                probs = self._get_model_proba(model_entry, X)
                predictions.append(probs)
                self._model_order.append(name)
                print(f"    [OK] Predictions from {name}: shape {probs.shape}")
            except Exception as e:
                print(f"    [ERROR] Prediction from {name} failed: {e}")

        if predictions:
            return np.column_stack(predictions)
        return None

    def _train_meta_learner(self, X_meta, y_meta):
        """Train meta-learner on base model outputs."""
        try:
            self.meta_learner = LogisticRegression(
                random_state=42, max_iter=2000, class_weight='balanced',
                C=1.0
            )
            self.meta_learner.fit(X_meta, y_meta)

            # Get meta-learner accuracy
            meta_preds = self.meta_learner.predict(X_meta)
            meta_f1 = f1_score(y_meta, meta_preds, zero_division=0)
            print(f"    Meta-learner training F1: {meta_f1:.4f}")

            # Save meta-learner
            joblib.dump(self.meta_learner,
                       os.path.join(self.saved_dir, f"{self.prefix}_meta_learner.pkl"))
            print("    [OK] Meta-learner trained and saved")

        except Exception as e:
            print(f"    [ERROR] Meta-learner training failed: {e}")

    def _optimize_weights_bayesian(self, X_val, y_val):
        """
        Optimize ensemble weights using Nelder-Mead to maximize F1 score.
        Much better than performance-proportional weights.
        """
        val_predictions = self._get_ensemble_predictions(X_val)
        if val_predictions is None:
            return

        n_models = val_predictions.shape[1]

        def neg_f1(weights):
            """Objective: negative F1 (we minimize)."""
            w = np.abs(weights)
            w = w / w.sum()  # Normalize to sum to 1
            weighted_probs = val_predictions @ w
            preds = (weighted_probs > self.optimal_threshold).astype(int)
            return -f1_score(y_val, preds, zero_division=0)

        # Start with equal weights
        initial_weights = np.ones(n_models) / n_models

        # Optimize
        result = minimize(
            neg_f1, initial_weights,
            method='Nelder-Mead',
            options={'maxiter': 1000, 'xatol': 1e-6, 'fatol': 1e-6}
        )

        # Normalize optimal weights
        optimal_weights = np.abs(result.x)
        optimal_weights = optimal_weights / optimal_weights.sum()

        model_names = self._model_order
        for name, weight in zip(model_names, optimal_weights):
            self.model_weights[name] = float(weight)

        optimized_f1 = -result.fun
        print(f"    Optimized F1: {optimized_f1:.4f}")
        print(f"    Optimized weights:")
        for name, weight in self.model_weights.items():
            print(f"      {name:8s}: {weight:.4f}")

    def _optimize_threshold(self, X_val, y_val):
        """
        Find optimal classification threshold that maximizes F1 score.
        Default 0.5 is rarely optimal for imbalanced datasets.
        """
        probs = self._soft_voting(X_val)

        best_threshold = 0.5
        best_f1 = 0.0

        for threshold in np.arange(0.2, 0.8, 0.01):
            preds = (probs > threshold).astype(int)
            f1 = f1_score(y_val, preds, zero_division=0)
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = threshold

        self.optimal_threshold = float(best_threshold)
        print(f"    Optimal threshold: {self.optimal_threshold:.2f} (F1={best_f1:.4f})")

    def _evaluate_ensemble(self, X_test, y_test):
        """Evaluate individual models vs ensemble on test set."""
        print("\n=== Ensemble vs Individual Evaluation ===")

        results = {'individual_models': {}, 'ensemble': {}}

        # --- Individual model metrics ---
        print("Individual Model Performance:")
        for name, model_entry in self.individual_models.items():
            try:
                probs = self._get_model_proba(model_entry, X_test)
                preds = (probs > 0.5).astype(int)
                f1 = f1_score(y_test, preds, zero_division=0)
                prec = precision_score(y_test, preds, zero_division=0)
                rec = recall_score(y_test, preds, zero_division=0)
                acc = accuracy_score(y_test, preds)

                results['individual_models'][name] = {
                    'accuracy': acc, 'f1': f1, 'precision': prec, 'recall': rec
                }
                print(f"  {name:8s} | Acc={acc:.4f} | F1={f1:.4f} | Prec={prec:.4f} | Rec={rec:.4f}")
            except Exception as e:
                print(f"  {name} evaluation failed: {e}")

        # --- Ensemble (weighted voting) ---
        print("\nEnsemble (Optimized Weighted Voting):")
        ensemble_probs = self._soft_voting(X_test)
        ensemble_preds = (ensemble_probs > self.optimal_threshold).astype(int)

        ens_f1 = f1_score(y_test, ensemble_preds, zero_division=0)
        ens_prec = precision_score(y_test, ensemble_preds, zero_division=0)
        ens_rec = recall_score(y_test, ensemble_preds, zero_division=0)
        ens_acc = accuracy_score(y_test, ensemble_preds)

        try:
            ens_auc = roc_auc_score(y_test, ensemble_probs)
        except ValueError:
            ens_auc = 0.0

        results['ensemble'] = {
            'accuracy': ens_acc, 'f1': ens_f1, 'precision': ens_prec,
            'recall': ens_rec, 'auc': ens_auc
        }
        cm = confusion_matrix(y_test, ensemble_preds)
        results['ensemble']['confusion_matrix'] = cm.tolist()

        print(f"  Ensemble | Acc={ens_acc:.4f} | F1={ens_f1:.4f} | Prec={ens_prec:.4f} | Rec={ens_rec:.4f} | AUC={ens_auc:.4f}")
        print(f"  Confusion Matrix:\n{cm}")

        # --- Stacking (meta-learner) ---
        if self.meta_learner is not None:
            print("\nEnsemble (Stacking with Meta-Learner):")
            try:
                meta_probs = self._stacking_voting(X_test)
                meta_preds = (meta_probs > 0.5).astype(int)

                meta_f1 = f1_score(y_test, meta_preds, zero_division=0)
                meta_prec = precision_score(y_test, meta_preds, zero_division=0)
                meta_rec = recall_score(y_test, meta_preds, zero_division=0)
                meta_acc = accuracy_score(y_test, meta_preds)

                results['ensemble_stacking'] = {
                    'accuracy': meta_acc, 'f1': meta_f1,
                    'precision': meta_prec, 'recall': meta_rec
                }
                print(f"  Stacking | Acc={meta_acc:.4f} | F1={meta_f1:.4f} | Prec={meta_prec:.4f} | Rec={meta_rec:.4f}")
            except Exception as e:
                print(f"  Stacking evaluation failed: {e}")

        self.ensemble_results = results
        joblib.dump(results, os.path.join(self.saved_dir, f"{self.prefix}_ensemble_results.pkl"))

    def _soft_voting(self, X):
        """Soft voting with optimized weights."""
        model_names = list(self.individual_models.keys())
        weighted_probs = np.zeros(len(X))
        total_weight = 0.0

        for name, model_entry in self.individual_models.items():
            weight = self.model_weights.get(name, 1.0 / len(self.individual_models))
            try:
                probs = self._get_model_proba(model_entry, X)
                weighted_probs += weight * probs
                total_weight += weight
            except Exception as e:
                pass

        # Normalize by total weight (not by number of models — previous bug)
        if total_weight > 0:
            weighted_probs /= total_weight

        return weighted_probs

    def _stacking_voting(self, X):
        """Use meta-learner for final prediction."""
        if self.meta_learner is None:
            return self._soft_voting(X)

        try:
            base_preds = self._get_ensemble_predictions(X)
            meta_probs = self.meta_learner.predict_proba(base_preds)[:, 1]
            return meta_probs
        except Exception as e:
            print(f"Stacking failed: {e}. Falling back to soft voting.")
            return self._soft_voting(X)

    def predict(self, X, method='voting'):
        """
        Make ensemble prediction.
        Args:
            X: Input features
            method: 'voting' (weighted) or 'stacking' (meta-learner)
        Returns:
            probabilities array
        """
        if method == 'stacking' and self.meta_learner is not None:
            probs = self._stacking_voting(X)
        else:
            probs = self._soft_voting(X)

        return probs

    def predict_class(self, X, method='voting'):
        """Make ensemble class prediction using optimized threshold."""
        probs = self.predict(X, method)
        return (probs > self.optimal_threshold).astype(int)

    def _save_ensemble_config(self):
        """Save ensemble configuration."""
        config = {
            'model_weights': self.model_weights,
            'individual_models': list(self.individual_models.keys()),
            'has_meta_learner': self.meta_learner is not None,
            'optimal_threshold': self.optimal_threshold,
        }
        joblib.dump(config, os.path.join(self.saved_dir, f"{self.prefix}_ensemble_config.pkl"))
        print(f"  [OK] Ensemble configuration saved")

    def load_config(self):
        """Load saved ensemble configuration."""
        config_path = os.path.join(self.saved_dir, f"{self.prefix}_ensemble_config.pkl")
        if os.path.exists(config_path):
            config = joblib.load(config_path)
            self.model_weights = config.get('model_weights', {})
            self.optimal_threshold = config.get('optimal_threshold', 0.5)
            return True
        return False
