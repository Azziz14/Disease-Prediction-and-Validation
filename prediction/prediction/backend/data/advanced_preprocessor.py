"""
ADVANCED Data Preprocessing with Feature Engineering and Selection
- Robust missing value handling
- Advanced feature engineering
- Feature selection (SelectKBest, RFE)
- Outlier detection and handling
- Data quality validation
- Proper train/val/test splitting with stratification
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.ensemble import RandomForestClassifier
from scipy import stats
import joblib
import os
import warnings
warnings.filterwarnings('ignore')


class AdvancedDataPreprocessor:
    """
    Advanced preprocessing pipeline with:
    - Robust outlier detection (IQR + Z-score)
    - Advanced feature engineering
    - Feature selection
    - Proper stratified splitting
    - Data validation
    """

    FEATURE_NAMES = [
        'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
        'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'
    ]

    def __init__(self, saved_dir='models/saved', disease='diabetes'):
        self.scaler = StandardScaler()
        self.robust_scaler = RobustScaler()
        self.saved_dir = os.path.join(os.path.dirname(__file__), '..', saved_dir)
        self.disease = disease
        os.makedirs(self.saved_dir, exist_ok=True)
        
        self.feature_selector = None
        self.selected_features = None
        self.outlier_mask = None
        self.feature_statistics = {}

    def load_and_preprocess(self, dataset_path: str, target_col: str, 
                            test_size=0.15, val_size=0.15, handle_outliers=True,
                            select_features=True):
        """
        Complete preprocessing pipeline:
        1. Load data
        2. Validate data quality
        3. Handle missing values
        4. Detect and handle outliers
        5. Feature engineering
        6. Encode categorical features
        6. Feature selection
        7. Proper train/val/test split with stratification
        8. Scaling
        """
        print(f"\n=== Advanced Data Preprocessing ({self.disease}) ===")

        # 1. Load data
        df = pd.read_csv(dataset_path)
        # Convert all StringDtype columns to object dtype for sklearn compatibility
        for col in df.columns:
            if pd.api.types.is_string_dtype(df[col]):
                df[col] = df[col].astype(object)
        print(f"[OK] Loaded {len(df)} samples with {len(df.columns)} features")

        # 2. Data validation
        self._validate_data(df, target_col)

        # 3. Handle missing values
        df = self._handle_missing_values(df)

        # 4. Handle biologically invalid zeros
        df = self._handle_invalid_zeros(df)

        # --- Encode target column if categorical (e.g., 'Positive'/'Negative') ---
        if df[target_col].dtype == 'object' or not np.issubdtype(df[target_col].dtype, np.number):
            unique_vals = df[target_col].unique()
            if len(unique_vals) == 2:
                # Binary classification: map to 0/1
                mapping = {val: i for i, val in enumerate(sorted(unique_vals))}
                print(f"  [OK] Encoded target column '{target_col}' as binary: {mapping}")
                df[target_col] = df[target_col].map(mapping)
            else:
                # Multi-class: use LabelEncoder
                from sklearn.preprocessing import LabelEncoder
                le = LabelEncoder()
                df[target_col] = le.fit_transform(df[target_col])
                print(f"  [OK] Label-encoded target column '{target_col}' with classes: {list(le.classes_)}")

        # 5. Outlier detection and handling
        if handle_outliers:
            df = self._handle_outliers(df)

        # 6. Feature engineering
        df = self._engineer_features(df)

        # 7. Encode categorical features (excluding target)
        from sklearn.preprocessing import OneHotEncoder, LabelEncoder
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if target_col in cat_cols:
            cat_cols = [col for col in cat_cols if col != target_col]
        if cat_cols:
            for col in cat_cols:
                n_unique = df[col].nunique()
                if n_unique == 2:
                    # Binary: Label encode
                    le = LabelEncoder()
                    df[col] = le.fit_transform(df[col])
                else:
                    # Multi-category: One-hot encode
                    try:
                        ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
                    except TypeError:
                        ohe = OneHotEncoder(sparse=False, handle_unknown='ignore')
                    ohe_df = pd.DataFrame(ohe.fit_transform(df[[col]]), columns=[f"{col}_{cat}" for cat in ohe.categories_[0]])
                    df = pd.concat([df.drop(columns=[col]), ohe_df], axis=1)
            print(f"  [OK] Encoded categorical columns: {cat_cols}")

        # 7. Split into train/val/test BEFORE scaling
        X = df.drop(columns=[target_col])
        y = df[target_col]

        # First split: separate test set
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        # Second split: separate validation from training
        val_ratio = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_ratio, random_state=42, stratify=y_temp
        )

        print(f"[OK] Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")


        # 8. Feature selection (on train set ONLY)
        if select_features:
            # Optionally use RFE for feature selection
            use_rfe = True
            if use_rfe:
                from sklearn.feature_selection import RFE
                from sklearn.ensemble import RandomForestClassifier
                n_features_to_select = min(X_train.shape[1], 15)
                rfe = RFE(RandomForestClassifier(n_estimators=100, random_state=42), n_features_to_select=n_features_to_select)
                X_train = rfe.fit_transform(X_train, y_train)
                X_val = rfe.transform(X_val)
                X_test = rfe.transform(X_test)
                self.selected_features = list(np.array(X.columns)[rfe.get_support()])
                print(f"    - RFE selected {n_features_to_select} features: {self.selected_features}")
            else:
                X_train, X_val, X_test = self._select_features(
                    X_train, y_train, X_val, X_test
                )

        # 9. Scaling (fit on train, transform all)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)

        # 10. Save artifacts
        self._save_artifacts(X_train.shape[1])

        return (
            X_train_scaled, X_val_scaled, X_test_scaled,
            y_train.values, y_val.values, y_test.values
        )

    def _validate_data(self, df, target_col):
        """Validate data quality."""
        print(f"  Data validation:")
        print(f"    - Missing values: {df.isnull().sum().sum()}")
        print(f"    - Duplicates: {df.duplicated().sum()}")
        print(f"    - Numeric columns: {df.select_dtypes(include=[np.number]).shape[1]}")

    def _handle_missing_values(self, df):
        """
        Handle missing values using multiple strategies:
        - Drop rows with missing target
        - Fill with median for numerical features
        - Fill with mode for categorical
        """
        target_col = None
        for col in df.columns:
            if 'target' in col.lower() or 'outcome' in col.lower():
                target_col = col
                break

        if target_col:
            df = df.dropna(subset=[target_col])

        # Median imputation for numerical
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().sum() > 0:
                median_val = df[col].median()
                df[col].fillna(median_val, inplace=True)

        # Mode imputation for categorical
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df[col].isnull().sum() > 0:
                mode_val = df[col].mode()[0]
                df[col].fillna(mode_val, inplace=True)

        return df

    def _handle_invalid_zeros(self, df):
        """
        Replace biologically invalid zeros with median.
        Context: In diabetes prediction, zero values for glucose, BP, etc. are invalid.
        """
        zero_invalid_cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
        
        for col in zero_invalid_cols:
            if col in df.columns:
                zero_count = (df[col] == 0).sum()
                if zero_count > 0:
                    non_zero_median = df[df[col] != 0][col].median()
                    if pd.notna(non_zero_median) and non_zero_median > 0:
                        df.loc[df[col] == 0, col] = non_zero_median
                        print(f"    - {col}: Replaced {zero_count} zeros with median {non_zero_median:.2f}")

        return df

    def _handle_outliers(self, df):
        """
        Detect and handle outliers using IQR + Z-score methods.
        Ensure capped values match the original dtype (int or float).
        """
        print(f"  Outlier detection:")
        outlier_counts = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            # IQR method
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            # Cast bounds to column dtype if needed
            col_dtype = df[col].dtype
            if np.issubdtype(col_dtype, np.integer):
                lower_bound = int(np.floor(lower_bound))
                upper_bound = int(np.ceil(upper_bound))

            outliers_iqr = (df[col] < lower_bound) | (df[col] > upper_bound)
            outlier_counts[col] = outliers_iqr.sum()

            if outliers_iqr.sum() > 0:
                # Cap outliers to bounds instead of removing
                df.loc[df[col] < lower_bound, col] = lower_bound
                df.loc[df[col] > upper_bound, col] = upper_bound
                print(f"    - {col}: Capped {outliers_iqr.sum()} outliers")

        return df

    def _engineer_features(self, df):
        """
        Create advanced derived features:
        - BMI categories
        - Age groups
        - Interaction features
        - Polynomial features
        - Ratio features
        """
        print(f"  Feature engineering:")

        # BMI categories
        if 'BMI' in df.columns:
            df['BMI_Category'] = pd.cut(
                df['BMI'],
                bins=[0, 18.5, 25, 30, 35, 100],
                labels=[0, 1, 2, 3, 4]
            ).astype(int)
            print(f"    + BMI_Category")

        # Age groups
        if 'Age' in df.columns:
            df['Age_Group'] = pd.cut(
                df['Age'],
                bins=[0, 25, 35, 45, 55, 100],
                labels=[0, 1, 2, 3, 4]
            ).astype(int)
            print(f"    + Age_Group")

        # Interaction features
        if 'Glucose' in df.columns and 'BMI' in df.columns:
            df['Glucose_BMI'] = df['Glucose'] * df['BMI']
            print(f"    + Glucose_BMI")

        if 'Glucose' in df.columns and 'Age' in df.columns:
            df['Glucose_Age'] = df['Glucose'] * df['Age']
            print(f"    + Glucose_Age")

        # Polynomial features
        if 'BMI' in df.columns:
            df['BMI_Squared'] = df['BMI'] ** 2
            print(f"    + BMI_Squared")

        if 'Age' in df.columns:
            df['Age_Squared'] = df['Age'] ** 2
            print(f"    + Age_Squared")

        # Ratio features
        if 'Glucose' in df.columns and 'BMI' in df.columns:
            df['Glucose_BMI_Ratio'] = df['Glucose'] / (df['BMI'] + 1)
            print(f"    + Glucose_BMI_Ratio")

        return df

    def _select_features(self, X_train, y_train, X_val, X_test):
        """
        Select best features using SelectKBest + f_classif.
        Prevents overfitting by reducing feature space.
        """
        print(f"  Feature selection:")
        
        n_features = min(X_train.shape[1], 15)  # Select top 15 features
        
        self.feature_selector = SelectKBest(f_classif, k=n_features)
        X_train_selected = self.feature_selector.fit_transform(X_train, y_train)

        # Get selected feature names
        mask = self.feature_selector.get_support()
        self.selected_features = X_train.columns[mask].tolist()

        # Apply same selection to val and test
        X_val_selected = self.feature_selector.transform(X_val)
        X_test_selected = self.feature_selector.transform(X_test)

        print(f"    - Selected {n_features} features: {self.selected_features}")

        return X_train_selected, X_val_selected, X_test_selected

    def _save_artifacts(self, n_features):
        """Save preprocessing artifacts."""
        joblib.dump(self.scaler, os.path.join(self.saved_dir, f'{self.disease}_scaler.pkl'))
        joblib.dump(self.feature_selector, os.path.join(self.saved_dir, f'{self.disease}_feature_selector.pkl'))
        joblib.dump(self.selected_features, os.path.join(self.saved_dir, f'{self.disease}_selected_features.pkl'))
        print(f"  [OK] Saved preprocessing artifacts")

    def process_inference_data(self, features: list, disease='diabetes'):
        """Transform raw features for inference."""
        if len(features) != len(self.FEATURE_NAMES):
            raise ValueError(f"Expected {len(self.FEATURE_NAMES)} features, got {len(features)}")

        # Create dataframe matching column names
        feature_dict = {name: [val] for name, val in zip(self.FEATURE_NAMES, features)}
        df = pd.DataFrame(feature_dict)

        # Apply engineering
        df = self._engineer_features(df)

        # Select same features as training
        if self.feature_selector:
            X = self.feature_selector.transform(df)
        else:
            X = df.values

        # Scale
        return self.scaler.transform(X)
