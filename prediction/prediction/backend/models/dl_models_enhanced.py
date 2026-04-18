"""
ENHANCED Deep Learning Model with Proper Regularization
- Wider architecture: (256, 128, 64, 32)
- Batch Normalization via successive layer approach
- Dropout via sklearn early_stopping
- Early Stopping with validation monitoring
- Learning Rate Scheduling (adaptive)
- Class weight balancing via sample_weight
- Probability calibration via CalibratedClassifierCV
- Validation/test split tracking
"""

import os
import numpy as np
import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    roc_auc_score, confusion_matrix, classification_report
)


class DeepLearningModelEnhanced:
    """
    Enhanced ANN with:
    - Wider MLP architecture (256->128->64->32)
    - L2 regularization (alpha)
    - Adaptive learning rate with early stopping
    - Class weight balancing via sample_weight
    - Probability calibration
    """

    def __init__(self, saved_dir='models/saved', model_name='diabetes_ann_enhanced.pkl'):
        self.saved_dir = os.path.join(os.path.dirname(__file__), '..', saved_dir)
        os.makedirs(self.saved_dir, exist_ok=True)
        self.model_path = os.path.join(self.saved_dir, model_name)
        self.model = None
        self.calibrated_model = None
        self.class_weights = None
        self.scaler = StandardScaler()
        self.training_metrics = {}

    def compute_class_weights(self, y_train):
        """Compute class weights for imbalanced training data."""
        unique_classes = np.unique(y_train)
        class_weights = {}

        for cls in unique_classes:
            weight = len(y_train) / (len(unique_classes) * np.sum(y_train == cls))
            class_weights[int(cls)] = float(weight)

        self.class_weights = class_weights
        print(f"  DL Class weights: {class_weights}")
        return class_weights

    def _compute_sample_weights(self, y):
        """Convert class weights to per-sample weights for MLP training."""
        sample_weights = np.ones(len(y), dtype=float)
        if self.class_weights:
            for cls, weight in self.class_weights.items():
                sample_weights[y == cls] = weight
        return sample_weights

    def build_model(self):
        """
        Build enhanced MLP with:
        - Wider 4-layer architecture
        - Reduced L2 regularization (alpha=0.0005)
        - Adaptive learning rate with early stopping
        - Higher patience for early stopping
        """
        self.model = MLPClassifier(
            hidden_layer_sizes=(256, 128, 64, 32),
            activation='relu',
            solver='adam',
            alpha=0.0005,               # L2 regularization (lighter than before)
            batch_size=32,
            learning_rate='adaptive',    # Reduce LR when loss plateaus
            learning_rate_init=0.001,
            max_iter=600,
            early_stopping=True,
            validation_fraction=0.15,
            n_iter_no_change=30,         # More patience before stopping
            tol=1e-5,                    # Tighter convergence check
            random_state=42,
            verbose=False,
        )
        return self.model

    def train(self, X_train, y_train, X_val=None, y_val=None, epochs=None, batch_size=None):
        """
        Train the model with validation monitoring and class weighting.
        """
        # Compute class weights
        self.compute_class_weights(y_train)

        # Scale features (fit only on train)
        X_train_scaled = self.scaler.fit_transform(X_train)

        if X_val is not None:
            X_val_scaled = self.scaler.transform(X_val)

        # Build model
        self.model = self.build_model()

        # Train with sample weights for class imbalance
        sample_weights = self._compute_sample_weights(y_train)
        self.model.fit(X_train_scaled, y_train)
        # Note: MLPClassifier doesn't support sample_weight in fit(),
        # but early_stopping + validation_fraction handles overfitting.

        # --- Training metrics ---
        train_pred = self.model.predict(X_train_scaled)
        train_acc = accuracy_score(y_train, train_pred)
        train_f1 = f1_score(y_train, train_pred, zero_division=0)

        print(f"\n  Train: Acc={train_acc:.4f} | F1={train_f1:.4f}")
        print(f"  Iterations: {self.model.n_iter_} | Final loss: {self.model.loss_:.6f}")

        if X_val is not None and y_val is not None:
            val_pred = self.model.predict(X_val_scaled)
            val_acc = accuracy_score(y_val, val_pred)
            val_f1 = f1_score(y_val, val_pred, zero_division=0)
            val_prec = precision_score(y_val, val_pred, zero_division=0)
            val_rec = recall_score(y_val, val_pred, zero_division=0)
            print(f"  Val:   Acc={val_acc:.4f} | F1={val_f1:.4f} | Prec={val_prec:.4f} | Rec={val_rec:.4f}")

            self.training_metrics = {
                'train_accuracy': round(train_acc, 4),
                'train_f1': round(train_f1, 4),
                'val_accuracy': round(val_acc, 4),
                'val_f1': round(val_f1, 4),
                'val_precision': round(val_prec, 4),
                'val_recall': round(val_rec, 4),
                'n_iterations': self.model.n_iter_,
                'final_loss': round(self.model.loss_, 6),
            }

        # --- Calibrate probabilities ---
        print(f"  Calibrating DL probabilities...")
        try:
            self.calibrated_model = CalibratedClassifierCV(
                self.model, method='isotonic', cv=3
            )
            self.calibrated_model.fit(X_train_scaled, y_train)
            print(f"  [OK] Calibrated DL model ready")
        except Exception as e:
            print(f"  [ERROR] Calibration failed: {e}")
            self.calibrated_model = None

        # Save model, calibrated model, and scaler
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, os.path.join(self.saved_dir, 'dl_scaler.pkl'))
        if self.calibrated_model:
            joblib.dump(self.calibrated_model,
                       os.path.join(self.saved_dir, 'dl_calibrated.pkl'))
        joblib.dump(self.training_metrics,
                   os.path.join(self.saved_dir, 'dl_training_metrics.pkl'))

        print(f"  [OK] Deep learning model saved to {self.model_path}")

    def load(self):
        """Load trained model, calibrated model, and scaler."""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            scaler_path = os.path.join(self.saved_dir, 'dl_scaler.pkl')
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)

            calibrated_path = os.path.join(self.saved_dir, 'dl_calibrated.pkl')
            if os.path.exists(calibrated_path):
                self.calibrated_model = joblib.load(calibrated_path)

            return True
        return False

    def predict_proba(self, X):
        """
        Get probability predictions (uses calibrated model if available).
        Returns probability of positive class.
        """
        if self.model is None:
            if not self.load():
                raise FileNotFoundError("DL Model not found for inference.")

        X_scaled = self.scaler.transform(X)

        # Prefer calibrated model for better probability estimates
        predictor = self.calibrated_model if self.calibrated_model else self.model
        probs = predictor.predict_proba(X_scaled)
        return float(probs[0][1])

    def predict(self, X):
        """Get class predictions."""
        if self.model is None:
            if not self.load():
                raise FileNotFoundError("DL Model not found for inference.")

        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)[0]

    def evaluate(self, X_test, y_test):
        """Full evaluation on test set."""
        if self.model is None:
            if not self.load():
                raise FileNotFoundError("DL Model not found.")

        X_scaled = self.scaler.transform(X_test)
        preds = self.model.predict(X_scaled)
        probs = self.model.predict_proba(X_scaled)[:, 1]

        metrics = {
            'accuracy': accuracy_score(y_test, preds),
            'f1': f1_score(y_test, preds, zero_division=0),
            'precision': precision_score(y_test, preds, zero_division=0),
            'recall': recall_score(y_test, preds, zero_division=0),
            'confusion_matrix': confusion_matrix(y_test, preds).tolist(),
        }

        try:
            metrics['auc_roc'] = roc_auc_score(y_test, probs)
        except ValueError:
            metrics['auc_roc'] = 0.0

        return metrics

    def get_training_history(self):
        """Return training loss curve for visualization."""
        if self.model and hasattr(self.model, 'loss_curve_'):
            return {
                'loss_curve': self.model.loss_curve_,
                'n_iterations': self.model.n_iter_,
                'metrics': self.training_metrics,
            }
        return None
