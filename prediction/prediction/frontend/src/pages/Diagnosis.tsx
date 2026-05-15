import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { predictAPI } from '../services/api';
import { usePatientData } from '../hooks/usePatientData';
import { useAuth } from '../context/AuthContext';

import CyberNeuralPath from '../components/ui/CyberNeuralPath';
import CyberAIWaveform from '../components/ui/CyberAIWaveform';
import ResultCard from '../components/ui/ResultCard';
import ImageUpload from '../components/ui/ImageUpload';
import { 
  Activity, ArrowLeft, ArrowRight, BrainCircuit, Check, CheckCircle, ChevronRight, 
  Database, Dumbbell, Fingerprint, Heart, HeartPulse, History, Info, Layers, Loader2, Mic, Pill, 
  Ruler, Shield, ShieldAlert, Sparkles, Square, Trash2, TrendingUp, Volume2, VolumeX, Zap,
  Calendar, Syringe, Baby, Hash, FileText, Brain, Stethoscope, Flame,
  Gauge, Moon, Users
} from 'lucide-react';

// ═══════════════════════════════════════════════════════
// Per-disease wizard step definitions
// Each disease has its own set of questions
// ALL must produce exactly 8 numeric features for the API
// ═══════════════════════════════════════════════════════

interface WizardStep {
  key: string;
  label: string;
  type: 'number' | 'select' | 'textarea' | 'select-numeric' | 'text';
  icon: React.ReactNode;
  placeholder?: string;
  options?: { value: string; label: string }[];
  hint?: string;
  condition?: string;
}

const DISEASE_SELECTOR: WizardStep = {
  key: 'disease', label: 'Select Target AI Model', type: 'select',
  icon: <BrainCircuit className="text-[var(--neon-purple)]" />
};

const PRESCRIPTION_STEP: WizardStep = {
  key: 'prescription', label: 'Clinical Notes / Prescription', type: 'textarea',
  icon: <FileText className="text-[var(--neon-blue)]" />,
  placeholder: 'Enter symptoms, medications, or prescriptions...'
};

const DISEASE_STEPS: Record<string, WizardStep[]> = {
  diabetes: [
    { key: 'treatingDoctor', label: 'Treating Physician Name', type: 'text', icon: <Stethoscope className="text-[var(--neon-green)]" />, placeholder: 'Enter your doctor\'s name' },
    { key: 'patientName', label: 'Patient Name', type: 'text', icon: <Users className="text-[var(--neon-blue)]" />, placeholder: 'Enter patient name' },
    { key: 'patientId', label: 'Patient Neural ID / Email', type: 'text', icon: <Fingerprint className="text-[var(--neon-purple)]" />, placeholder: 'e.g. patient@example.com or pat_123', hint: 'Leave empty for anonymous scan' },
    { key: 'biologicalSex', label: 'Biological Sex', type: 'select-numeric', icon: <Users className="text-[var(--neon-blue)]" />, options: [{ value: '1', label: 'Male' }, { value: '0', label: 'Female' }] },
    { key: 'pregnancies', label: 'Pregnancies', type: 'number', icon: <Baby className="text-[var(--neon-purple)]" />, placeholder: 'e.g. 2' },
    { key: 'glucose', label: 'Glucose Level (mg/dL)', type: 'number', icon: <Activity className="text-[var(--neon-blue)]" />, hint: 'Normal: 70-100 | Pre-diabetic: 100-125 | Diabetic: 126+', placeholder: 'e.g. 120' },
    { key: 'bloodPressure', label: 'Blood Pressure (mmHg)', type: 'number', icon: <HeartPulse className="text-[var(--neon-green)]" />, hint: 'Diastolic. Normal: 60-80 | Elevated: 80-90', placeholder: 'e.g. 72' },
    { key: 'skinThickness', label: 'Triceps Skin Thickness (mm)', type: 'number', icon: <Ruler className="text-[var(--neon-blue)]" />, hint: 'Normal: 10-50 mm', placeholder: 'e.g. 35' },
    { key: 'insulin', label: 'Insulin Level (µU/mL)', type: 'number', icon: <Syringe className="text-[var(--neon-green)]" />, hint: 'Normal: 16-166 µU/mL', placeholder: 'e.g. 100' },
    { key: 'bmi', label: 'Body Mass Index (BMI)', type: 'number', icon: <Ruler className="text-[var(--neon-blue)]" />, hint: 'Normal: 18.5-25 | Overweight: 25-30 | Obese: 30+', placeholder: 'e.g. 28.5' },
    { key: 'pedigree', label: 'Diabetes Pedigree Function', type: 'number', icon: <Hash className="text-[var(--neon-green)]" />, hint: 'Likelihood based on family history (e.g. 0.08 - 2.42)', placeholder: 'e.g. 0.47' },
    { key: 'age', label: 'Patient Age', type: 'number', icon: <Calendar className="text-[var(--neon-purple)]" />, placeholder: 'e.g. 45' },
  ],
  heart: [
    { key: 'treatingDoctor', label: 'Treating Physician Name', type: 'text', icon: <Stethoscope className="text-[var(--neon-green)]" />, placeholder: 'Enter your doctor\'s name' },
    { key: 'patientName', label: 'Patient Name', type: 'text', icon: <Users className="text-[var(--neon-blue)]" />, placeholder: 'Enter patient name' },
    { key: 'patientId', label: 'Patient Neural ID / Email', type: 'text', icon: <Fingerprint className="text-[var(--neon-purple)]" />, placeholder: 'e.g. patient@example.com' },
    { key: 'age', label: 'Patient Age', type: 'number', icon: <Calendar className="text-[var(--neon-purple)]" />, placeholder: 'e.g. 55' },
    { key: 'sex', label: 'Biological Sex', type: 'select-numeric', icon: <Users className="text-[var(--neon-blue)]" />, options: [{ value: '1', label: 'Male' }, { value: '0', label: 'Female' }] },
    { key: 'chestPain', label: 'Chest Pain Type', type: 'select-numeric', icon: <ShieldAlert className="text-[var(--neon-green)]" />, options: [{ value: '0', label: 'Typical Angina' }, { value: '1', label: 'Atypical Angina' }, { value: '2', label: 'Non-Anginal Pain' }, { value: '3', label: 'Asymptomatic' }] },
    { key: 'restingBP', label: 'Resting Blood Pressure (mmHg)', type: 'number', icon: <HeartPulse className="text-[var(--neon-green)]" />, hint: 'Normal: <120 | Elevated: 120-139', placeholder: 'e.g. 130' },
    { key: 'cholesterol', label: 'Serum Cholesterol (mg/dL)', type: 'number', icon: <Flame className="text-[var(--neon-blue)]" />, hint: 'Desirable: <200 | Borderline: 200-239', placeholder: 'e.g. 240' },
    { key: 'fastingBS', label: 'Fasting Blood Sugar > 120?', type: 'select-numeric', icon: <Gauge className="text-[var(--neon-purple)]" />, options: [{ value: '1', label: 'Yes (> 120 mg/dL)' }, { value: '0', label: 'No (≤ 120 mg/dL)' }] },
    { key: 'maxHR', label: 'Maximum Heart Rate Achieved', type: 'number', icon: <Zap className="text-[var(--neon-green)]" />, hint: 'Typical range: 60-220 bpm', placeholder: 'e.g. 150' },
    { key: 'exerciseAngina', label: 'Exercise-Induced Angina?', type: 'select-numeric', icon: <Dumbbell className="text-[var(--neon-blue)]" />, options: [{ value: '1', label: 'Yes' }, { value: '0', label: 'No' }] },
  ],
  mental: [
    { key: 'treatingDoctor', label: 'Treating Physician Name', type: 'text', icon: <Stethoscope className="text-[var(--neon-green)]" />, placeholder: 'Enter your doctor\'s name' },
    { key: 'patientName', label: 'Patient Name', type: 'text', icon: <Users className="text-[var(--neon-blue)]" />, placeholder: 'Enter patient name' },
    { key: 'patientId', label: 'Patient Neural ID / Email', type: 'text', icon: <Fingerprint className="text-[var(--neon-purple)]" />, placeholder: 'e.g. patient@example.com' },
    { key: 'age', label: 'Patient Age', type: 'number', icon: <Calendar className="text-[var(--neon-purple)]" />, placeholder: 'e.g. 30' },
    { key: 'gender', label: 'Gender', type: 'select-numeric', icon: <Users className="text-[var(--neon-blue)]" />, options: [{ value: '0', label: 'Male' }, { value: '1', label: 'Female' }, { value: '2', label: 'Non-Binary / Other' }] },
    { key: 'familyHistory', label: 'Family History of Mental Illness?', type: 'select-numeric', icon: <Hash className="text-[var(--neon-green)]" />, options: [{ value: '1', label: 'Yes' }, { value: '0', label: 'No' }] },
    { key: 'workInterfere', label: 'Does Work Interfere with Treatment?', type: 'select-numeric', icon: <Brain className="text-[var(--neon-purple)]" />, options: [{ value: '0', label: 'Never' }, { value: '1', label: 'Rarely' }, { value: '2', label: 'Sometimes' }, { value: '3', label: 'Often' }] },
    { key: 'sleepHours', label: 'Average Sleep Hours per Night', type: 'number', icon: <Moon className="text-[var(--neon-blue)]" />, hint: 'Healthy: 7–9 hours', placeholder: 'e.g. 6' },
    { key: 'stressLevel', label: 'Stress Level (1–10)', type: 'number', icon: <Flame className="text-[var(--neon-green)]" />, hint: '1 = Very Low, 10 = Extreme', placeholder: 'e.g. 7' },
    { key: 'socialSupport', label: 'Social Support Level (1–10)', type: 'number', icon: <Stethoscope className="text-[var(--neon-purple)]" />, hint: '1 = None, 10 = Strong', placeholder: 'e.g. 5' },
    { key: 'treatmentSeeking', label: 'Currently Seeking Treatment?', type: 'select-numeric', icon: <Pill className="text-[var(--neon-blue)]" />, options: [{ value: '1', label: 'Yes' }, { value: '0', label: 'No' }] },
  ],
};

// Build the features array for the backend (always 8 numbers)
function buildPayload(disease: string, features: Record<string, any>) {
  if (disease === 'diabetes') {
    // Force 0 pregnancies for males to maintain model input integrity
    const pregCount = (features.biologicalSex === '1') ? 0 : Number(features.pregnancies);
    return [
      pregCount,
      Number(features.glucose),
      Number(features.bloodPressure),
      Number(features.skinThickness),
      Number(features.insulin),
      Number(features.bmi),
      Number(features.pedigree),
      Number(features.age)
    ];
  }
  
  const steps = DISEASE_STEPS[disease];
  // Filter out metadata steps (like name) for the ML payload
  return steps
    .filter(step => step.type !== 'text' && step.type !== 'textarea')
    .map(step => Number(features[step.key]) || 0);
}

// Get default features for a given disease
function getDefaultFeatures(disease: string): Record<string, any> {
  const defaults: Record<string, any> = { disease, prescription: '' };
  DISEASE_STEPS[disease].forEach(s => { defaults[s.key] = ''; });
  return defaults;
}

// Direction tracking for animation
type Direction = 'forward' | 'backward';

const slideVariants = {
  enter: (dir: Direction) => ({
    opacity: 0,
    y: dir === 'forward' ? 60 : -60,
    scale: 0.92,
    filter: 'blur(8px)',
  }),
  center: {
    opacity: 1,
    y: 0,
    scale: 1,
    filter: 'blur(0px)',
  },
  exit: (dir: Direction) => ({
    opacity: 0,
    y: dir === 'forward' ? -40 : 40,
    scale: 1.02,
    filter: 'blur(10px)',
    transition: { duration: 0.3, ease: [0.4, 0, 0.2, 1] }
  }),
};

const Diagnosis: React.FC = () => {
  const { addRecord } = usePatientData();
  const { user } = useAuth();
  const location = useLocation();
  const [targetPatientId, setTargetPatientId] = useState<string | null>(null);
  const [assignedPhysician, setAssignedPhysician] = useState<string | null>(null);

  const [activeTab, setActiveTab] = useState<'structured' | 'image' | 'voice'>('structured');
  const [currentStep, setCurrentStep] = useState(0);
  const [direction, setDirection] = useState<Direction>('forward');
  const [features, setFeatures] = useState<Record<string, any>>(() => {
    const initial = getDefaultFeatures('diabetes');
    if (user && user.role === 'patient') {
      initial.patientName = user.name;
    }
    return initial;
  });

  // Build the full wizard steps dynamically: disease selector + disease-specific inputs + prescription
  const wizardSteps = useMemo(() => {
    let diseaseInputs = DISEASE_STEPS[features.disease] || DISEASE_STEPS.diabetes;
    
    // SURGICAL REMOVAL: For patients, identity fields are completely removed from the wizard
    if (user && user.role === 'patient') {
      diseaseInputs = diseaseInputs.filter(step => 
        step.key !== 'treatingDoctor' && step.key !== 'patientName' && step.key !== 'patientId'
      );
    }
    
    // GENDER INTELLIGENCE: Skip pregnancies for males
    if (features.disease === 'diabetes' && features.biologicalSex === '1') {
      diseaseInputs = diseaseInputs.filter(step => step.key !== 'pregnancies');
    }
    
    return [DISEASE_SELECTOR, ...diseaseInputs, PRESCRIPTION_STEP];
  }, [features.disease, user, features.biologicalSex]);

  // Handle URL parameters and Patient-Doctor binding
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const pName = params.get('patientName');
    const pId = params.get('patientId');
    
    // 1. Resolve Patient Identity from URL (Doctor flow)
    if (pName) {
      setFeatures(prev => ({ ...prev, patientName: pName }));
      if (pId) setTargetPatientId(pId);
      
      // Automatically advance past disease selection and identity fields
      if (currentStep === 0) {
          let targetStep = 1; // Start by skipping disease selector
          
          if (wizardSteps[targetStep]?.key === 'treatingDoctor' && user?.role === 'doctor') {
            targetStep++;
          }
          
          if (wizardSteps[targetStep]?.key === 'patientName') {
            targetStep++;
          }

          if (wizardSteps[targetStep]?.key === 'patientId') {
            targetStep++;
          }
          
          setCurrentStep(targetStep); 
      }
    }
    
    // 2. Resolve Doctor Identity for Patients (Patient flow)
    const resolvePatientDoctor = async () => {
      if (user && user.role === 'patient') {
        try {
          const res = await fetch(`${process.env.REACT_APP_API_URL || 'http://' + window.location.hostname + ':5000'}/api/patient-assignment?patient_id=${user.id}`);
          const data = await res.json();
          if (data.status === 'success' && data.assigned) {
            setAssignedPhysician(data.doctor_name);
            setFeatures(prev => ({ 
              ...prev, 
              treatingDoctor: data.doctor_name, 
              patientName: user.name 
            }));
          }
        } catch (e) {
          console.warn("Failed to resolve assigned doctor", e);
        }
      }
    };
    
    resolvePatientDoctor();
  }, [location.search, user, wizardSteps]);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [apiError, setApiError] = useState("");
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>(null);

  // Voice Diagnosis mode state
  const [voiceDisease, setVoiceDisease] = useState('diabetes');
  const [voiceRecording, setVoiceRecording] = useState(false);
  const [voiceLanguage, setVoiceLanguage] = useState<'en-IN' | 'hi-IN' | 'en-US'>('en-IN');
  const [voiceProcessing, setVoiceProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceResult, setVoiceResult] = useState<any>(null);
  const speechRecognitionRef = useRef<any>(null);

  // ═══ Voice Input State (for prescription field) ═══
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [voiceTranscript, setVoiceTranscript] = useState<string | null>(null);

  // ═══ Browser Web Speech API — prescription voice input ═══
  const startVoiceRecording = useCallback(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech Recognition is not supported in this browser. Please use Chrome.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    let finalText = '';

    recognition.onresult = (event: any) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalText += transcript + ' ';
        }
      }
      setVoiceTranscript(finalText.trim() || 'Listening...');
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      if (event.error === 'not-allowed') {
        alert('Microphone access denied. Please allow microphone permissions.');
      }
      setIsRecording(false);
    };

    recognition.onend = () => {
      setIsRecording(false);
      if (finalText.trim()) {
        setVoiceTranscript(finalText.trim());
        // Auto-fill into prescription field
        setFeatures(prev => ({
          ...prev,
          prescription: prev.prescription ? prev.prescription + ' ' + finalText.trim() : finalText.trim()
        }));
      }
    };

    speechRecognitionRef.current = recognition;
    recognition.start();
    setIsRecording(true);
    setVoiceTranscript('Listening...');
  }, []);

  const stopVoiceRecording = useCallback(() => {
    if (speechRecognitionRef.current) {
      speechRecognitionRef.current.stop();
      setIsRecording(false);
    }
  }, []);

  // ═══ Voice Diagnosis — full pipeline using Web Speech API ═══
  const startVoiceDiagnosis = useCallback(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setVoiceResult({ error: 'Speech Recognition not supported. Please use Google Chrome.' });
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false; // Better for discrete command-based diagnostics
    recognition.interimResults = true;
    recognition.lang = voiceLanguage;

    let finalText = '';

    recognition.onresult = (event: any) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalText += transcript + ' ';
        }
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setVoiceRecording(false);
      if (event.error === 'not-allowed') {
        setVoiceResult({ error: 'Microphone access denied. Please allow microphone permissions in your browser.' });
      } else if (event.error === 'no-speech') {
        setVoiceResult({ error: 'No speech detected. Please speak clearly and try again.' });
      } else {
        setVoiceResult({ error: `Speech recognition error: ${event.error}` });
      }
    };

    recognition.onend = () => {
      // Recognition ended — now send transcribed text to backend
      setVoiceRecording(false);
      setIsTranscribing(true);
      const text = finalText.trim();
      if (!text) {
        setVoiceResult({ error: 'No speech detected. Please speak clearly for at least 3 seconds.' });
        setIsTranscribing(false);
        return;
      }

      // Send text to backend for parameter extraction + ML prediction
      setVoiceProcessing(true);
      const formData = new FormData();
      formData.append('text', text);
      formData.append('disease', voiceDisease);

      fetch(`${process.env.REACT_APP_API_URL || 'http://' + window.location.hostname + ':5000'}/api/voice-diagnosis`, {
        method: 'POST',
        body: formData
      })
        .then(res => res.json())
        .then(data => {
          if (data.status === 'success') {
            setVoiceResult(data);
            // Auto-speak the narrative if available
            if (data.clinical_narrative || data.consensus_intelligence?.narrative) {
              const textToSpeak = data.clinical_narrative || data.consensus_intelligence?.narrative;
              speakNarrative(textToSpeak);
            }
          } else {
            setVoiceResult({ error: data.error || 'Voice diagnosis failed.' });
          }
        })
        .catch(err => {
          console.error(err);
          setVoiceResult({ error: 'Could not connect to backend. Is the server running?' });
        })
        .finally(() => {
          setVoiceProcessing(false);
          setIsTranscribing(false);
        });
    };

    speechRecognitionRef.current = recognition;
    recognition.start();
    setVoiceRecording(true);
    setVoiceResult(null);
    if (window.speechSynthesis) window.speechSynthesis.cancel();
  }, [voiceDisease, voiceLanguage]);

  const speakNarrative = (text: string) => {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    
    const cleanText = text.replace(/[*#\[\]]/g, '').replace(/([.?!])\s*/g, '$1   ');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = voiceLanguage.startsWith('hi') ? 'hi-IN' : 'en-IN';
    utterance.rate = 0.9;
    
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    
    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  const stopVoiceDiagnosis = useCallback(() => {
    if (speechRecognitionRef.current && voiceRecording) {
      speechRecognitionRef.current.stop();
    }
  }, [voiceRecording]);


  // Auto-focus input on step change
  useEffect(() => {
    const timer = setTimeout(() => {
      inputRef.current?.focus();
    }, 400);
    return () => clearTimeout(timer);
  }, [currentStep]);

  // When disease changes (step 0), reset all feature values and go back to step 1
  const handleDiseaseChange = (newDisease: string) => {
    if (newDisease !== features.disease) {
      const resetFeatures = getDefaultFeatures(newDisease);
      if (user && user.role === 'patient') {
        resetFeatures.patientName = user.name;
        if (assignedPhysician) resetFeatures.treatingDoctor = assignedPhysician;
      }
      setFeatures(resetFeatures);
      // Don't change step — user clicks Next to proceed
    } else {
      setFeatures({ ...features, disease: newDisease });
    }
  };

  const handleNext = () => {
    const stepKey = wizardSteps[currentStep].key;
    // Prescription is OPTIONAL — don't block on empty value for textarea fields
    if (stepKey !== 'disease' && stepKey !== 'prescription' && features[stepKey] === "") return;

    let nextStep = currentStep + 1;
    
    // Skip treating doctor if the user is a doctor (still in the array for doctors, but skipped)
    if (nextStep < wizardSteps.length) {
      const nextKey = wizardSteps[nextStep].key;
      if (nextKey === 'treatingDoctor' && user?.role === 'doctor') nextStep++;
    }

    setDirection('forward');
    if (nextStep < wizardSteps.length) {
      setCurrentStep(nextStep);
    } else {
      handleSubmit();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      let prevStep = currentStep - 1;
      
      setDirection('backward');
      setCurrentStep(prevStep);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleNext();
    }
    if (e.key === 'Backspace' && features[wizardSteps[currentStep].key] === "" && currentStep > 0) {
      handleBack();
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    setApiError("");
    try {
      const payload: any = {
        features: buildPayload(features.disease, features),
        prescription: features.prescription,
        disease: features.disease,
        patient_name: features.patientName || user?.name || 'Unknown Patient',
        patient_id: targetPatientId || features.patientId || (user?.role === 'patient' ? user?.id || user?.email : 'web_user'),
        treating_doctor: features.treatingDoctor || assignedPhysician || (user?.role === 'doctor' ? user?.name : 'Primary Physician Sync'),
        treating_doctor_id: (user?.role === 'doctor' ? user?.id || user?.email : undefined) 
      };
      // If we're a patient, and we have an assigned doctor, we should ideally pass their ID too if we had it.
      // For now, focusing on the Doctor's dashboard fix as requested.

      const response = await predictAPI(payload);
      if (!response) {
        setApiError("BACKEND OFFLINE — Unable to reach the backend API. Start the Flask server and ensure port 5000 is accessible.");
      } else if (response.error) {
        setApiError(response.error);
      } else {
        setResult(response);
        addRecord({
          glucose: Number(features.glucose || 0), bloodPressure: Number(features.bloodPressure || features.restingBP || 0),
          bmi: Number(features.bmi || 0), risk: response.risk, confidence: response.confidence,
          matchedDrugs: response.matched_drugs || [],
          disease: response.disease || features.disease,
          autoMedications: response.auto_medications || [],
          recommendations: response.recommendations || {},
          drugInteractions: response.drug_interactions || [],
          prescriptionEvaluation: response.prescription_evaluation || undefined,
          treatingDoctor: response.treating_doctor || features.treatingDoctor,
          patientName: response.patient_name || features.patientName
        });
      }
    } catch {
      setApiError("CRITICAL FAILURE — Neural uplink connection lost. Check that the Flask backend is running and reachable.");
    } finally {
      setLoading(false);
    }
  };

  // Cursor gravity effect (Optimized)
  const containerRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    let animationFrameId: number;
    const handleGlobalMouse = (e: MouseEvent) => {
      animationFrameId = requestAnimationFrame(() => {
        if (!containerRef.current) return;
        const x = (e.clientX / window.innerWidth) * 2 - 1;
        const y = (e.clientY / window.innerHeight) * 2 - 1;
        containerRef.current.style.transform = `translateZ(0) rotateX(${-y * 1}deg) rotateY(${x * 1}deg)`;
      });
    };
    window.addEventListener('mousemove', handleGlobalMouse);
    return () => {
      window.removeEventListener('mousemove', handleGlobalMouse);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  const currentField = wizardSteps[currentStep];

  // Disease description badge
  const diseaseLabels: Record<string, { name: string; color: string }> = {
    diabetes: { name: 'DIABETES PROTOCOL', color: 'var(--neon-green)' },
    heart: { name: 'CARDIAC PROTOCOL', color: 'var(--neon-blue)' },
    mental: { name: 'NEURO-PSYCH PROTOCOL', color: 'var(--neon-purple)' },
  };

  return (
    <div className="relative min-h-[calc(100vh-80px)] w-full flex flex-col items-center pt-8 md:pt-16 pb-10" style={{ perspective: '1200px' }}>

      {/* TABS */}
      <div className="z-[100] glass-panel p-1.5 flex gap-2 pointer-events-auto mb-8 relative">
        <button
          onClick={() => setActiveTab('structured')}
          className={`px-6 py-2 rounded-xl font-bold transition-all duration-300 ${activeTab === 'structured' ? 'bg-[var(--cyber-dark)] neon-text-blue border border-[var(--neon-blue)]' : 'text-gray-400 hover:text-white'}`}
        >
          Neural Diagnostic
        </button>
        <button
          onClick={() => { setActiveTab('voice'); setVoiceResult(null); }}
          className={`px-6 py-2 rounded-xl font-bold transition-all duration-300 ${activeTab === 'voice' ? 'bg-[var(--cyber-dark)] neon-text-green border border-[var(--neon-green)]' : 'text-gray-400 hover:text-white'}`}
        >
          <span className="flex items-center gap-2"><Mic size={14} /> Voice Diagnosis</span>
        </button>
        <button
          onClick={() => setActiveTab('image')}
          className={`px-6 py-2 rounded-xl font-bold transition-all duration-300 ${activeTab === 'image' ? 'bg-[var(--cyber-dark)] neon-text-purple border border-[var(--neon-purple)]' : 'text-gray-400 hover:text-white'}`}
        >
          Visual Scan
        </button>
      </div>

      <motion.div
        ref={containerRef}
        className="w-full max-w-3xl px-6 relative z-10 flex flex-col items-center justify-center"
        style={{
          transition: 'transform 0.1s linear',
          willChange: 'transform',
          transformStyle: 'preserve-3d',
          backfaceVisibility: 'hidden'
        }}
      >
        {activeTab === 'structured' ? (
           !result ? (
            <div className="glass-panel glowing-wrap p-10 md:p-14 text-center min-h-[500px] flex flex-col justify-center relative">
              <h1 className="text-3xl md:text-5xl font-extrabold mb-2 tracking-tight neon-text-blue">
                SYSTEM INITIALIZATION
              </h1>

              {/* Active protocol badge — shows which disease is selected */}
              {currentStep > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mx-auto mb-6 px-4 py-1 rounded-full border text-xs font-bold uppercase tracking-[0.2em]"
                  style={{
                    borderColor: diseaseLabels[features.disease]?.color,
                    color: diseaseLabels[features.disease]?.color,
                    boxShadow: `0 0 10px ${diseaseLabels[features.disease]?.color}40`,
                  }}
                >
                  {diseaseLabels[features.disease]?.name}
                </motion.div>
              )}

              {currentStep === 0 && (
                <p className="text-gray-400 mb-10 uppercase tracking-widest text-sm">Select diagnostic protocol to begin...</p>
              )}

              {apiError && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="w-full max-w-lg mx-auto mb-8 bg-red-900/30 border border-red-500/50 rounded-2xl p-6 text-center shadow-[0_0_30px_rgba(255,0,0,0.15)]"
                >
                  <div className="text-red-400 text-3xl mb-3">⚠</div>
                  <h3 className="text-red-300 font-extrabold uppercase tracking-widest text-sm mb-2">Connection Failed</h3>
                  <p className="text-red-200/70 text-sm mb-5 leading-relaxed">{apiError}</p>
                  <div className="flex gap-3 justify-center">
                    <button
                      onClick={() => { setApiError(""); handleSubmit(); }}
                      className="px-6 py-2.5 bg-red-500/20 border border-red-500 text-red-300 rounded-xl font-bold text-xs uppercase tracking-widest hover:bg-red-500/40 transition-all duration-300"
                    >
                      Retry Scan
                    </button>
                    <button
                      onClick={() => { setApiError(""); setCurrentStep(wizardSteps.length - 1); }}
                      className="px-6 py-2.5 border border-white/20 text-gray-400 rounded-xl font-bold text-xs uppercase tracking-widest hover:border-[var(--neon-blue)] hover:text-[var(--neon-blue)] transition-all duration-300"
                    >
                      Go Back
                    </button>
                  </div>
                </motion.div>
              )}

              {loading ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex flex-col items-center justify-center gap-6 py-10"
                >
                  <CyberAIWaveform isThinking={true} />
                  <p className="neon-text-green text-lg tracking-widest animate-pulse">ANALYZING BIOMETRICS...</p>
                </motion.div>
              ) : !apiError ? (
                <div className="flex-1 flex flex-col items-center justify-center">
                  <AnimatePresence mode="wait" custom={direction}>
                    <motion.div
                      key={`${features.disease}-${currentStep}`}
                      custom={direction}
                      variants={slideVariants}
                      initial="enter"
                      animate="center"
                      exit="exit"
                      transition={{ 
                        duration: 0.5, 
                        ease: [0.22, 1, 0.36, 1],
                        opacity: { duration: 0.3 }
                      }}
                      className="w-full max-w-md flex flex-col items-center gap-5"
                    >
                      {/* Step counter */}
                      <div className="text-xs text-gray-500 uppercase tracking-[0.3em] font-bold">
                        Step {currentStep + 1} <span className="text-gray-600">/ {wizardSteps.length}</span>
                      </div>

                      <div className="flex items-center gap-4 text-2xl font-semibold mb-1">
                        {currentField.icon}
                        <h2>{currentField.label}</h2>
                      </div>

                      {/* Hint text */}
                      {'hint' in currentField && currentField.hint && (
                        <p className="text-xs text-gray-500 -mt-3 tracking-wide">{currentField.hint}</p>
                      )}

                      {/* ---- INPUT RENDERING ---- */}
                      {currentField.type === 'select' ? (
                        <select
                          ref={inputRef as React.RefObject<HTMLSelectElement>}
                          value={features[currentField.key]}
                          onChange={(e) => handleDiseaseChange(e.target.value)}
                          className="glass-input w-full text-center text-xl p-4 rounded-xl appearance-none cursor-pointer"
                        >
                          <option value="diabetes" className="bg-[#090a0f]">🧬 Diabetes Baseline (Pima Config)</option>
                          <option value="heart" className="bg-[#090a0f]">❤️ Heart Disease Risk (Cardiac)</option>
                          <option value="mental" className="bg-[#090a0f]">🧠 Mental Health Baseline (Neuro)</option>
                        </select>
                      ) : currentField.type === 'select-numeric' ? (
                        <select
                          ref={inputRef as React.RefObject<HTMLSelectElement>}
                          value={features[currentField.key]}
                          onChange={(e) => setFeatures({ ...features, [currentField.key]: e.target.value })}
                          className="glass-input w-full text-center text-xl p-4 rounded-xl appearance-none cursor-pointer"
                        >
                          <option value="" disabled className="bg-[#090a0f]">— Select —</option>
                          {currentField.options?.map(opt => (
                            <option key={opt.value} value={opt.value} className="bg-[#090a0f]">{opt.label}</option>
                          ))}
                        </select>
                      ) : currentField.type === 'textarea' ? (
                        <div className="w-full space-y-4">
                          <textarea
                            ref={inputRef as React.RefObject<HTMLTextAreaElement>}
                            value={features[currentField.key]}
                            onChange={(e) => setFeatures({ ...features, [currentField.key]: e.target.value })}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter' && e.ctrlKey) handleNext();
                            }}
                            placeholder={currentField.placeholder || 'Enter symptoms or prescriptions... (Ctrl+Enter to submit)'}
                            className="glass-input w-full p-4 rounded-xl text-lg h-32 resize-none"
                          />

                          {/* ═══ VOICE INPUT BUTTON ═══ */}
                          <div className="flex flex-col items-center gap-3">
                            <div className="flex items-center gap-3">
                              {!isRecording ? (
                                <button
                                  type="button"
                                  onClick={startVoiceRecording}
                                  disabled={isTranscribing}
                                  className={`group relative flex items-center gap-3 px-6 py-3 rounded-full font-bold text-sm uppercase tracking-widest transition-all duration-300 ${
                                    isTranscribing
                                      ? 'bg-gray-700/50 text-gray-500 cursor-wait'
                                      : 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-500/40 text-cyan-300 hover:border-cyan-400 hover:shadow-[0_0_25px_rgba(34,211,238,0.3)] hover:scale-105'
                                  }`}
                                >
                                  {isTranscribing ? (
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                  ) : (
                                    <Mic className="w-5 h-5 group-hover:animate-pulse" />
                                  )}
                                  {isTranscribing ? 'PROCESSING WITH WAV2VEC2...' : 'VOICE INPUT (RNN/DL)'}
                                  {!isTranscribing && (
                                    <span className="absolute -top-1 -right-1 w-3 h-3 bg-cyan-400 rounded-full animate-ping" />
                                  )}
                                </button>
                              ) : (
                                <button
                                  type="button"
                                  onClick={stopVoiceRecording}
                                  className="flex items-center gap-3 px-6 py-3 rounded-full bg-red-500/20 border border-red-500/50 text-red-400 font-bold text-sm uppercase tracking-widest animate-pulse hover:bg-red-500/30 transition-all duration-300"
                                >
                                  <Square className="w-5 h-5" />
                                  STOP RECORDING
                                  <span className="w-2 h-2 bg-red-500 rounded-full animate-ping" />
                                </button>
                              )}
                            </div>

                            {/* Recording indicator */}
                            {isRecording && (
                              <motion.div
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="flex items-center gap-2 text-red-400 text-xs tracking-widest"
                              >
                                <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                                LISTENING... Speak your symptoms clearly
                              </motion.div>
                            )}

                            {/* Transcription result */}
                            {voiceTranscript && !isTranscribing && (
                              <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="w-full bg-cyan-500/10 border border-cyan-500/20 rounded-xl p-3 text-sm text-cyan-300"
                              >
                                <span className="text-[10px] uppercase tracking-widest text-cyan-500/60 block mb-1">Wav2Vec2 Transcription:</span>
                                {voiceTranscript}
                              </motion.div>
                            )}

                            <p className="text-[10px] text-gray-600 tracking-wider">
                              Powered by facebook/wav2vec2-base-960h local deep learning model
                            </p>
                          </div>
                        </div>
                      ) : (
                        <input
                          ref={inputRef as React.RefObject<HTMLInputElement>}
                          type={currentField.type === 'text' ? 'text' : 'number'}
                          value={features[currentField.key]}
                          onChange={(e) => setFeatures({ ...features, [currentField.key]: e.target.value })}
                          onKeyDown={handleKeyDown}
                          placeholder={currentField.placeholder || `Enter ${currentField.label}`}
                          className="glass-input w-full text-center text-3xl font-bold py-4 rounded-xl focus:scale-[1.03] transition-transform duration-300"
                        />
                      )}

                      {/* Button row with Back + Next */}
                      <div className="flex items-center gap-4 mt-3 w-full justify-center">
                        {currentStep > 0 && (
                          <motion.button
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            onClick={handleBack}
                            className="flex items-center gap-2 border border-white/20 text-gray-300 font-bold px-6 py-3 rounded-full hover:border-[var(--neon-purple)] hover:text-[var(--neon-purple)] hover:shadow-[0_0_15px_rgba(176,91,255,0.3)] transition-all duration-300 group"
                          >
                            <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform duration-300" /> BACK
                          </motion.button>
                        )}
                        <button
                          onClick={handleNext}
                          disabled={currentField.key !== 'disease' && currentField.key !== 'prescription' && features[currentField.key] === ""}
                          className="flex items-center gap-2 bg-[var(--neon-blue)] text-black font-bold px-8 py-3 rounded-full hover:shadow-[0_0_20px_var(--neon-blue)] hover:bg-white transition-all duration-300 disabled:opacity-20 disabled:pointer-events-none group"
                        >
                         {currentStep === wizardSteps.length - 1 ? (features.prescription ? 'INITIATE SCAN' : 'SKIP & SCAN') : 'NEXT PARAMETER'} <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform duration-300" />
                        </button>
                      </div>
                    </motion.div>
                  </AnimatePresence>
                </div>
              ) : null}

              {!loading && !apiError && <CyberNeuralPath totalSteps={wizardSteps.length} currentStep={currentStep} />}
            </div>
           ) : (
             <motion.div
                initial={{ opacity: 0, scale: 0.9, filter: 'blur(10px)' }}
                animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
                transition={{ duration: 0.6, ease: [0.33, 1, 0.68, 1] }}
             >
                <div className="glass-panel p-6">
                  <ResultCard result={result} />
                  <button
                    onClick={() => {
                      setResult(null);
                      setCurrentStep(0);
                      setDirection('forward');
                      setFeatures(getDefaultFeatures('diabetes'));
                    }}
                    className="mt-6 w-full py-3 border border-[var(--neon-blue)] text-[var(--neon-blue)] rounded-xl hover:bg-[var(--neon-blue)] hover:text-black font-bold transition-all duration-300"
                  >
                    START NEW DIAGNOSIS
                  </button>
                </div>
             </motion.div>
           )
        ) : activeTab === 'voice' ? (
           /* ═══════════════════════════════════════════════ */
           /* VOICE DIAGNOSIS MODE                            */
           /* ═══════════════════════════════════════════════ */
           <div className="glass-panel glowing-wrap p-8 md:p-12 text-center min-h-[500px] flex flex-col items-center gap-6">
             <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight neon-text-green">
               VOICE DIAGNOSIS
             </h1>
             <p className="text-gray-400 text-sm max-w-md">
               Select your diagnostic protocol, then speak all your medical data naturally.
               The AI will extract parameters, fill in any gaps, and run the full prediction.
               <br/><span className="text-cyan-500">Prescription is optional</span> — medications will be auto-suggested.
             </p>
              <div className="w-full max-w-sm flex gap-3">
                <div className="flex-1 text-left">
                  <label className="text-[10px] text-gray-500 uppercase tracking-widest block mb-2">Protocol</label>
                  <select
                    value={voiceDisease}
                    onChange={(e) => { setVoiceDisease(e.target.value); setVoiceResult(null); }}
                    className="glass-input w-full text-center text-sm p-3 rounded-xl appearance-none cursor-pointer"
                  >
                    <option value="diabetes" className="bg-[#090a0f]">Diabetes</option>
                    <option value="heart" className="bg-[#090a0f]">Heart Disease</option>
                    <option value="mental" className="bg-[#090a0f]">Mental Health</option>
                  </select>
                </div>
                <div className="flex-1 text-left">
                  <label className="text-[10px] text-gray-500 uppercase tracking-widest block mb-2">Language</label>
                  <select
                    value={voiceLanguage}
                    onChange={(e) => setVoiceLanguage(e.target.value as any)}
                    className="glass-input w-full text-center text-sm p-3 rounded-xl appearance-none cursor-pointer"
                  >
                    <option value="en-IN" className="bg-[#090a0f]">English (IN)</option>
                    <option value="hi-IN" className="bg-[#090a0f]">Hindi (IN)</option>
                    <option value="en-US" className="bg-[#090a0f]">English (US)</option>
                  </select>
                </div>
              </div>

             {/* Example prompt */}
             <div className="w-full max-w-lg bg-white/5 border border-white/10 rounded-xl p-4 text-left">
               <p className="text-[10px] uppercase tracking-widest text-gray-500 mb-2">Example: What to say</p>
               {voiceDisease === 'diabetes' && (
                 <p className="text-sm text-gray-300 italic">"My glucose is 180, blood pressure 85, BMI 31, I'm 52 years old, insulin level 140, and I have 2 pregnancies"</p>
               )}
               {voiceDisease === 'heart' && (
                 <p className="text-sm text-gray-300 italic">"I'm 60 years old, male, typical angina, blood pressure 150, cholesterol 260, max heart rate 130"</p>
               )}
               {voiceDisease === 'mental' && (
                 <p className="text-sm text-gray-300 italic">"I am 28 years old female, family history yes, sleep 4 hours, stress level 9, social support 2"</p>
               )}
             </div>

             {/* Record button */}
             {!voiceResult && !voiceProcessing && (
               <div className="flex flex-col items-center gap-4 mt-2">
                 {!voiceRecording ? (
                   <motion.button
                     onClick={startVoiceDiagnosis}
                     whileHover={{ scale: 1.05 }}
                     whileTap={{ scale: 0.95 }}
                     className="relative w-28 h-28 rounded-full bg-gradient-to-br from-green-500/30 to-cyan-500/30 border-2 border-green-500/50 flex items-center justify-center hover:shadow-[0_0_40px_rgba(34,197,94,0.4)] transition-all duration-300 group"
                   >
                     <Mic className="w-12 h-12 text-green-400 group-hover:animate-pulse" />
                     <span className="absolute -bottom-8 text-xs text-gray-400 tracking-widest uppercase">Tap to Record</span>
                   </motion.button>
                 ) : (
                   <motion.button
                     onClick={stopVoiceDiagnosis}
                     animate={{ boxShadow: ['0 0 20px rgba(239,68,68,0.3)', '0 0 40px rgba(239,68,68,0.6)', '0 0 20px rgba(239,68,68,0.3)'] }}
                     transition={{ duration: 1.5, repeat: Infinity }}
                     className="relative w-28 h-28 rounded-full bg-gradient-to-br from-red-500/30 to-orange-500/30 border-2 border-red-500/50 flex items-center justify-center"
                   >
                     <Square className="w-10 h-10 text-red-400" />
                     <span className="absolute -bottom-8 text-xs text-red-400 tracking-widest uppercase animate-pulse">Recording...</span>
                   </motion.button>
                 )}
               </div>
             )}

             {/* Processing indicator */}
             {voiceProcessing && (
               <motion.div
                 initial={{ opacity: 0 }}
                 animate={{ opacity: 1 }}
                 className="flex flex-col items-center gap-4"
               >
                 <CyberAIWaveform isThinking={true} />
                 <p className="neon-text-green text-sm tracking-widest animate-pulse">PROCESSING VOICE WITH WAV2VEC2 + ML ENSEMBLE...</p>
               </motion.div>
             )}

             {/* Voice Result */}
             {voiceResult && !voiceResult.error && (
               <motion.div
                 initial={{ opacity: 0, y: 20 }}
                 animate={{ opacity: 1, y: 0 }}
                 className="w-full max-w-2xl space-y-4 text-left"
               >
                 {/* Transcription */}
                 <div className="bg-cyan-500/10 border border-cyan-500/20 rounded-xl p-4">
                   <p className="text-[10px] uppercase tracking-widest text-cyan-500/60 mb-1">Wav2Vec2 Transcription</p>
                   <p className="text-cyan-300 text-sm">{voiceResult.transcription}</p>
                   <p className="text-[10px] text-gray-600 mt-1">Model: {voiceResult.stt_model}</p>
                 </div>

                 {/* Extracted Parameters */}
                 <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                   <p className="text-[10px] uppercase tracking-widest text-gray-400 mb-3">Extracted Parameters</p>
                   <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                     {Object.entries(voiceResult.extraction?.parameters || {}).map(([key, val]: [string, any]) => (
                       <div key={key} className={`p-2 rounded-lg text-center text-xs ${
                         voiceResult.extraction?.defaults_used?.includes(key)
                           ? 'bg-yellow-500/10 border border-yellow-500/20 text-yellow-300'
                           : 'bg-green-500/10 border border-green-500/20 text-green-300'
                       }`}>
                         <span className="block text-[9px] uppercase tracking-wider text-gray-500">{key}</span>
                         <span className="font-bold text-lg">{typeof val === 'number' ? val.toFixed(val % 1 ? 1 : 0) : val}</span>
                         <span className="block text-[8px] text-gray-600">
                           {voiceResult.extraction?.defaults_used?.includes(key) ? 'auto-filled' : 'from voice'}
                         </span>
                       </div>
                     ))}
                   </div>
                   <p className="text-[10px] text-gray-500 mt-2">
                     Extraction confidence: {Math.round((voiceResult.extraction?.extraction_confidence || 0) * 100)}%
                   </p>
                 </div>

                 {/* Prediction Result */}
                 <div className={`rounded-xl p-5 border ${
                   voiceResult.prediction?.risk === 'High'
                     ? 'bg-red-500/10 border-red-500/30'
                     : voiceResult.prediction?.risk === 'Moderate'
                     ? 'bg-yellow-500/10 border-yellow-500/30'
                     : 'bg-green-500/10 border-green-500/30'
                 }`}>
                   <div className="flex justify-between items-center mb-3">
                     <div>
                       <p className="text-[10px] uppercase tracking-widest text-gray-400">Risk Assessment</p>
                       <p className={`text-3xl font-extrabold ${
                         voiceResult.prediction?.risk === 'High' ? 'text-red-400'
                         : voiceResult.prediction?.risk === 'Moderate' ? 'text-yellow-400'
                         : 'text-green-400'
                       }`}>{voiceResult.prediction?.risk}</p>
                     </div>
                     <div className="text-right">
                       <p className="text-[10px] uppercase tracking-widest text-gray-400">Confidence</p>
                       <p className="text-2xl font-bold text-white">{Math.round((voiceResult.prediction?.confidence || 0) * 100)}%</p>
                     </div>
                   </div>
                   <p className="text-xs text-gray-400 capitalize">Protocol: {voiceResult.prediction?.disease}</p>
                 </div>

                 {/* Abnormalities */}
                 {voiceResult.abnormalities?.length > 0 && (
                   <div className="bg-red-500/5 border border-red-500/20 rounded-xl p-4">
                     <p className="text-[10px] uppercase tracking-widest text-red-400 mb-2">Abnormalities Detected</p>
                     {voiceResult.abnormalities.map((a: string, i: number) => (
                       <p key={i} className="text-sm text-red-300/80 mb-1">- {a}</p>
                     ))}
                   </div>
                 )}

                 {/* Auto Medications */}
                 {voiceResult.auto_medications?.length > 0 && (
                   <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-4">
                     <p className="text-[10px] uppercase tracking-widest text-purple-400 mb-3">
                       {voiceResult.prescription_detected ? 'Prescription Analysis' : 'Auto-Suggested Medications'}
                     </p>
                     <div className="space-y-3">
                       {voiceResult.auto_medications.map((med: any, i: number) => (
                         <div key={i} className="bg-white/5 rounded-lg p-3 border border-white/5">
                           <div className="flex justify-between items-start">
                             <div>
                               <p className="text-white font-bold text-sm">{typeof med === 'object' ? String(med.name || 'Medication') : String(med)}</p>
                               <p className="text-cyan-400 text-xs font-mono">
                                 {typeof med === 'object' ? `${String(med.dosage || 'As prescribed')} — ${String(med.frequency || 'As directed')}` : ''}
                               </p>
                             </div>
                             <Pill size={16} className="text-purple-400 mt-1" />
                           </div>
                           {typeof med === 'object' && (med.note || med.purpose) && (
                             <p className="text-gray-400 text-[11px] mt-1">{String(med.note || med.purpose)}</p>
                           )}
                         </div>
                       ))}
                     </div>
                     <p className="text-[9px] text-gray-600 mt-3 italic">
                       Disclaimer: Auto-suggested medications are for informational purposes only. Always consult a healthcare professional.
                     </p>
                   </div>
                 )}

                 {/* Recommendations */}
                 {voiceResult.recommendations?.lifestyle?.length > 0 && (
                   <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                     <p className="text-[10px] uppercase tracking-widest text-gray-400 mb-2">Lifestyle Recommendations</p>
                     {voiceResult.recommendations.lifestyle.map((r: string, i: number) => (
                       <p key={i} className="text-sm text-gray-300 mb-1">- {r}</p>
                     ))}
                   </div>
                 )}

                 {/* Retry button */}
                 <button
                   onClick={() => setVoiceResult(null)}
                   className="w-full py-3 border border-[var(--neon-green)] text-[var(--neon-green)] rounded-xl hover:bg-[var(--neon-green)] hover:text-black font-bold transition-all duration-300"
                 >
                   NEW VOICE DIAGNOSIS
                 </button>
               </motion.div>
             )}

             {/* Error display */}
             {voiceResult?.error && (
               <div className="bg-red-900/30 border border-red-500/50 rounded-xl p-4 text-sm text-red-300 max-w-lg">
                 <p className="font-bold mb-1">Error</p>
                 <p>{voiceResult.error}</p>
                 <button onClick={() => setVoiceResult(null)} className="mt-3 text-xs text-red-400 underline">Try Again</button>
               </div>
             )}
           </div>
        ) : (
           <div className="glass-panel glowing-wrap p-8 text-center min-h-[450px]">
             <h1 className="text-3xl font-bold mb-8 neon-text-purple">VISUAL CORTEX UPLINK</h1>
             <ImageUpload 
               patientId={targetPatientId || undefined} 
               patientName={features.patientName} 
             />
           </div>
        )}
      </motion.div>
    </div>
  );
};

export default Diagnosis;
