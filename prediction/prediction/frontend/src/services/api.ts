/**
 * API Service - Healthcare Prediction System
 * Handles all communication with the backend Flask server
 */

const BASE_URL = 'http://127.0.0.1:5000/api';

/**
 * API Response Types
 */

export interface FeatureAnalysis {
  name: string;
  value: number;
  unit: string;
  normal_range: string;
  status: string;
}

export interface HealthReport {
  report_id: string;
  generated_at: string;
  summary: {
    disease_context: string;
    risk_level: string;
    confidence_score: number;
    overall_assessment: string;
  };
  feature_analysis: FeatureAnalysis[];
  risk_factors: Record<string, string>;
  drug_report: {
    prescribed: string;
    validated_drugs: string[];
    suggestions: string[];
    interactions_detected: string[];
    interaction_severity: string;
  };
  recommendations: string[];
  disclaimer: string;
}

export interface PredictionResponse {
  risk: 'High' | 'Moderate' | 'Low';
  confidence: number;
  disease: string;
  explanation: Record<string, string>;
  matched_drugs: string[];
  suggestions: string[];
  drug_interactions: string[];
  drug_details: Record<string, any>;
  report?: HealthReport;
  error?: string;
}

export interface PredictionRequest {
  features: number[];
  prescription: string;
  disease?: string;
}

export interface ImagePredictionResponse {
  classification: string;
  confidence: number;
  severity: string;
  description: string;
  recommended_action: string;
  differential_diagnosis: { label: string; confidence: number }[];
  disclaimer: string;
  error?: string;
}

export interface ModelInfo {
  available: boolean;
  disease_context?: string;
  models: {
    id: string;
    name: string;
    accuracy: number;
    is_best: boolean;
  }[];
  best_model?: string;
  ensemble_strategy?: string;
  disclaimer?: string;
  message?: string;
}

/**
 * Predict diabetes risk and get medication recommendations
 */
export const predictAPI = async (
  data: PredictionRequest
): Promise<PredictionResponse | null> => {
  try {
    const response = await fetch(`${BASE_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      console.error(`HTTP Error: ${response.status}`);
      return { 
        error: `Server returned status ${response.status}`,
        risk: 'Low',
        confidence: 0,
        disease: 'Unknown',
        matched_drugs: [],
        suggestions: [],
        drug_interactions: [],
        drug_details: {},
        explanation: {}
      };
    }

    const result: PredictionResponse = await response.json();
    return result;
  } catch (err) {
    console.error('API Error:', err);
    return null;
  }
};

/**
 * Upload a medical image for classification
 */
export const imagePredictAPI = async (
  file: File
): Promise<ImagePredictionResponse | null> => {
  try {
    const formData = new FormData();
    formData.append('image', file);

    const response = await fetch(`${BASE_URL}/image-predict`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      return {
        error: errData.error || `Server returned status ${response.status}`,
        classification: '',
        confidence: 0,
        severity: '',
        description: '',
        recommended_action: '',
        differential_diagnosis: [],
        disclaimer: ''
      };
    }

    return await response.json();
  } catch (err) {
    console.error('Image API Error:', err);
    return null;
  }
};

/**
 * Get model performance metadata for trust dashboard
 */
export const getModelInfoAPI = async (
  disease: string = 'diabetes'
): Promise<ModelInfo | null> => {
  try {
    const response = await fetch(`${BASE_URL}/model-info?disease=${disease}`);
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.error('Model Info API Error:', err);
    return null;
  }
};

export default { predictAPI, imagePredictAPI, getModelInfoAPI };
