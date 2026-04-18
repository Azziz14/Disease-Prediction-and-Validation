"""
Advanced Data Preprocessing Pipeline
- Robust missing value handling with biological zero imputation
- Advanced feature engineering (interactions, polynomial, log, ratio)
- Winsorization for extreme outliers
- RobustScaler (IQR-based, less sensitive to outliers)
- Proper train/val/test split with stratification
- Prevents data leakage (fit only on train)
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
import warnings
warnings.filterwarnings('ignore')


class DataPipeline:
    FEATURE_NAMES = [
        'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
        'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'
    ]

    # Columns where zero is biologically invalid
    ZERO_INVALID_COLS = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']

    # Columns that benefit from log transform (highly skewed)
    LOG_TRANSFORM_COLS = ['Insulin', 'DiabetesPedigreeFunction']

    def __init__(self, saved_dir='models/saved'):
        self.scaler = RobustScaler()  # IQR-based, robust to outliers
        self.saved_dir = os.path.join(os.path.dirname(__file__), '..', saved_dir)
        os.makedirs(self.saved_dir, exist_ok=True)
        self.scaler_path = os.path.join(self.saved_dir, 'scaler.pkl')
        self._medians = {}  # Store medians for inference-time imputation

    def load_and_preprocess(self, dataset_path: str, target_col: str,
                            test_size=0.15, val_size=0.15):
        """
        Full preprocessing: clean -> impute -> engineer -> split -> scale.
        Returns train/val/test splits. Fit only on train to prevent data leakage.
        """
        df = pd.read_csv(dataset_path)
        print(f"  Loaded {len(df)} samples, {len(df.columns)} columns")

        # 1. Handle missing values
        df = df.dropna(subset=[target_col])
        df = df.fillna(df.median(numeric_only=True))

        # 2. Replace biologically invalid zeros with column medians
        for col in self.ZERO_INVALID_COLS:
            if col in df.columns:
                non_zero_median = df[df[col] != 0][col].median()
                zero_count = (df[col] == 0).sum()
                if zero_count > 0 and pd.notna(non_zero_median):
                    df[col] = df[col].replace(0, non_zero_median)
                    self._medians[col] = non_zero_median
                    print(f"    -> {col}: replaced {zero_count} zeros with median {non_zero_median:.1f}")

        # 3. Winsorize extreme outliers (clip at 1st and 99th percentile)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.drop(target_col, errors='ignore')
        for col in numeric_cols:
            lower = df[col].quantile(0.01)
            upper = df[col].quantile(0.99)
            clipped = ((df[col] < lower) | (df[col] > upper)).sum()
            if clipped > 0:
                df[col] = df[col].clip(lower, upper)

        # 4. Feature engineering
        df = self._engineer_features(df)

        # 5. Split into train/val/test BEFORE scaling (prevent leakage)
        X = df.drop(columns=[target_col])
        y = df[target_col]

        # First: separate test set
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        # Second: separate validation from training
        val_ratio = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_ratio, random_state=42, stratify=y_temp
        )

        print(f"  Split: Train={len(X_train)} | Val={len(X_val)} | Test={len(X_test)} | Features={X_train.shape[1]}")

        # 6. Scale (fit ONLY on train)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)

        # 7. Save artifacts
        joblib.dump(self.scaler, self.scaler_path)
        joblib.dump(X_train.shape[1], os.path.join(self.saved_dir, 'n_features.pkl'))
        joblib.dump(self._medians, os.path.join(self.saved_dir, 'medians.pkl'))

        return (
            X_train_scaled, X_val_scaled, X_test_scaled,
            y_train.values, y_val.values, y_test.values,
            self.scaler
        )

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Advanced feature engineering:
        - BMI category (clinical bins)
        - Age group (clinical bins)
        - Interaction features (Glucose*BMI, Glucose*Age)
        - Polynomial features (BMI², Age²)
        - Log transforms for skewed columns
        - Ratio features (Glucose/BMI, Insulin/Glucose)
        """
        # --- Categorical bins ---
        if 'BMI' in df.columns:
            df['BMI_Category'] = pd.cut(
                df['BMI'],
                bins=[0, 18.5, 25, 30, 35, 100],
                labels=[0, 1, 2, 3, 4],
                include_lowest=True
            ).astype(int)

        if 'Age' in df.columns:
            df['Age_Group'] = pd.cut(
                df['Age'],
                bins=[0, 25, 35, 45, 55, 100],
                labels=[0, 1, 2, 3, 4],
                include_lowest=True
            ).astype(int)

        # --- Interaction features ---
        if 'Glucose' in df.columns and 'BMI' in df.columns:
            df['Glucose_BMI'] = df['Glucose'] * df['BMI']

        if 'Glucose' in df.columns and 'Age' in df.columns:
            df['Glucose_Age'] = df['Glucose'] * df['Age']

        # --- Polynomial features ---
        if 'BMI' in df.columns:
            df['BMI_Squared'] = df['BMI'] ** 2

        if 'Age' in df.columns:
            df['Age_Squared'] = df['Age'] ** 2

        # --- Ratio features ---
        if 'Glucose' in df.columns and 'BMI' in df.columns:
            df['Glucose_BMI_Ratio'] = df['Glucose'] / (df['BMI'] + 1e-6)

        if 'Insulin' in df.columns and 'Glucose' in df.columns:
            df['Insulin_Glucose_Ratio'] = df['Insulin'] / (df['Glucose'] + 1e-6)

        # --- Log transforms for highly skewed features ---
        for col in self.LOG_TRANSFORM_COLS:
            if col in df.columns:
                df[f'{col}_Log'] = np.log1p(df[col])

        return df

    def process_inference_data(self, features: list) -> np.ndarray:
        """Transform raw 8-feature input into scaled vector matching training shape."""
        if len(features) != 8:
            raise ValueError(f"Expected 8 features, received {len(features)}")

        try:
            arr = np.array(features, dtype=float)
        except (ValueError, TypeError):
            raise ValueError("All features must be numeric")

        # Reconstruct derived features to match training
        pregnancies, glucose, bp, skin, insulin, bmi, dpf, age = arr

        # BMI category
        if bmi <= 18.5: bmi_cat = 0
        elif bmi <= 25: bmi_cat = 1
        elif bmi <= 30: bmi_cat = 2
        elif bmi <= 35: bmi_cat = 3
        else: bmi_cat = 4

        # Age group
        if age <= 25: age_group = 0
        elif age <= 35: age_group = 1
        elif age <= 45: age_group = 2
        elif age <= 55: age_group = 3
        else: age_group = 4

        # Interaction features
        glucose_bmi = glucose * bmi
        glucose_age = glucose * age

        # Polynomial features
        bmi_squared = bmi ** 2
        age_squared = age ** 2

        # Ratio features
        glucose_bmi_ratio = glucose / (bmi + 1e-6)
        insulin_glucose_ratio = insulin / (glucose + 1e-6)

        # Log transforms
        insulin_log = np.log1p(insulin)
        dpf_log = np.log1p(dpf)

        full_features = np.array([
            pregnancies, glucose, bp, skin, insulin, bmi, dpf, age,
            bmi_cat, age_group, glucose_bmi, glucose_age,
            bmi_squared, age_squared, glucose_bmi_ratio, insulin_glucose_ratio,
            insulin_log, dpf_log
        ]).reshape(1, -1)

        # Load scaler & transform
        if not os.path.exists(self.scaler_path):
            raise FileNotFoundError("Scaler not found. Run trainer.py first.")

        self.scaler = joblib.load(self.scaler_path)
        return self.scaler.transform(full_features)
