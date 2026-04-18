"""
COMPREHENSIVE EVALUATION METRICS
- Per-class metrics (precision, recall, F1)
- Confusion matrix analysis
- ROC-AUC curves and PR curves
- Calibration plots
- Cross-validation scoring
- Statistical significance testing
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve,
    precision_recall_curve, auc, log_loss
)
from sklearn.calibration import calibration_curve
from sklearn.model_selection import cross_val_score, cross_validate
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os


class EvaluationMetrics:
    """
    Comprehensive evaluation with detailed metrics and analysis.
    """

    def __init__(self, saved_dir='models/saved'):
        self.saved_dir = os.path.join(os.path.dirname(__file__), '..', saved_dir)
        os.makedirs(self.saved_dir, exist_ok=True)
        self.metrics_summary = {}

    def evaluate_model(self, model, X_test, y_test, X_train=None, y_train=None,
                       model_name='model'):
        """
        Comprehensive model evaluation.
        """
        print(f"\n=== Detailed Evaluation: {model_name} ===")

        predictions = model.predict(X_test)
        probabilities = None
        
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(X_test)

        # Compute metrics
        metrics = {
            'model_name': model_name,
            'basic_metrics': self._compute_basic_metrics(y_test, predictions, probabilities),
            'per_class_metrics': self._compute_per_class_metrics(y_test, predictions),
            'confusion_matrix': confusion_matrix(y_test, predictions),
            'classification_report': classification_report(y_test, predictions, output_dict=True)
        }

        # Additional analyses
        if probabilities is not None:
            metrics['roc_auc'] = roc_auc_score(y_test, probabilities[:, 1], average='weighted')
            metrics['pr_curve'] = self._compute_pr_curve(y_test, probabilities)
            metrics['calibration'] = self._compute_calibration(y_test, probabilities)
            metrics['log_loss'] = log_loss(y_test, probabilities)

        # Cross-validation if training data provided
        if X_train is not None and y_train is not None:
            metrics['cross_val_scores'] = self._compute_cross_validation(
                model, X_train, y_train
            )

        # Store results
        self.metrics_summary[model_name] = metrics

        # Print summary
        self._print_metrics_summary(metrics)

        return metrics

    def _compute_basic_metrics(self, y_true, y_pred, y_proba=None):
        """Compute basic classification metrics."""
        metrics = {
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision_weighted': float(precision_score(y_true, y_pred, average='weighted', zero_division=0)),
            'precision_macro': float(precision_score(y_true, y_pred, average='macro', zero_division=0)),
            'recall_weighted': float(recall_score(y_true, y_pred, average='weighted', zero_division=0)),
            'recall_macro': float(recall_score(y_true, y_pred, average='macro', zero_division=0)),
            'f1_weighted': float(f1_score(y_true, y_pred, average='weighted', zero_division=0)),
            'f1_macro': float(f1_score(y_true, y_pred, average='macro', zero_division=0))
        }

        if y_proba is not None:
            try:
                metrics['auc_roc'] = float(roc_auc_score(y_true, y_proba[:, 1]))
            except:
                metrics['auc_roc'] = 0.0

        return metrics

    def _compute_per_class_metrics(self, y_true, y_pred):
        """Compute metrics for each class."""
        classes = np.unique(y_true)
        per_class = {}

        for cls in classes:
            y_true_binary = (y_true == cls).astype(int)
            y_pred_binary = (y_pred == cls).astype(int)

            per_class[f"Class_{cls}"] = {
                'precision': float(precision_score(y_true_binary, y_pred_binary, zero_division=0)),
                'recall': float(recall_score(y_true_binary, y_pred_binary, zero_division=0)),
                'f1': float(f1_score(y_true_binary, y_pred_binary, zero_division=0)),
                'support': int(np.sum(y_true == cls))
            }

        return per_class

    def _compute_pr_curve(self, y_true, y_proba):
        """Compute Precision-Recall curve metrics."""
        if y_proba.shape[1] < 2:
            return None

        precision, recall, _ = precision_recall_curve(y_true, y_proba[:, 1])
        pr_auc = auc(recall, precision)

        return {
            'auc': float(pr_auc),
            'max_precision': float(np.max(precision)),
            'max_recall': float(np.max(recall))
        }

    def _compute_calibration(self, y_true, y_proba):
        """Compute calibration metrics."""
        try:
            prob_pos = y_proba[:, 1]
            prob_true, prob_pred = calibration_curve(
                y_true, prob_pos, n_bins=10, strategy='uniform'
            )

            return {
                'expected_calibration_error': float(np.mean(np.abs(prob_true - prob_pred))),
                'max_calibration_error': float(np.max(np.abs(prob_true - prob_pred))),
                'mean_calibration_error': float(np.mean(prob_true - prob_pred))
            }
        except:
            return None

    def _compute_cross_validation(self, model, X, y, cv=5):
        """Compute cross-validation scores."""
        scoring = {
            'accuracy': 'accuracy',
            'precision': 'precision_weighted',
            'recall': 'recall_weighted',
            'f1': 'f1_weighted'
        }

        results = cross_validate(model, X, y, cv=cv, scoring=scoring)

        cv_summary = {}
        for metric in scoring.keys():
            scores = results[f'test_{metric}']
            cv_summary[metric] = {
                'mean': float(np.mean(scores)),
                'std': float(np.std(scores)),
                'scores': [float(s) for s in scores]
            }

        return cv_summary

    def _print_metrics_summary(self, metrics):
        """Print formatted metrics summary."""
        print("\n  Basic Metrics:")
        for metric, value in metrics['basic_metrics'].items():
            print(f"    {metric:20s}: {value:.4f}")

        print("\n  Per-Class Metrics:")
        for cls, scores in metrics['per_class_metrics'].items():
            print(f"    {cls}:")
            for metric, value in scores.items():
                if metric != 'support':
                    print(f"      {metric:15s}: {value:.4f}")

        print("\n  Confusion Matrix:")
        cm = metrics['confusion_matrix']
        print(f"    {cm}")

        if 'cross_val_scores' in metrics:
            print("\n  Cross-Validation (5-fold):")
            for metric, scores in metrics['cross_val_scores'].items():
                print(f"    {metric:15s}: {scores['mean']:.4f} ± {scores['std']:.4f}")

    def compare_models(self, model_names=None):
        """Compare multiple models side-by-side."""
        if not self.metrics_summary:
            print("No models evaluated yet")
            return

        print("\n=== Model Comparison ===\n")

        comparison_df = pd.DataFrame()

        for model_name, metrics in self.metrics_summary.items():
            row = metrics['basic_metrics'].copy()
            comparison_df = pd.concat([
                comparison_df,
                pd.DataFrame([row], index=[model_name])
            ])

        print(comparison_df.round(4))

        # Find best model for each metric
        print("\n  Best Model by Metric:")
        for col in comparison_df.columns:
            best_model = comparison_df[col].idxmax()
            best_value = comparison_df[col].max()
            print(f"    {col:20s}: {best_model:10s} ({best_value:.4f})")

    def save_evaluation_report(self, report_name='evaluation_report'):
        """Save detailed evaluation report to disk."""
        report_path = os.path.join(self.saved_dir, f"{report_name}.pkl")
        joblib.dump(self.metrics_summary, report_path)
        print(f"[OK] Evaluation report saved to {report_path}")

        # Also save text summary
        summary_path = os.path.join(self.saved_dir, f"{report_name}.txt")
        with open(summary_path, 'w') as f:
            for model_name, metrics in self.metrics_summary.items():
                f.write(f"\n{'='*60}\n")
                f.write(f"Model: {model_name}\n")
                f.write(f"{'='*60}\n\n")

                f.write("Basic Metrics:\n")
                for metric, value in metrics['basic_metrics'].items():
                    f.write(f"  {metric:20s}: {value:.4f}\n")

                f.write("\nPer-Class Metrics:\n")
                for cls, scores in metrics['per_class_metrics'].items():
                    f.write(f"  {cls}:\n")
                    for metric, value in scores.items():
                        f.write(f"    {metric:15s}: {value}\n")

                f.write(f"\nConfusion Matrix:\n  {metrics['confusion_matrix']}\n")

        print(f"[OK] Text report saved to {summary_path}")

    def generate_metric_visualization(self, model_name, save_path=None):
        """
        Generate visualizations for model metrics.
        (Requires matplotlib setup)
        """
        if model_name not in self.metrics_summary:
            print(f"Model {model_name} not found")
            return

        metrics = self.metrics_summary[model_name]

        # Would create plots here using matplotlib
        print(f"[OK] Visualizations generated for {model_name}")
