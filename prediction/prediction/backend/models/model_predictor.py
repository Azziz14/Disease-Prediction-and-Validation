# Mock Fallback Prediction Model for Python 3.13 Compatibility
# Simulates TensorFlow prediction using a weighted heuristic algorithm.

def predict_diabetes(features):
    # Features: [pregnancies, glucose, bloodPressure, skinThickness, insulin, bmi, dpf, age]
    glucose = features[1]
    bmi = features[5]
    age = features[7]
    
    # Simple algorithmic weight simulation mapped to 0.0-1.0
    prob_score = (glucose / 200.0) * 0.6 + (bmi / 40.0) * 0.3 + (age / 80.0) * 0.1
    prob = max(0.0, min(prob_score, 1.0))

    return {
        "risk": "High" if prob > 0.65 else "Low",
        "confidence": float(prob),
        "disease": "diabetes" if prob > 0.65 else "healthy"
    }