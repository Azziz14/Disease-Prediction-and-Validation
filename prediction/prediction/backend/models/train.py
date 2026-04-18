import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'trained_models')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'datasets')

os.makedirs(MODELS_DIR, exist_ok=True)

def train_and_select_best(dataset_path: str, disease_type: str, target_col: str):
    """
    Trains multiple models, evaluates their performance, and saves them.
    Automatically selects the best model.
    """
    if not os.path.exists(dataset_path):
        print(f"Dataset {dataset_path} not found. Skipping training for {disease_type}.")
        return

    print(f"--- Training models for {disease_type} ---")
    df = pd.read_csv(dataset_path)
    
    # Assume target column is labeled target_col and prep features
    if target_col not in df.columns:
        print(f"Target column '{target_col}' not found.")
        return
        
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    models = {
        'rf': RandomForestClassifier(n_estimators=100, random_state=42),
        'svm': SVC(probability=True, random_state=42),
        'xgb': XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42),
        'ann': MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
    }
    
    best_acc = 0.0
    best_model_name = ""
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        print(f"{name} Accuracy: {acc:.4f}")
        
        # Save model
        joblib.dump(model, os.path.join(MODELS_DIR, f"{disease_type}_{name}.pkl"))
        
        if acc > best_acc:
            best_acc = acc
            best_model_name = name
            
    print(f"-> Best Model for {disease_type}: {best_model_name.upper()} ({best_acc:.4f})")

def run_pipeline():
    # Attempt training on generic targets if datasets exist
    train_and_select_best(os.path.join(DATA_DIR, 'diabetes.csv'), 'diabetes', target_col='Outcome')
    # Can extend here for train_and_select_best(..., 'heart', 'target') etc.
    
if __name__ == "__main__":
    run_pipeline()
