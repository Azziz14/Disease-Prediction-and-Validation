import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

export interface PatientRecord {
  id: string;
  doctorId: string;
  timestamp: string;
  glucose: number;
  bloodPressure: number;
  bmi: number;
  risk: string;
  confidence: number;
  matchedDrugs: string[];
  disease: string;
}

export const usePatientData = () => {
  const { user, isAdmin } = useAuth();
  const [history, setHistory] = useState<PatientRecord[]>([]);

  useEffect(() => {
    loadData();
  }, [user]);

  const loadData = () => {
    const rawData = localStorage.getItem('carepredict_history');
    if (rawData) {
      const allRecords: PatientRecord[] = JSON.parse(rawData);
      if (isAdmin) {
        setHistory(allRecords);
      } else if (user) {
        setHistory(allRecords.filter(r => r.doctorId === user.id));
      } else {
        setHistory([]);
      }
    }
  };

  const addRecord = (record: Omit<PatientRecord, 'id' | 'doctorId' | 'timestamp'>) => {
    if (!user) return;
    
    const newRecord: PatientRecord = {
      ...record,
      id: `pat_${Math.random().toString(36).substr(2, 9)}`,
      doctorId: user.id,
      timestamp: new Date().toISOString(),
    };

    const rawData = localStorage.getItem('carepredict_history');
    const currentRecords: PatientRecord[] = rawData ? JSON.parse(rawData) : [];
    
    const updatedRecords = [newRecord, ...currentRecords];
    localStorage.setItem('carepredict_history', JSON.stringify(updatedRecords));
    
    loadData();
    return newRecord;
  };

  const clearHistory = () => {
    if (isAdmin) {
      localStorage.removeItem('carepredict_history');
      setHistory([]);
    }
  };

  return { history, addRecord, clearHistory };
};
