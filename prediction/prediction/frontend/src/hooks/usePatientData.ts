import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getHistoryAPI } from '../services/api';

export interface PatientRecord {
  id: string;
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
  matchedDrugs: string[];
  disease: string;
  prescription_image?: string;
  autoMedications?: Array<{
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
}

export const usePatientData = () => {
  const { user } = useAuth();
  const [history, setHistory] = useState<PatientRecord[]>([]);

  const loadData = async () => {
    if (!user) return;
    try {
      const result = await getHistoryAPI(user.email, user.role);
      if (result && result.status === 'success') {
        const mappedHistory: PatientRecord[] = (result.history || []).map((r: any) => ({
          id: r.patient_id || r.id || r._id,
          mongoId: r.id || r._id,
          patientName: r.patient_name || 'Anonymous',
          doctorId: r.treating_doctor_id || r.doctor_id || 'System',
          doctorEmail: r.doctor_email || '',
          timestamp: r.timestamp || new Date().toISOString(),
          glucose: r.glucose || 0,
          bloodPressure: r.blood_pressure || r.bloodPressure || 0,
          bmi: r.bmi || 0,
          risk: r.risk || 'Low',
          confidence: r.confidence || 0,
          matchedDrugs: r.matched_drugs || r.matchedDrugs || [],
          disease: r.disease || r.disease_type || 'General',
          autoMedications: r.auto_medications || [],
          recommendations: r.recommendations || {},
          prescription_image: r.prescription_image
        }));
        setHistory(mappedHistory);
      }
    } catch (err) {
      console.error('History Fetch Failed:', err);
    }
  };

  useEffect(() => {
    loadData();
  }, [user]);

  // addRecord is now a no-op as the backend handles logging during prediction
  const addRecord = () => {
    loadData();
  };

  const clearHistory = () => {
    // History is DB-persisted, clearing locally only affects the current state
    setHistory([]);
  };

  return { history, addRecord, clearHistory, loadData };
};
