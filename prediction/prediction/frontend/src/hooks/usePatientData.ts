import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getHistoryAPI } from '../services/api';

export interface PatientRecord {
  id: string;
  patientId: string;
  mongoId?: string;
  patientName?: string;
  doctorId: string;
  doctorEmail: string;
  timestamp: string;
  glucose: number;
  bloodPressure: number;
  bmi: number;
  risk: string;
  confidence: number;
  matchedDrugs: any[];
  disease: string;
  prescription_image?: string;
  drugInteractions?: string[];
  prescriptionEvaluation?: {
    score: number;
    details: string[];
  };
  autoMedications?: Array<{
    name?: string;
    dosage?: string;
    frequency?: string;
    note?: string;
    purpose?: string;
  }>;
  recommendations?: {
    lifestyle?: string[];
    medical?: string[];
    precautions?: string[];
    summary?: string;
  };
}

export const usePatientData = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const { user } = useAuth();
  const [history, setHistory] = useState<PatientRecord[]>([]);

  const loadData = async (patientId?: string) => {
    if (!user) return;
    setLoading(true);
    try {
      const result = await getHistoryAPI(user.email, user.role, patientId);
      if (result && result.status === 'success') {
        const mappedHistory: PatientRecord[] = (result.history || []).map((r: any) => ({
          // Critical: Use the MongoDB _id for the React key to ensure uniqueness
          id: String(r.id || r._id || Math.random().toString()),
          patientId: String(r.patient_id || r.user_id || 'Unknown'),
          mongoId: String(r.id || r._id || ''),
          patientName: r.patient_name || 'Anonymous',
          doctorId: String(r.treating_doctor_id || r.doctor_id || 'System'),
          doctorEmail: r.doctor_email || '',
          timestamp: r.timestamp || r.date || new Date().toISOString(),
          glucose: Number(r.glucose || 0),
          bloodPressure: Number(r.blood_pressure || r.bloodPressure || 0),
          bmi: Number(r.bmi || 0),
          risk: String(r.risk || 'Low'),
          confidence: Number(r.confidence || 0),
          matchedDrugs: r.matched_drugs || r.matchedDrugs || [],
          disease: String(r.disease || r.disease_type || 'General'),
          autoMedications: r.auto_medications || [],
          recommendations: r.recommendations || {},
          prescription_image: r.prescription_image,
          drugInteractions: r.drug_interactions || [],
          prescriptionEvaluation: r.prescription_evaluation
        }));
        setHistory(mappedHistory);
      }
    } catch (err) {
      console.error('Failed to load history:', err);
      // Inject a visible error record so the UI isn't just blank
      setHistory([{
        id: 'error_node',
        patientId: 'ERROR',
        patientName: 'Connection Failure',
        timestamp: new Date().toISOString(),
        disease: 'System Offline',
        risk: 'High',
        doctorId: 'Network',
        glucose: 0,
        bloodPressure: 0,
        confidence: 0,
        autoMedications: [],
        recommendations: {},
        mongoId: 'error'
      } as any]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user && user.role === 'patient') {
      loadData(user.id);
    } else {
      loadData();
    }
  }, [user]);

  // addRecord triggers an immediate fresh retrieval matching user context
  const addRecord = () => {
    if (user && user.role === 'patient') {
      loadData(user.id);
    } else {
      loadData();
    }
  };

  const clearHistory = () => {
    // History is DB-persisted, clearing locally only affects the current state
    setHistory([]);
  };

  return { history, addRecord, clearHistory, loadData };
};
