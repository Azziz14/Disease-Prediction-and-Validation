import React, { useMemo, useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { usePatientData } from '../../hooks/usePatientData';
import AudioRecorder from '../../components/ui/AudioRecorder';
import FileUpload from '../../components/ui/FileUpload';
import InsightsPanel from '../../components/ui/InsightsPanel';
import PatientVoiceAssistant from '../../components/ui/PatientVoiceAssistant';
import {
  Activity,
  BrainCircuit,
  Clock,
  ChevronDown,
  ChevronUp,
  Download,
  Mic,
  Pill,
  Shield,
  ShieldAlert,
  Sparkles,
  Stethoscope,
  TrendingUp,
  UploadCloud,
  Waves,
  Send,
  Loader2,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';

const PatientDashboard: React.FC = () => {
  const { user } = useAuth();
  const { history } = usePatientData();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedDisease, setSelectedDisease] = useState('auto');
  const [activeInsight, setActiveInsight] = useState<any>(null);
  const [loadingAudio, setLoadingAudio] = useState(false);
  const [loadingScanner, setLoadingScanner] = useState(false);
  const [expandedLogId, setExpandedLogId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'diagnosis' | 'history' | 'feedback'>('dashboard');

  // Feedback State
  const [assignedDoctor, setAssignedDoctor] = useState<{ id: string; name: string } | null>(null);
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const [feedbackRating, setFeedbackRating] = useState(5);
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  const [feedbackStatus, setFeedbackStatus] = useState<{ type: 'success' | 'error', msg: string } | null>(null);

  useEffect(() => {
    // Fetch assigned doctor
    fetch(`http://${window.location.hostname}:5000/api/patient-assignment?patient_id=${user?.id}`)
      .then(res => res.json())
      .then(res => {
        if (res.status === 'success' && res.assigned) {
          setAssignedDoctor({ id: res.doctor_id, name: res.doctor_name });
        }
      })
      .catch(err => console.error('Failed to fetch assigned doctor:', err));
  }, [user]);

  const submitFeedback = async () => {
    if (!feedbackMessage.trim() || !assignedDoctor || !user?.id) {
      setFeedbackStatus({ type: 'error', msg: 'Missing submission requirements (ID or Message).' });
      return;
    }
    setSubmittingFeedback(true);
    setFeedbackStatus(null);
    try {
      const res = await fetch(`http://${window.location.hostname}:5000/api/submit-feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: user.id,
          patient_name: user.name,
          doctor_id: assignedDoctor.id,
          message: feedbackMessage,
          rating: feedbackRating
        })
      });
      const resData = await res.json();
      if (res.ok) {
        setFeedbackStatus({ type: 'success', msg: 'Feedback submitted successfully.' });
        setFeedbackMessage('');
        setFeedbackRating(5);
      } else {
        setFeedbackStatus({ type: 'error', msg: resData.error || 'Review failed (Server rejected submission).' });
      }
    } catch (e: any) {
      console.error('Feedback Submission Error:', e);
      setFeedbackStatus({ type: 'error', msg: `Network error: ${e.message || 'Check connection to backend server.'}` });
    }
    setSubmittingFeedback(false);
  };

  useEffect(() => {
    const fetchData = () => {
      // SMART POLLING: Only fetch if the window is currently visible to the user
      if (document.hidden) return;
      
      fetch(`http://${window.location.hostname}:5000/api/dashboard-data?role=patient&user_id=${user?.id}`)
        .then(res => res.json())
        .then(res => {
          if (res.status === 'success') {
            setData(res.data);
          }
        })
        .catch(err => {
          console.error('Poll Error:', err);
        })
        .finally(() => {
          setLoading(false);
        });
    };

    fetchData();
    // 30-second polling for real-time diagnostic sync (Only when tab is active)
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [user]);

  const handleAudio = async (blob: Blob) => {
    setLoadingAudio(true);
    setActiveInsight(null);
    const formData = new FormData();
    formData.append('audio', blob, 'recording.wav');
    formData.append('patient_id', user?.id || 'guest');
    formData.append('disease', selectedDisease);

    try {
      const res = await fetch(`http://${window.location.hostname}:5000/api/voice-diagnosis`, {
        method: 'POST',
        body: formData
      });
      
      const contentType = res.headers.get("content-type");
      if (!res.ok || !contentType || !contentType.includes("application/json")) {
        const text = await res.text();
        throw new Error(text || `Server responded with ${res.status}`);
      }

      const resultData = await res.json();
      if (resultData.status === 'success') {
        setActiveInsight(resultData);
        setActiveTab('dashboard'); // Auto-switch to see results
      } else {
        alert(`Error: ${resultData.error || 'Prediction failed.'}`);
      }
    } catch (e: any) {
      console.error(e);
      alert(`Diagnostic Error: ${e.message || 'Connection failure in voice processing service.'}`);
    } finally {
      setLoadingAudio(false);
    }
  };

  const handleImage = async (file: File) => {
    setLoadingScanner(true);
    setActiveInsight(null);
    const formData = new FormData();
    formData.append('image', file);
    formData.append('patient_id', user?.id || 'guest');

    try {
      const res = await fetch(`http://${window.location.hostname}:5000/api/upload-prescription`, {
        method: 'POST',
        body: formData
      });
      
      const contentType = res.headers.get("content-type");
      if (!res.ok || !contentType || !contentType.includes("application/json")) {
        const text = await res.text();
        throw new Error(text || `Server responded with ${res.status}`);
      }

      const resultData = await res.json();
      
      if (resultData.status === 'success') {
        setActiveInsight(resultData);
        setActiveTab('dashboard'); // Auto-switch to see results
      } else {
        alert(`Scanner Error: ${resultData.error || 'Failed to interpret image.'}`);
      }
    } catch (e: any) {
      console.error(e);
      alert(`Diagnostic Error: ${e.message || 'Network failure connecting to scanner service.'}`);
    } finally {
      setLoadingScanner(false);
    }
  };

  const predictions = useMemo(() => {
    const serverPredictions = data?.predictions || [];
    const serverRecords = data?.medical_records || [];
    
    // Simple unity of server-provided data
    const merged = [...serverPredictions, ...serverRecords];

    const seen = new Set<string>();
    return merged
      .filter((entry: any) => {
        const rowId = entry._id || entry.id || entry.timestamp || 'key';
        const key = `${rowId}|${entry.disease || entry.disease_type || ''}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      })
      .map((entry: any) => ({
        ...entry,
        id: entry._id || entry.id,
        timestamp: entry.timestamp || entry.date,
        risk: entry.risk || 'Low',
        confidence: typeof entry.confidence === 'number' ? entry.confidence : 0,
        disease: entry.disease || entry.disease_type || 'General',
        auto_medications: entry.auto_medications || entry.autoMedications || [],
        recommendations: entry.recommendations || {},
        clinical_narrative: entry.clinical_narrative || ""
      }))
      .sort((a: any, b: any) => {
        const timeA = new Date(a.timestamp).getTime();
        const timeB = new Date(b.timestamp).getTime();
        return (isNaN(timeB) ? 0 : timeB) - (isNaN(timeA) ? 0 : timeA);
      });
  }, [data]);

  const selectedLog = useMemo(
    () => predictions.find((entry: any) => (entry.id || entry.timestamp) === expandedLogId) || null,
    [predictions, expandedLogId]
  );
  const latestPrediction = activeInsight?.consensus_intelligence || activeInsight?.prediction || predictions[0];
  const latestRisk = latestPrediction?.risk || activeInsight?.prediction?.risk || 'No data';
  const latestConfidence = typeof (latestPrediction?.confidence || latestPrediction?.accuracy) === 'number'
    ? `${((latestPrediction?.confidence || latestPrediction?.accuracy) * 100).toFixed(1)}%`
    : 'Pending';
  const normalizedActive = useMemo(() => {
    if (!activeInsight) return null;
    return {
      ...activeInsight,
      recommendations: activeInsight.recommendations || activeInsight.consensus_intelligence?.directives || {},
      auto_medications: activeInsight.auto_medications || (activeInsight.prediction?.auto_medications) || []
    };
  }, [activeInsight]);

  const medicationCount = normalizedActive?.auto_medications?.length || 0;
  const recommendationCount = [
    ...(normalizedActive?.recommendations?.lifestyle || []),
    ...(normalizedActive?.recommendations?.medical || []),
    ...(normalizedActive?.recommendations?.precautions || [])
  ].length;

  const highRiskCount = useMemo(
    () => predictions.filter((entry: any) => entry.risk === 'High').length,
    [predictions]
  );

  const diseaseLabel = useMemo(() => {
    const mapping: Record<string, string> = {
      auto: 'Auto-detect',
      diabetes: 'Diabetes',
      heart: 'Heart',
      mental: 'Mental Health'
    };
    return mapping[selectedDisease] || selectedDisease;
  }, [selectedDisease]);

  const riskScore = (risk?: string) => {
    if (risk === 'High') return 3;
    if (risk === 'Moderate') return 2;
    return 1;
  };

  const trendData = useMemo(() => {
    return predictions.slice().reverse().map((p: any) => ({
      date: new Date(p.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
      risk: riskScore(p.risk),
      confidence: Math.round(p.confidence * 100)
    }));
  }, [predictions]);

  const downloadReport = async () => {
    const element = document.getElementById('clinical-print-template');
    if (!element) return;
    
    // Temporarily show the template for capture
    element.style.display = 'block';
    setLoading(true);

    try {
      const canvas = await html2canvas(element, { 
        scale: 2, 
        useCORS: true, 
        backgroundColor: '#ffffff' 
      });
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
      
      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
      pdf.save(`CarePredict_Report_${user?.name?.replace(/\s+/g, '_') || 'Guest'}_${new Date().toISOString().split('T')[0]}.pdf`);
    } catch (e) {
      console.error('PDF generation failed', e);
      alert('Failed to generate Professional PDF Report');
    } finally {
      element.style.display = 'none';
      setLoading(false);
    }
  };

  return (
    <div id="dashboard-report-content" className="max-w-7xl mx-auto space-y-8 animate-in fade-in pb-12 bg-[#020812] px-4 pt-4">
      
      {/* --- HIDDEN PROFESSIONAL PRINT TEMPLATE --- */}
      <div id="clinical-print-template" style={{ display: 'none', width: '800px', padding: '40px', backgroundColor: '#ffffff', color: '#000000', fontFamily: 'Arial, sans-serif' }}>
        <div style={{ borderBottom: '4px solid #000', paddingBottom: '20px', marginBottom: '30px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: '28px', fontWeight: 'bold', margin: 0, color: '#1a365d' }}>CAREPREDICT CLINICAL INTELLIGENCE</h1>
            <p style={{ fontSize: '12px', color: '#4a5568', margin: '5px 0' }}>Multi-Node Inference & Consensus Diagnostic Record</p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ backgroundColor: '#000', color: '#fff', padding: '5px 15px', fontWeight: 'bold', fontSize: '14px' }}>OFFICIAL RECORD</div>
            <p style={{ fontSize: '10px', marginTop: '5px' }}>Generated: {new Date().toLocaleString()}</p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px', marginBottom: '40px', backgroundColor: '#f7fafc', padding: '20px', borderRadius: '8px' }}>
          <div>
            <h3 style={{ fontSize: '10px', textTransform: 'uppercase', color: '#718096', margin: '0 0 5px 0' }}>Patient Information</h3>
            <p style={{ fontSize: '18px', fontWeight: 'bold', margin: '0 0 5px 0' }}>{user?.name}</p>
            <p style={{ fontSize: '12px', margin: 0 }}>Patient ID: <span style={{ fontWeight: 'bold' }}>#{activeInsight?.numeric_patient_id || '100452'}</span></p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <h3 style={{ fontSize: '10px', textTransform: 'uppercase', color: '#718096', margin: '0 0 5px 0' }}>Treating Physician</h3>
            <p style={{ fontSize: '16px', fontWeight: 'bold', margin: '0 0 5px 0' }}>{latestPrediction?.treating_doctor || 'Dr. Unified Intelligence'}</p>
            <p style={{ fontSize: '12px', margin: 0 }}>Serial No: {Math.random().toString(36).substr(2, 9).toUpperCase()}</p>
          </div>
        </div>

        <div style={{ marginBottom: '40px' }}>
          <h2 style={{ fontSize: '20px', borderBottom: '2px solid #edf2f7', paddingBottom: '10px', marginBottom: '15px' }}>Inference Summary</h2>
          <div style={{ display: 'flex', gap: '20px' }}>
            <div style={{ flex: 1, padding: '15px', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
              <p style={{ fontSize: '10px', textTransform: 'uppercase', color: '#718096' }}>Diagnostic Protocol</p>
              <p style={{ fontSize: '20px', fontWeight: 'bold', margin: '5px 0', textTransform: 'capitalize' }}>{latestPrediction?.disease || selectedDisease}</p>
            </div>
            <div style={{ flex: 1, padding: '15px', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
              <p style={{ fontSize: '10px', textTransform: 'uppercase', color: '#718096' }}>Risk Assessment</p>
              <p style={{ fontSize: '20px', fontWeight: 'bold', margin: '5px 0', color: latestRisk === 'High' ? '#e53e3e' : '#3182ce' }}>{latestRisk}</p>
            </div>
            <div style={{ flex: 1, padding: '15px', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
              <p style={{ fontSize: '10px', textTransform: 'uppercase', color: '#718096' }}>Consensus Confidence</p>
              <p style={{ fontSize: '20px', fontWeight: 'bold', margin: '5px 0' }}>{latestConfidence}</p>
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '30px' }}>
          <div>
            <h2 style={{ fontSize: '20px', borderBottom: '2px solid #edf2f7', paddingBottom: '10px', marginBottom: '15px' }}>Clinical Narrative</h2>
            <p style={{ fontSize: '14px', lineHeight: '1.6', color: '#2d3748' }}>
              {activeInsight?.recommendations?.summary || activeInsight?.clinical_narrative || activeInsight?.consensus_intelligence?.narrative || 'Scan interpreted via Neural Consensus. The multi-node handshake verifies current biometrics against trained model baselines and validated medical directives.'}
            </p>
            
            <h2 style={{ fontSize: '20px', borderBottom: '2px solid #edf2f7', paddingBottom: '10px', marginTop: '30px', marginBottom: '15px' }}>Directive Care Plan</h2>
            <ul style={{ paddingLeft: '20px', fontSize: '13px', lineHeight: '1.8' }}>
              {[
                ...(activeInsight?.recommendations?.lifestyle || []),
                ...(activeInsight?.recommendations?.daily_routine || []),
                ...(activeInsight?.recommendations?.medical || []),
                ...(activeInsight?.recommendations?.precautions || [])
              ].map((rec: any, i: number) => (
                <li key={i}>
                  {typeof rec === 'object' ? (
                    <span>
                      <strong>{String(rec.name || 'Unknown')}</strong> {rec.dosage ? `(${String(rec.dosage)})` : ''} - {String(rec.note || rec.purpose || rec.frequency || '')}
                    </span>
                  ) : String(rec)}
                </li>
              ))}
              {recommendationCount === 0 && <li>Maintain current clinical baseline and monitor daily vitals.</li>}
            </ul>
          </div>
          <div>
            <h2 style={{ fontSize: '20px', borderBottom: '2px solid #edf2f7', paddingBottom: '10px', marginBottom: '15px' }}>Prescription Logic</h2>
            <div style={{ backgroundColor: '#fdf2f2', padding: '15px', borderRadius: '8px', border: '1px solid #fed7d7' }}>
              <p style={{ fontSize: '10px', fontWeight: 'bold', color: '#c53030', textTransform: 'uppercase', marginBottom: '10px' }}>Attention: Medication Suggestions</p>
              {activeInsight?.auto_medications?.map((med: any, i: number) => (
                <div key={i} style={{ marginBottom: '10px' }}>
                  <p style={{ fontSize: '13px', fontWeight: 'bold', margin: 0 }}>{typeof med === 'object' ? String(med.name || 'Unknown') : String(med)}</p>
                  <p style={{ fontSize: '11px', margin: 0 }}>
                    {typeof med === 'object' ? `${String(med.dosage || 'As prescribed')} - ${String(med.frequency || 'As directed')}` : ''}
                  </p>
                </div>
              ))}
              {(activeInsight?.auto_medications?.length || 0) === 0 && <p style={{ fontSize: '12px' }}>No active medication changes suggested at this time.</p>}
            </div>
            
            {activeInsight?.prescription_image && (
              <div style={{ marginTop: '30px' }}>
                <h3 style={{ fontSize: '10px', textTransform: 'uppercase', color: '#718096', marginBottom: '10px' }}>Handwriting Evidence</h3>
                <img src={activeInsight.prescription_image} style={{ width: '100%', borderRadius: '8px', border: '1px solid #e2e8f0' }} alt="Prescription" />
              </div>
            )}
          </div>
        </div>

        <div style={{ marginTop: '60px', borderTop: '1px solid #e2e8f0', paddingTop: '20px', textAlign: 'center' }}>
          <p style={{ fontSize: '10px', color: '#a0aec0' }}>Disclaimer: This report is generated by an AI decision support system and should be reviewed by a human medical professional before clinical action is taken.</p>
          <p style={{ fontSize: '12px', fontWeight: 'bold', color: '#1a365d', marginTop: '10px' }}>Validated by CarePredict Core Consensus Engine</p>
        </div>
      </div>
      <section className="relative overflow-hidden rounded-[28px] border border-[rgba(0,243,255,0.18)] bg-[linear-gradient(135deg,rgba(2,8,18,0.88),rgba(8,14,30,0.78),rgba(10,42,52,0.42))] p-8 md:p-10 shadow-[0_0_45px_rgba(0,243,255,0.08)]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(0,243,255,0.12),transparent_32%),radial-gradient(circle_at_bottom_left,rgba(176,91,255,0.10),transparent_30%)]" />
        <div className="absolute -right-12 top-10 h-40 w-40 rounded-full border border-[rgba(0,243,255,0.12)] bg-[rgba(0,243,255,0.04)] blur-2xl" />
        <div className="absolute left-1/3 top-0 h-px w-32 bg-[linear-gradient(90deg,transparent,rgba(0,243,255,0.9),transparent)]" />

        <div className="relative z-10 grid gap-8 lg:grid-cols-[1.5fr_1fr]">
          <div className="space-y-5">
            <div className="inline-flex items-center gap-2 rounded-full border border-[rgba(0,243,255,0.22)] bg-[rgba(0,243,255,0.08)] px-4 py-2 text-[11px] font-bold uppercase tracking-[0.25em] text-cyan-200">
              <Sparkles size={14} className="text-[var(--neon-green)]" />
              Clinical Command Deck
            </div>

            <div>
              <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-white leading-[1.05]">
                Patient Intelligence,
                <span className="block bg-gradient-to-r from-[var(--neon-blue)] via-white to-[var(--neon-green)] bg-clip-text text-transparent">
                  Voice Copilot Enabled
                </span>
              </h1>
              <p className="mt-4 max-w-2xl text-sm md:text-base text-white/70 leading-relaxed">
                Welcome back, {user?.name}. <span className="text-cyan-400 font-bold ml-1">Patient ID: #{activeInsight?.numeric_patient_id || '100452'}</span>.
                This cockpit combines your trained-model prediction feed, voice-driven symptom intake, and a handwriting-aware clinical scanner.
              </p>
              
              <button 
                onClick={downloadReport}
                className="mt-6 inline-flex items-center gap-2 rounded-full border border-purple-500/40 bg-purple-500/10 px-5 py-2.5 text-sm font-semibold text-purple-200 transition-all hover:bg-purple-500/20 shadow-[0_0_15px_rgba(176,91,255,0.2)]"
              >
                <Download size={18} />
                Download PDF Clinical Report
              </button>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {[
                { label: 'Latest Risk', value: latestRisk, icon: ShieldAlert, accent: 'text-red-300' },
                { label: 'Confidence', value: latestConfidence, icon: TrendingUp, accent: 'text-cyan-200' },
                { label: 'Med Suggestions', value: String(medicationCount), icon: Pill, accent: 'text-purple-200' },
                { label: 'High-Risk History', value: String(highRiskCount), icon: Activity, accent: 'text-amber-200' }
              ].map((item) => (
                <div
                  key={item.label}
                  className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 backdrop-blur-md shadow-[inset_0_0_20px_rgba(255,255,255,0.03)]"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] uppercase tracking-[0.24em] text-white/45">{item.label}</span>
                    <item.icon size={16} className={item.accent} />
                  </div>
                  <p className="mt-3 text-2xl font-extrabold text-white">{item.value}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[24px] border border-[rgba(0,243,255,0.16)] bg-[rgba(5,10,18,0.72)] p-5 backdrop-blur-xl">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[10px] uppercase tracking-[0.22em] text-cyan-300/70">Live Session Context</p>
                <h2 className="mt-2 text-xl font-bold text-white">Inference Readiness</h2>
              </div>
              <Waves size={22} className="text-[var(--neon-blue)]" />
            </div>

            <div className="mt-5 space-y-4">
              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                <p className="text-[10px] uppercase tracking-[0.2em] text-white/45">Protocol</p>
                <p className="mt-2 text-lg font-semibold text-white">{diseaseLabel}</p>
                <p className="mt-1 text-sm text-white/60">Switch disease context before recording symptoms.</p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                <p className="text-[10px] uppercase tracking-[0.2em] text-white/45">Recommendations Loaded</p>
                <p className="mt-2 text-lg font-semibold text-white">{recommendationCount}</p>
                <p className="mt-1 text-sm text-white/60">Latest care-plan actions available for the assistant to explain.</p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                <p className="text-[10px] uppercase tracking-[0.2em] text-white/45">Prediction Feed</p>
                <p className="mt-2 text-lg font-semibold text-white">{predictions.length} records</p>
                <p className="mt-1 text-sm text-white/60">Historical outputs available for voice summaries and context-aware guidance.</p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                <p className="text-[10px] uppercase tracking-[0.2em] text-white/45">Daily Routine Focus</p>
                <div className="mt-2 space-y-1">
                  {[
                    ...(normalizedActive?.recommendations?.lifestyle || []),
                    ...(normalizedActive?.recommendations?.medical || []),
                    ...(normalizedActive?.recommendations?.precautions || [])
                  ].slice(0, 3).map((item: any, idx: number) => (
                    <p key={`focus-${idx}`} className="text-xs text-white/75 truncate">
                      - {typeof item === 'object' ? `${String(item.name || 'Care Plan')} (${String(item.dosage || 'Review')})` : String(item)}
                    </p>
                  ))}
                  {[
                    ...(normalizedActive?.recommendations?.lifestyle || []),
                    ...(normalizedActive?.recommendations?.medical || []),
                    ...(normalizedActive?.recommendations?.precautions || [])
                  ].length === 0 && (
                    <p className="text-xs text-white/55">Run a fresh diagnosis to generate your daily routine and exercise guidance.</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* --- TAB NAVIGATION --- */}
      <div className="flex gap-4 p-1 bg-white/5 border border-white/10 rounded-2xl w-fit mx-auto sticky top-4 z-[40] backdrop-blur-xl shadow-2xl">
        <button 
          onClick={() => setActiveTab('dashboard')}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold transition-all ${
            activeTab === 'dashboard' 
              ? 'bg-cyan-600 text-white shadow-[0_0_15px_rgba(6,182,212,0.4)]' 
              : 'text-white/40 hover:text-white hover:bg-white/5'
          }`}
        >
          <Activity size={18} />
          Clinical Dashboard
        </button>
        <button 
          onClick={() => setActiveTab('diagnosis')}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold transition-all ${
            activeTab === 'diagnosis' 
              ? 'bg-purple-600 text-white shadow-[0_0_15px_rgba(168,85,247,0.4)]' 
              : 'text-white/40 hover:text-white hover:bg-white/5'
          }`}
        >
          <BrainCircuit size={18} />
          New Diagnosis
        </button>
        <button 
          onClick={() => setActiveTab('history')}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold transition-all ${
            activeTab === 'history' 
              ? 'bg-amber-600 text-white shadow-[0_0_15px_rgba(245,158,11,0.4)]' 
              : 'text-white/40 hover:text-white hover:bg-white/5'
          }`}
        >
          <Clock size={18} />
          Clinical History
        </button>
        {assignedDoctor && (
          <button 
            onClick={() => setActiveTab('feedback')}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold transition-all ${
              activeTab === 'feedback' 
                ? 'bg-emerald-600 text-white shadow-[0_0_15px_rgba(16,185,129,0.4)]' 
                : 'text-white/40 hover:text-white hover:bg-white/5'
            }`}
          >
            <Shield size={18} />
            Physician Feedback
          </button>
        )}
      </div>

      {activeTab === 'diagnosis' && (
        <section className="rounded-[26px] border border-[rgba(0,243,255,0.16)] bg-[rgba(8,12,24,0.76)] p-6 backdrop-blur-xl shadow-[0_0_30px_rgba(0,243,255,0.05)] animate-in slide-in-from-bottom-4 duration-500">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-[10px] uppercase tracking-[0.2em] text-cyan-300/70">Voice-to-Model Pipeline</p>
              <h2 className="mt-2 text-2xl font-bold text-white">Symptom Capture Nexus</h2>
            </div>

            <div className="inline-flex items-center gap-2 rounded-full border border-[rgba(0,243,255,0.18)] bg-[rgba(0,243,255,0.08)] px-4 py-2 text-xs font-semibold text-cyan-100">
              <BrainCircuit size={14} />
              Active protocol: {diseaseLabel}
            </div>
          </div>

          <div className="mt-6 grid gap-6 lg:grid-cols-2">
            <div className="rounded-3xl border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02))] p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <Mic size={18} className="text-[var(--neon-blue)]" />
                    Voice Diagnosis
                  </h3>
                  <p className="mt-1 text-sm text-white/60">Capture symptoms and route them into the diagnostic pipeline.</p>
                </div>

                <select
                  value={selectedDisease}
                  onChange={(e) => setSelectedDisease(e.target.value)}
                  className="bg-black/40 border border-white/10 text-white text-sm rounded-xl px-3 py-2 focus:outline-none focus:border-cyan-500"
                >
                  <option value="auto" className="bg-[#090a0f]">Auto-detect</option>
                  <option value="diabetes" className="bg-[#090a0f]">Diabetes</option>
                  <option value="heart" className="bg-[#090a0f]">Heart Disease</option>
                  <option value="mental" className="bg-[#090a0f]">Mental Health</option>
                </select>
              </div>

              <div className="rounded-2xl border border-[rgba(0,243,255,0.14)] bg-black/20 p-3">
                <AudioRecorder onAudioReady={handleAudio} isProcessing={loadingAudio} />
              </div>
            </div>

            <div className="rounded-3xl border border-white/10 bg-[linear-gradient(180deg,rgba(176,91,255,0.08),rgba(255,255,255,0.02))] p-5">
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <UploadCloud size={18} className="text-[var(--neon-purple)]" />
                  Prescription Vision
                </h3>
                <p className="mt-1 text-sm text-white/60">Upload a prescription image and extract medications with OCR plus NLP.</p>
              </div>

              <FileUpload onFileSelect={handleImage} isProcessing={loadingScanner} label="Upload Prescription Image" accept="image/*" />
            </div>
          </div>
        </section>
      )}

      {activeTab === 'history' && (
        <section className="rounded-[26px] border border-[rgba(0,243,255,0.14)] bg-[rgba(9,12,22,0.72)] p-6 backdrop-blur-xl animate-in slide-in-from-bottom-4 duration-500">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between mb-8">
            <div>
              <p className="text-[10px] uppercase tracking-[0.2em] text-cyan-300/70">Historical Repository</p>
              <h2 className="mt-2 text-2xl font-bold text-white flex items-center gap-2">
                <Clock size={18} className="text-[var(--neon-blue)]" />
                Comprehensive History & Past Logs
              </h2>
            </div>
            <div className="px-4 py-2 bg-white/5 border border-white/10 rounded-full text-xs text-white/50">
              {predictions.length} Total Medical Events
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {predictions.map((p: any, i: number) => {
              const rowKey = p.id || p.timestamp || i;
              const isExpanded = expandedLogId === rowKey;
              const logMeds = (p.auto_medications || p.autoMedications || []);
              
              return (
                <div key={rowKey} className={`rounded-3xl border transition-all ${isExpanded ? 'border-cyan-500/40 bg-cyan-500/10' : 'border-white/10 bg-white/[0.02]'} p-6`}>
                   <div className="flex justify-between items-start mb-4">
                      <div>
                        <span className="text-[10px] text-white/30 uppercase tracking-widest">{new Date(p.timestamp).toLocaleDateString()}</span>
                        <h3 className="text-xl font-bold text-white capitalize mt-1">{p.disease} Diagnostic</h3>
                      </div>
                      <div className={`px-3 py-1 rounded-full text-[10px] font-bold ${p.risk === 'High' ? 'text-red-400 bg-red-400/10' : 'text-emerald-400 bg-emerald-400/10'}`}>
                        {p.risk} RISK
                      </div>
                   </div>
                   
                   <div className="flex gap-4 border-t border-white/5 pt-4">
                      <div className="flex flex-col">
                        <span className="text-[9px] text-white/40 uppercase">Confidence</span>
                        <span className="text-sm font-bold text-cyan-400">{(p.confidence * 100).toFixed(1)}%</span>
                      </div>
                      <button 
                        onClick={() => {
                          setExpandedLogId(isExpanded ? null : rowKey);
                          if(!isExpanded) setActiveInsight(p);
                        }}
                        className="ml-auto text-[10px] uppercase font-bold text-white/60 hover:text-white"
                      >
                        {isExpanded ? 'Minimize' : 'View Full Details'}
                      </button>
                   </div>

                   {isExpanded && (
                     <div className="mt-6 space-y-4 animate-in fade-in duration-300">
                        <div className="p-4 rounded-2xl bg-black/40 border border-white/5">
                           <p style={{ fontSize: '10px', text_cyan_300_50: 'rgba(34,211,238,0.5)', uppercase: 'uppercase', mb: '8px' }}>Narrative & AI Insight</p>
                           <p className="text-sm text-white/80 italic leading-relaxed">
                              {p.clinical_narrative || p.recommendations?.summary || p.consensus_intelligence?.narrative || "Model inference successful. No further narrative logged."}
                           </p>
                        </div>
                        {logMeds.length > 0 && (
                          <div className="space-y-2">
                             <p className="text-[10px] text-purple-300/50 uppercase">Directed Medications</p>
                              {logMeds.map((m: any, mi: number) => (
                                <div key={mi} className="flex justify-between text-xs p-2 bg-white/5 rounded-lg">
                                   <span className="text-white font-medium">{typeof m === 'object' ? String(m.name || 'Medication') : String(m)}</span>
                                   <span className="text-white/40">{typeof m === 'object' ? String(m.dosage || m.note || 'As directed') : ''}</span>
                                </div>
                              ))}
                          </div>
                        )}
                     </div>
                   )}
                </div>
              )
            })}
          </div>
        </section>
      )}

      {activeTab === 'feedback' && assignedDoctor && (
        <section className="max-w-2xl mx-auto rounded-[26px] border border-emerald-500/20 bg-emerald-500/5 p-8 backdrop-blur-xl animate-in slide-in-from-bottom-4 duration-500">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-emerald-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-emerald-500/30">
              <Stethoscope className="text-emerald-400" size={32} />
            </div>
            <h2 className="text-2xl font-bold text-white">Physician Performance Feedback</h2>
            <p className="text-sm text-white/50 mt-2">Providing feedback for <span className="text-emerald-400 font-bold">Dr. {assignedDoctor.name}</span></p>
          </div>

          <div className="space-y-6">
            <div className="bg-black/20 border border-white/5 rounded-2xl p-6 text-center">
              <h3 className="text-xs font-bold text-white/40 uppercase tracking-widest mb-4">Clinical Quality Rating</h3>
              <div className="flex justify-center gap-4">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setFeedbackRating(star)}
                    className={`transition-all ${feedbackRating >= star ? 'text-yellow-400 scale-125' : 'text-white/10 hover:text-white/30'}`}
                  >
                    <Sparkles size={32} fill={feedbackRating >= star ? 'currentColor' : 'none'} />
                  </button>
                ))}
              </div>
              <p className="mt-4 text-[10px] text-white/30 font-bold uppercase tracking-widest">
                {feedbackRating === 5 ? 'Excellent Care' : feedbackRating === 4 ? 'Good Experience' : feedbackRating === 3 ? 'Average Service' : feedbackRating === 2 ? 'Needs Improvement' : 'Unsatisfied'}
              </p>
            </div>

            <div className="bg-black/20 border border-white/5 rounded-2xl p-6">
              <h3 className="text-xs font-bold text-white/40 uppercase tracking-widest mb-4">Your Experience</h3>
              <textarea 
                value={feedbackMessage}
                onChange={(e) => setFeedbackMessage(e.target.value)}
                placeholder="Share your experience with the physician... Are you satisfied with the directives and medication suggestions?"
                className="w-full bg-transparent border-none text-white placeholder:text-white/10 focus:ring-0 resize-none h-40"
              />
            </div>

            {feedbackStatus && (
              <div className={`p-4 rounded-xl text-sm font-medium flex items-center gap-3 ${feedbackStatus.type === 'success' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
                {feedbackStatus.type === 'success' ? <CheckCircle size={18}/> : <AlertTriangle size={18}/>}
                {feedbackStatus.msg}
              </div>
            )}

            <button 
              onClick={submitFeedback}
              disabled={submittingFeedback || !feedbackMessage.trim()}
              className="w-full py-4 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:hover:bg-emerald-600 text-white rounded-2xl font-bold transition-all shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2"
            >
              {submittingFeedback ? <Loader2 className="w-5 h-5 animate-spin"/> : <><Send size={18}/> Submit Feedback to Admin</>}
            </button>

            <p className="text-[10px] text-white/30 text-center uppercase tracking-widest leading-relaxed">
              Your feedback is shared directly with the system administrators to ensure the highest quality of clinical care and physician accountability.
            </p>
          </div>
        </section>
      )}

      {activeTab === 'dashboard' && (
        <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
           <div className="grid grid-cols-1 xl:grid-cols-[1fr_1fr] gap-6">
            <div className="rounded-[26px] border border-[rgba(176,91,255,0.18)] bg-[rgba(11,12,25,0.78)] p-6 backdrop-blur-xl shadow-[0_0_30px_rgba(176,91,255,0.08)]">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-[10px] uppercase tracking-[0.2em] text-purple-300/70">Model Provenance</p>
                  <h2 className="mt-2 text-2xl font-bold text-white">Inference Intelligence</h2>
                </div>
                <Stethoscope size={20} className="text-[var(--neon-green)]" />
              </div>

              <div className="mt-6 space-y-4">
                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                  <p className="text-[10px] uppercase tracking-[0.2em] text-white/45">Requested Disease</p>
                  <p className="mt-2 text-lg font-semibold text-white">{latestPrediction?.disease || diseaseLabel}</p>
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                  <p className="text-[10px] uppercase tracking-[0.2em] text-white/45">Prediction Method</p>
                  <p className="mt-2 text-lg font-semibold text-white capitalize">
                    {activeInsight?.prediction?.model_metadata?.prediction_method?.replace(/_/g, ' ') || 'Awaiting live inference'}
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                    <p className="text-[10px] uppercase tracking-[0.2em] text-white/45">Best Model</p>
                    <p className="mt-2 text-base font-semibold text-white">
                      {activeInsight?.prediction?.model_metadata?.best_ml_model || 'Unavailable'}
                    </p>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                    <p className="text-[10px] uppercase tracking-[0.2em] text-white/45">Ensemble Accuracy</p>
                    <p className="mt-2 text-base font-semibold text-white">
                      {typeof activeInsight?.prediction?.model_metadata?.ensemble_accuracy === 'number'
                        ? `${(activeInsight.prediction.model_metadata.ensemble_accuracy * 100).toFixed(1)}%`
                        : 'Unavailable'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {normalizedActive && (
              <div className="animate-in fade-in zoom-in duration-300">
                <InsightsPanel predictionResult={normalizedActive} disease={normalizedActive?.prediction?.disease || selectedDisease} />
              </div>
            )}
          </div>

      {/* --- CLINICAL TRAJECTORY GRAPHS --- */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-[26px] border border-cyan-500/20 bg-cyan-500/5 p-6 backdrop-blur-xl">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-[10px] uppercase tracking-[0.2em] text-cyan-300/70">Bio-Metric Timeline</p>
              <h2 className="text-xl font-bold text-white">Condition Trajectory</h2>
            </div>
            <TrendingUp size={20} className="text-cyan-400" />
          </div>
          
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ffffff10" />
                <XAxis dataKey="date" stroke="#ffffff40" fontSize={10} tickLine={false} axisLine={false} />
                <YAxis hide domain={[0, 4]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#020617', border: '1px solid #1e293b', borderRadius: '12px', fontSize: '12px' }}
                  itemStyle={{ color: '#22d3ee' }}
                />
                <Area type="monotone" dataKey="risk" stroke="#22d3ee" fillOpacity={1} fill="url(#colorRisk)" strokeWidth={3} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <p className="mt-4 text-[11px] text-white/50 text-center uppercase tracking-widest">Risk Level Progression (Higher = Increased Severity)</p>
        </div>

        <div className="rounded-[26px] border border-purple-500/20 bg-purple-500/5 p-6 backdrop-blur-xl">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-[10px] uppercase tracking-[0.2em] text-purple-300/70">Metric Integrity</p>
              <h2 className="text-xl font-bold text-white">Consensus Confidence History</h2>
            </div>
            <ShieldAlert size={20} className="text-purple-400" />
          </div>
          
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ffffff10" />
                <XAxis dataKey="date" stroke="#ffffff40" fontSize={10} tickLine={false} axisLine={false} />
                <YAxis stroke="#ffffff40" fontSize={10} tickLine={false} axisLine={false} domain={[0, 100]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#020617', border: '1px solid #1e293b', borderRadius: '12px' }}
                />
                <Line type="stepAfter" dataKey="confidence" stroke="#a855f7" strokeWidth={3} dot={{ r: 4, fill: '#a855f7' }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="mt-4 text-[11px] text-white/50 text-center uppercase tracking-widest">AI Consensus Certainty Trend (%)</p>
        </div>
      </section>



      <PatientVoiceAssistant
        patientName={user?.name}
        predictions={predictions}
        activeInsight={activeInsight}
        selectedLog={selectedLog}
      />
        
        <section className="rounded-[26px] border border-[rgba(0,243,255,0.14)] bg-[rgba(9,12,22,0.72)] p-6 backdrop-blur-xl">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between mb-5">
            <div>
              <p className="text-[10px] uppercase tracking-[0.2em] text-cyan-300/70">Prediction Timeline</p>
              <h2 className="mt-2 text-2xl font-bold text-white flex items-center gap-2">
                <Clock size={18} className="text-[var(--neon-blue)]" />
                History & Past Logs
              </h2>
            </div>

            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-xs text-white/65">
              <Activity size={14} className="text-[var(--neon-green)]" />
              {predictions.length} events logged
            </div>
          </div>

          {predictions.length > 0 ? (
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
              {predictions.map((p: any, i: number) => (
                (() => {
                  const rowKey = p.id || p.timestamp || i;
                  const isExpanded = expandedLogId === rowKey;
                  const previousSameDisease = predictions
                    .filter((entry: any) => entry.disease === p.disease && (entry.id || entry.timestamp) !== rowKey)
                    .find((entry: any) => new Date(entry.timestamp || 0).getTime() < new Date(p.timestamp || 0).getTime());
                  const logMeds = (p.auto_medications && p.auto_medications.length > 0)
                    ? p.auto_medications
                    : (p.matched_drugs || []).map((name: string) => ({ name, dosage: 'Consult doctor', frequency: 'As prescribed' }));
                  const logLifestyle = p.recommendations?.lifestyle || [];
                  const logMedical = p.recommendations?.medical || [];
                  const logPrecautions = p.recommendations?.precautions || [];
                  const logUnsafeMeds = p.drug_interactions || [];
                  const rxDetails = p.prescription_evaluation?.details || [];
                  const hasDetails =
                    logMeds.length > 0 ||
                    logLifestyle.length > 0 ||
                    logMedical.length > 0 ||
                    logPrecautions.length > 0 ||
                    logUnsafeMeds.length > 0 ||
                    rxDetails.length > 0 ||
                    !!previousSameDisease;

                  return (
                <div
                  key={rowKey}
                  className={`relative overflow-hidden rounded-3xl border transition-all duration-300 ${
                    isExpanded ? 'border-cyan-500/40 bg-cyan-500/5' : 'border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))]'
                  } p-5`}
                >
                  <div className="relative z-10 flex items-start justify-between gap-4">
                    <div>
                      <p className="text-[10px] uppercase tracking-[0.2em] text-white/45">{(() => {
                        const d = new Date(p.timestamp);
                        return isNaN(d.getTime()) ? 'Awaiting Time' : d.toLocaleString();
                      })()}</p>
                      <h3 className="mt-2 text-xl font-semibold text-white capitalize">{p.disease} analysis</h3>
                    </div>

                    <div className={`rounded-2xl px-3 py-2 text-xs font-bold uppercase tracking-[0.18em] ${
                      p.risk === 'High'
                        ? 'bg-red-500/15 text-red-300 border border-red-400/20'
                        : p.risk === 'Moderate'
                          ? 'bg-amber-500/15 text-amber-200 border border-amber-300/20'
                          : 'bg-emerald-500/15 text-emerald-200 border border-emerald-300/20'
                    }`}>
                      {p.risk}
                    </div>
                  </div>

                  {hasDetails && (
                    <button
                      type="button"
                      onClick={() => {
                        setExpandedLogId(isExpanded ? null : rowKey);
                        // If expanding, also set as active insight to update the main panel
                        if (!isExpanded) {
                          setActiveInsight(p);
                        }
                      }}
                      className="relative z-10 mt-4 w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-[10px] uppercase tracking-widest font-bold text-white/60 hover:bg-white/10 transition-colors"
                    >
                      {isExpanded ? 'Hide Details' : 'View Full Clinical Log'}
                    </button>
                  )}

                  {isExpanded && hasDetails && (
                    <div className="relative z-10 mt-4 space-y-3 rounded-2xl border border-white/10 bg-black/40 p-4">
                      {logMeds.length > 0 && (
                        <div>
                          <p className="text-[10px] uppercase tracking-[0.2em] text-purple-300/80 mb-2">Medications</p>
                          <div className="flex flex-wrap gap-2">
                            {logMeds.map((med: any, idx: number) => (
                              <span key={idx} className="px-2 py-1 bg-white/5 border border-white/10 rounded text-[10px] text-white/70">
                                {typeof med === 'object' ? String(med.name || 'Medication') : String(med)}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between text-[10px] text-white/40">
                         <span className="uppercase tracking-widest font-bold">Confidence: {(p.confidence * 100).toFixed(1)}%</span>
                         <span className="italic">Dr. {p.treating_doctor}</span>
                      </div>
                    </div>
                  )}
                </div>
                  );
              })()
            ))}
            </div>
          ) : (
            <p className="text-white/50 text-sm">No predictions found.</p>
          )}
        </section>
      </div>
    )}
    </div>
  );
};

export default PatientDashboard;
