import os
import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score

class DeepLearningModel:
    def __init__(self, saved_dir='models/saved', model_name='diabetes_ann.pkl'):
        # Fallback to sklearn MLPClassifier due to TensorFlow incompatibility with Python 3.14
        self.saved_dir = os.path.join(os.path.dirname(__file__), '..', saved_dir)
        os.makedirs(self.saved_dir, exist_ok=True)
        self.model_path = os.path.join(self.saved_dir, model_name)
        self.model = None

    def build_model(self):
        """Constructs the ANN architecture representation via MLP."""
        # 2 Hidden layers matching Keras Sequential requirement
        self.model = MLPClassifier(hidden_layer_sizes=(64, 32, 16), max_iter=500, random_state=42)
        return self.model

    def train(self, X_train, y_train, epochs=None, batch_size=None):
        if self.model is None:
            self.build_model()
        
        self.model.fit(X_train, y_train)
        joblib.dump(self.model, self.model_path)
        print(f"Deep learning surrogate (MLP) model saved to {self.model_path}")

    def load(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            return True
        return False

    def predict_proba(self, X):
        if self.model is None:
            if not self.load():
                raise FileNotFoundError("ANN Model not found for inference.")
        
        # Scikit predicts probability list per class
        probs = self.model.predict_proba(X)
        return probs[0][1]
