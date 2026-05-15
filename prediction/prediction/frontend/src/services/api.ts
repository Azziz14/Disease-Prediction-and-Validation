/**
 * API Service - Healthcare Prediction System
 * Handles all communication with the backend Flask server
 */

const BASE_URL = `http://${window.location.hostname}:5000/api`;

/**
 * API Response Types
 */
export interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: 'doctor' | 'admin' | 'patient';
}

export interface AuthResponse {
  success: boolean;
  user?: AuthUser;
  error?: string;
}

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
  auto_medications?: Array<{
    name?: string;
    dosage?: string;
    frequency?: string;
    note?: string;
  }>;
  recommendations?: {
    lifestyle?: string[];
    medical?: string[];
    precautions?: string[];
  };
  prescription_evaluation?: {
    provided?: boolean;
    status?: string;
    message?: string;
    details?: string[];
  };
  report?: HealthReport;
  error?: string;
}

export interface PredictionRequest {
  features: number[];
  prescription: string;
  disease?: string;
  patient_id?: string;
  patient_name?: string;
  treating_doctor?: string;
}

export interface ImagePredictionResponse {
  status: string;
  prediction?: any;
  record_id?: string;
  consensus_intelligence?: {
    diagnosis: string;
    confidence: number;
    narrative: string;
    directives: any;
    handwriting_audit: {
       is_legible: boolean;
       clarity_score: number;
       verdict: string;
       audit_note: string;
    };
    medication_details: Array<{
       name: string;
       role: string;
       target_condition: string;
    }>;
  };
  auto_medications?: Array<{
    name: string;
    dosage: string;
    frequency: string;
    note: string;
  }>;
  prescription_image?: string;
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

export const registerAPI = async (payload: {
  email: string;
  password: string;
  role: 'doctor' | 'admin' | 'patient';
  name: string;
}): Promise<AuthResponse> => {
  try {
    const response = await fetch(`${BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    return await response.json();
  } catch (err) {
    console.error('Register API Error:', err);
    return { success: false, error: 'Could not connect to the authentication server.' };
  }
};

export const loginAPI = async (payload: {
  email: string;
  password: string;
}): Promise<AuthResponse> => {
  try {
    const response = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    return await response.json();
  } catch (err) {
    console.error('Login API Error:', err);
    return { success: false, error: 'Could not connect to the authentication server.' };
  }
};

/**
 * Predict diabetes risk and get medication recommendations
 */
export const predictAPI = async (
  data: PredictionRequest
): Promise<PredictionResponse | null> => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 40000); // 40 second timeout
    
    try {
      const response = await fetch(`${BASE_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data),
        signal: controller.signal
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
    } finally {
      clearTimeout(timeoutId);
    }
  } catch (err) {
    console.error('API Error:', err);
    return null;
  }
};

/**
 * Upload a medical image for classification
 */
export const imagePredictAPI = async (
  file: File,
  patientId?: string,
  patientName?: string,
  treatingDoctor?: string,
  treatingDoctorId?: string
): Promise<ImagePredictionResponse | null> => {
  try {
    const formData = new FormData();
    formData.append('image', file);
    if (patientId) formData.append('patient_id', patientId);
    if (patientName) formData.append('patient_name', patientName);
    if (treatingDoctor) formData.append('treating_doctor', treatingDoctor);
    if (treatingDoctorId) formData.append('treating_doctor_id', treatingDoctorId);

    const response = await fetch(`${BASE_URL}/upload-prescription`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      return {
        status: 'error',
        error: errData.error || `Server returned status ${response.status}`
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

export const getAdminPatientsAPI = async (): Promise<{
  status: string;
  data: { patients: any[]; total_count: number };
  error?: string;
} | null> => {
  try {
    const response = await fetch(`${BASE_URL}/admin-patients`);
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.error('Admin Patients API Error:', err);
    return null;
  }
};

export const getAllFeedbackAPI = async (): Promise<{
  status: string;
  data: any[];
  error?: string;
} | null> => {
  try {
    const response = await fetch(`${BASE_URL}/all-feedback`);
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.error('All Feedback API Error:', err);
    return null;
  }
};

export const downloadReportPDF = async (recordId: string): Promise<void> => {
  try {
    const response = await fetch(`${BASE_URL}/generate-pdf/${recordId}`);
    if (!response.ok) throw new Error('Failed to generate report');
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `MedReport_${recordId.substring(0, 8)}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  } catch (err) {
    console.error('PDF Download Error:', err);
    alert('Failed to generate high-quality PDF report. Please try again.');
  }
};

export const getHistoryAPI = async (email: string, role: string, patientId?: string): Promise<{ status: string; history: any[] } | null> => {
  try {
    const url = new URL(`${BASE_URL}/history`);
    url.searchParams.append('email', email);
    url.searchParams.append('role', role);
    if (patientId) url.searchParams.append('patient_id', patientId);
    // Cache bust to ensure fresh data on account switch
    url.searchParams.append('_t', Date.now().toString());
    
    const response = await fetch(url.toString());
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.error('History API Error:', err);
    return null;
  }
};

export default { predictAPI, imagePredictAPI, getModelInfoAPI, registerAPI, loginAPI, downloadReportPDF, getHistoryAPI };
