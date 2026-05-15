import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { 
  Users, Stethoscope, Activity, AlertTriangle, Shield, Heart, Brain, 
  Pill, ChevronDown, ChevronUp, Search, ShieldCheck, Mail, Send, Loader2, Sparkles
} from 'lucide-react';

const RISK_CONFIG: Record<string, { color: string; bg: string; border: string; glow: string }> = {
  'High':     { color: 'text-red-400',    bg: 'bg-red-500/15',    border: 'border-red-500/40',    glow: 'shadow-[0_0_12px_rgba(239,68,68,0.25)]' },
  'Moderate': { color: 'text-yellow-400', bg: 'bg-yellow-500/15', border: 'border-yellow-500/40', glow: 'shadow-[0_0_12px_rgba(234,179,8,0.2)]' },
  'Low':      { color: 'text-green-400',  bg: 'bg-green-500/15',  border: 'border-green-500/40',  glow: 'shadow-[0_0_12px_rgba(34,197,94,0.2)]' },
};

const DISEASE_ICONS: Record<string, React.ReactNode> = {
  diabetes: <Activity size={14} className="text-cyan-400" />,
  heart:    <Heart size={14} className="text-rose-400" />,
  mental:   <Brain size={14} className="text-purple-400" />,
};

const DISEASE_COLORS: Record<string, string> = {
  diabetes: '#22d3ee',
  heart:    '#f43f5e',
  mental:   '#a855f7',
};

const PIE_COLORS = ['#ef4444', '#eab308', '#22c55e'];

const AdminDashboard: React.FC = () => {
  const { user } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [expandedPatient, setExpandedPatient] = useState<string | null>(null);
  const [filterRisk, setFilterRisk] = useState<string>('all');
  const [filterDisease, setFilterDisease] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeDoctorTab, setActiveDoctorTab] = useState<string | null>(null);
  const [pingModal, setPingModal] = useState<{ open: boolean; docId: string; docName: string }>({ open: false, docId: '', docName: '' });
  const [pingMessage, setPingMessage] = useState('');
  const [sendingPing, setSendingPing] = useState(false);

  const [feedback, setFeedback] = useState<any[]>([]);
  const [flaggingDoctor, setFlaggingDoctor] = useState<string | null>(null);
  const [flagReason, setFlagReason] = useState('');
  const [submittingFlag, setSubmittingFlag] = useState(false);

  // Signal State
  const [signalModal, setSignalModal] = useState<{ open: boolean; docId: string; docName: string; currentSignal: string }>({ open: false, docId: '', docName: '', currentSignal: 'green' });
  const [signalNote, setSignalNote] = useState('');
  const [submittingSignal, setSubmittingSignal] = useState(false);

  const handleSendPing = async () => {
    if (!pingMessage.trim()) return;
    setSendingPing(true);
    try {
      await fetch(`${process.env.REACT_APP_API_URL || 'http://' + window.location.hostname + ':5000'}/api/send-ping`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          admin_id: user?.id,
          doctor_id: pingModal.docId,
          message: pingMessage
        })
      });
      alert(`Priority Ping sent to Dr. ${pingModal.docName}`);
      setPingModal({ open: false, docId: '', docName: '' });
      setPingMessage('');
    } catch (e) {
      console.error(e);
    }
    setSendingPing(false);
  };

  useEffect(() => {
    fetch(`${process.env.REACT_APP_API_URL || 'http://' + window.location.hostname + ':5000'}/api/dashboard-data?role=admin`)
      .then(res => res.json())
      .then(res => {
        if (res.status === 'success') {
          setData(res.data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });

    // Fetch Feedback
    fetch(`${process.env.REACT_APP_API_URL || 'http://' + window.location.hostname + ':5000'}/api/all-feedback`)
      .then(res => res.json())
      .then(res => {
        if (res.status === 'success') {
          setFeedback(res.data);
        }
      })
      .catch(err => console.error(err));
  }, []);

  const handleFlagDoctor = async () => {
    if (!flaggingDoctor || !flagReason.trim()) return;
    setSubmittingFlag(true);
    try {
      await fetch(`${process.env.REACT_APP_API_URL || 'http://' + window.location.hostname + ':5000'}/api/flag-doctor`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          doctor_id: flaggingDoctor,
          reason: flagReason,
          flagged_by: user?.name || 'admin'
        })
      });
      alert('Physician flagged successfully.');
      setFlaggingDoctor(null);
      setFlagReason('');
    } catch (e) {
      console.error(e);
    }
    setSubmittingFlag(false);
  };

  const handleSetSignal = async (signal: string) => {
    setSubmittingSignal(true);
    try {
      await fetch(`${process.env.REACT_APP_API_URL || 'http://' + window.location.hostname + ':5000'}/api/set-doctor-signal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          doctor_id: signalModal.docId,
          signal,
          admin_note: signalNote
        })
      });
      alert(`Performance signal updated to ${signal.toUpperCase()}`);
      setSignalModal({ ...signalModal, open: false });
      // Refresh data
      window.location.reload(); 
    } catch (e) {
      console.error(e);
    }
    setSubmittingSignal(false);
  };

  if (loading) return (
    <div className="flex items-center justify-center h-96">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-white/60 text-sm uppercase tracking-widest">Loading Admin Dashboard...</p>
      </div>
    </div>
  );

  const patients = data?.patients || [];
  
  // Filter patients
  const filteredPatients = patients.filter((p: any) => {
    // Risk filter: use .includes for flexibility (e.g. "High Risk Evaluation" matches "High")
    if (filterRisk !== 'all') {
      const pRisk = (p.risk || "").toLowerCase();
      const fRisk = filterRisk.toLowerCase();
      if (!pRisk.includes(fRisk)) return false;
    }
    
    // Disease filter: use .includes (e.g. "Heart Disease" matches "heart")
    if (filterDisease !== 'all') {
      const pDisease = (p.disease || "").toLowerCase();
      const fDisease = filterDisease.toLowerCase();
      if (!pDisease.includes(fDisease)) return false;
    }

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        (p.name || "").toLowerCase().includes(q) || 
        (p.id || "").toLowerCase().includes(q) || 
        (p.doctor || "").toLowerCase().includes(q)
      );
    }
    return true;
  });

  // Chart data
  const barData = [
    { name: 'Patients', count: data?.total_patients || 0, fill: '#22d3ee' },
    { name: 'Doctors', count: data?.total_doctors || 0, fill: '#a855f7' },
    { name: 'Predictions', count: data?.total_predictions || 0, fill: '#22c55e' },
  ];

  const riskPieData = data?.risk_distribution ? [
    { name: 'High', value: data.risk_distribution.High || 0 },
    { name: 'Moderate', value: data.risk_distribution.Moderate || 0 },
    { name: 'Low', value: data.risk_distribution.Low || 0 },
  ] : [];

  const diseasePieData = data?.disease_distribution ? 
    Object.entries(data.disease_distribution).map(([name, value]) => ({ name, value: value as number })) : [];

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
          <Shield className="text-cyan-400" size={28} />
          System Administration
        </h1>
        <p className="text-sm text-white/50 mt-1">Welcome, {user?.name} — Full platform overview with patient analytics.</p>
      </div>

      {/* ═══ STAT CARDS ═══ */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="bg-white/5 border border-white/10 rounded-xl p-5 text-center hover:border-cyan-500/30 transition-all duration-300">
          <Users size={20} className="text-cyan-400 mx-auto mb-2" />
          <p className="text-[10px] font-bold text-white/40 uppercase tracking-widest mb-1">Patients</p>
          <p className="text-3xl font-extrabold text-cyan-400">{data?.total_patients || 0}</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
          className="bg-white/5 border border-white/10 rounded-xl p-5 text-center hover:border-purple-500/30 transition-all duration-300">
          <Stethoscope size={20} className="text-purple-400 mx-auto mb-2" />
          <p className="text-[10px] font-bold text-white/40 uppercase tracking-widest mb-1">Doctors</p>
          <p className="text-3xl font-extrabold text-purple-400">{data?.total_doctors || 0}</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="bg-white/5 border border-white/10 rounded-xl p-5 text-center hover:border-green-500/30 transition-all duration-300">
          <Activity size={20} className="text-green-400 mx-auto mb-2" />
          <p className="text-[10px] font-bold text-white/40 uppercase tracking-widest mb-1">Predictions</p>
          <p className="text-3xl font-extrabold text-green-400">{data?.total_predictions || 0}</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
          className="bg-white/5 border border-white/10 rounded-xl p-5 text-center hover:border-red-500/30 transition-all duration-300">
          <AlertTriangle size={20} className="text-red-400 mx-auto mb-2" />
          <p className="text-[10px] font-bold text-white/40 uppercase tracking-widest mb-1">Critical Cases</p>
          <p className="text-3xl font-extrabold text-red-400">{data?.risk_distribution?.High || 0}</p>
        </motion.div>
      </div>

      {/* ═══ CHARTS ROW ═══ */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Bar Chart */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-5">
          <h2 className="text-sm font-bold text-white/70 uppercase tracking-widest mb-4">Platform Stats</h2>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ffffff15" />
                <XAxis dataKey="name" stroke="#ffffff40" fontSize={11} />
                <YAxis stroke="#ffffff40" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px', color: '#fff', fontSize: 12 }} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {barData.map((entry, idx) => <Cell key={idx} fill={entry.fill} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Pie Chart */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-5">
          <h2 className="text-sm font-bold text-white/70 uppercase tracking-widest mb-4">Risk Distribution</h2>
          <div className="h-48 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={riskPieData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                  {riskPieData.map((_: any, idx: number) => <Cell key={idx} fill={PIE_COLORS[idx]} />)}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px', color: '#fff', fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Disease Pie Chart */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-5">
          <h2 className="text-sm font-bold text-white/70 uppercase tracking-widest mb-4">Disease Distribution</h2>
          <div className="h-48 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={diseasePieData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                  {diseasePieData.map((entry: any, idx: number) => <Cell key={idx} fill={DISEASE_COLORS[entry.name] || '#888'} />)}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px', color: '#fff', fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* ═══ PATIENT RECORDS TABLE ═══ */}
      <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
        <div className="p-5 border-b border-white/10">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Users size={18} className="text-cyan-400" />
              Patient Records
              <span className="text-xs text-white/40 font-normal ml-2">({filteredPatients.length} of {patients.length})</span>
            </h2>
            
            <div className="flex items-center gap-3 flex-wrap">
              {/* Search */}
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  placeholder="Search patients..."
                  className="pl-9 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder:text-gray-600 focus:border-cyan-500/50 focus:outline-none transition-colors w-48"
                />
              </div>
              
              {/* Risk filter */}
              <select value={filterRisk} onChange={e => setFilterRisk(e.target.value)}
                className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white appearance-none cursor-pointer focus:border-cyan-500/50 focus:outline-none">
                <option value="all" className="bg-[#0a0a0f]">All Risks</option>
                <option value="High" className="bg-[#0a0a0f]">🔴 High</option>
                <option value="Moderate" className="bg-[#0a0a0f]">🟡 Moderate</option>
                <option value="Low" className="bg-[#0a0a0f]">🟢 Low</option>
              </select>

              {/* Disease filter */}
              <select value={filterDisease} onChange={e => setFilterDisease(e.target.value)}
                className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white appearance-none cursor-pointer focus:border-cyan-500/50 focus:outline-none">
                <option value="all" className="bg-[#0a0a0f]">All Diseases</option>
                <option value="diabetes" className="bg-[#0a0a0f]">🧬 Diabetes</option>
                <option value="heart" className="bg-[#0a0a0f]">❤️ Heart</option>
                <option value="mental" className="bg-[#0a0a0f]">🧠 Mental</option>
              </select>
            </div>
          </div>
        </div>

        {/* Patient list */}
        <div className="divide-y divide-white/5">
          {filteredPatients.map((patient: any) => {
            const risk = RISK_CONFIG[patient.risk] || RISK_CONFIG['Low'];
            const isExpanded = expandedPatient === patient.id;
            
            return (
              <motion.div key={patient.id} layout className="transition-colors duration-200 hover:bg-white/[0.02]">
                {/* Row header */}
                <div 
                  className="flex items-center gap-4 px-5 py-4 cursor-pointer"
                  onClick={() => setExpandedPatient(isExpanded ? null : patient.id)}
                >
                  {/* Risk indicator */}
                  <div className={`w-2 h-10 rounded-full ${risk.bg} ${risk.border} border`} />
                  
                  {/* Patient info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-white font-semibold text-sm">{patient.name}</span>
                      <span className="text-[10px] text-gray-500 font-mono">{patient.id}</span>
                    </div>
                    <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-500">
                      <span>{patient.age}y/{patient.gender}</span>
                      <span className="flex items-center gap-1">{DISEASE_ICONS[patient.disease]} {patient.disease}</span>
                      <span>{patient.doctor}</span>
                    </div>
                  </div>
                  
                  {/* Risk badge */}
                  <div className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${risk.bg} ${risk.border} ${risk.color} border ${risk.glow}`}>
                    {patient.risk}
                  </div>
                  
                  {/* Confidence */}
                  <div className="text-right hidden md:block">
                    <p className="text-xs text-gray-500">Confidence</p>
                    <p className="text-sm font-bold text-white">{Math.round(patient.confidence * 100)}%</p>
                  </div>

                  {/* Expand arrow */}
                  <div className="text-gray-500">
                    {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </div>
                </div>

                {/* Expanded details */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="overflow-hidden"
                    >
                      <div className="px-5 pb-5 pt-1 grid grid-cols-1 md:grid-cols-3 gap-4 ml-6">
                        {/* Vitals */}
                        <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                          <h4 className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mb-3">Vitals</h4>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-400">Glucose</span>
                              <span className={`font-bold ${patient.glucose > 180 ? 'text-red-400' : patient.glucose > 125 ? 'text-yellow-400' : 'text-green-400'}`}>
                                {patient.glucose} mg/dL
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-400">Blood Pressure</span>
                              <span className={`font-bold ${patient.bloodPressure > 140 ? 'text-red-400' : patient.bloodPressure > 130 ? 'text-yellow-400' : 'text-green-400'}`}>
                                {patient.bloodPressure} mmHg
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-400">BMI</span>
                              <span className={`font-bold ${patient.bmi > 30 ? 'text-red-400' : patient.bmi > 25 ? 'text-yellow-400' : 'text-green-400'}`}>
                                {patient.bmi}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-400">Last Visit</span>
                              <span className="font-bold text-white/70">{patient.last_visit}</span>
                            </div>
                          </div>
                        </div>

                        {/* Prescribed Medicines */}
                        <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                          <h4 className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mb-3 flex items-center gap-2">
                            <Pill size={12} className="text-cyan-400" /> Prescribed Medicines
                          </h4>
                          <div className="space-y-1.5">
                            {patient.prescribed_medicines?.map((med: string, i: number) => (
                              <div key={i} className="flex items-center gap-2 text-sm">
                                <span className="w-1.5 h-1.5 rounded-full bg-cyan-500 flex-shrink-0" />
                                <span className="text-cyan-300">{med}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Symptoms & Notes */}
                        <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                          <h4 className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mb-3">Symptoms</h4>
                          <div className="flex flex-wrap gap-1.5 mb-3">
                            {patient.symptoms?.map((s: string, i: number) => (
                              <span key={i} className="px-2 py-0.5 bg-white/5 border border-white/10 rounded-full text-[11px] text-gray-300">
                                {s}
                              </span>
                            ))}
                          </div>
                          <h4 className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mb-1 mt-3">Doctor Notes</h4>
                          <p className="text-xs text-gray-400 leading-relaxed italic">"{patient.notes}"</p>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            );
          })}
          
          {filteredPatients.length === 0 && (
            <div className="px-5 py-12 text-center">
              <p className="text-gray-500 text-sm">No patients match your filters.</p>
            </div>
          )}
        </div>
      </div>

      {/* ═══ CLINICAL STAFF HUB (ACCOUNTABILITY) ═══ */}
      <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
        <div className="p-5 border-b border-white/10 flex justify-between items-center">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Stethoscope size={18} className="text-purple-400" />
              Clinical Staff Registry (Accountability Hub)
            </h2>
            <div className="px-2 py-1 bg-purple-500/10 border border-purple-500/30 rounded text-[10px] text-purple-400 font-bold uppercase tracking-widest">
              Live Audit Active
            </div>
        </div>
        
        <div className="divide-y divide-white/5">
          {(data?.doctor_registry || []).map((doc: any) => (
            <div key={doc.id} className="transition-all">
              <div 
                className="p-5 flex items-center justify-between cursor-pointer hover:bg-white/[0.02]"
                onClick={() => setActiveDoctorTab(activeDoctorTab === doc.id ? null : doc.id)}
              >
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-xl ${doc.rank > 90 ? 'bg-green-500/20 text-green-400' : 'bg-orange-500/20 text-orange-400'}`}>
                    {doc.rank}
                  </div>
                  <div>
                    <h3 className="text-white font-bold">Dr. {doc.name}</h3>
                    <p className="text-xs text-white/40">{doc.email}</p>
                  </div>
                </div>

                <div className="flex items-center gap-8">
                  <div className="text-center">
                    <p className="text-[10px] text-white/40 uppercase font-bold mb-1">Status</p>
                    <div className="flex justify-center">
                      <div className={`w-3 h-3 rounded-full ${
                        doc.performance_signal === 'red' ? 'bg-red-500 shadow-[0_0_10px_red]' : 
                        doc.performance_signal === 'yellow' ? 'bg-yellow-500 shadow-[0_0_10px_yellow]' : 
                        'bg-green-500 shadow-[0_0_10px_green]'
                      }`} />
                    </div>
                  </div>
                  <button 
                    onClick={(e) => { e.stopPropagation(); setSignalModal({ open: true, docId: doc.id, docName: doc.name, currentSignal: doc.performance_signal }); setSignalNote(doc.admin_signal_note || ''); }}
                    className="p-2 rounded-lg bg-white/5 border border-white/10 text-white/60 hover:border-cyan-500/50 hover:text-cyan-400 transition-all"
                    title="Set Signal"
                  >
                    <Shield size={16} />
                  </button>
                  <button 
                    onClick={(e) => { e.stopPropagation(); setPingModal({ open: true, docId: doc.id, docName: doc.name }); }}
                    className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/20 transition-all"
                    title="Ping Doctor"
                  >
                    <Send size={16} />
                  </button>
                  <button 
                    onClick={(e) => { e.stopPropagation(); setFlaggingDoctor(doc.id); setFlagReason(`Administrative review for Dr. ${doc.name}`); }}
                    className="p-2 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/20 transition-all"
                    title="Flag Physician"
                  >
                    <AlertTriangle size={16} />
                  </button>
                  {activeDoctorTab === doc.id ? <ChevronUp size={16} className="text-white/20"/> : <ChevronDown size={16} className="text-white/20"/>}
                </div>
              </div>

              {activeDoctorTab === doc.id && (
                <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} className="bg-black/20 border-t border-white/5 overflow-hidden">
                  <div className="p-5">
                    <h4 className="text-xs font-bold text-white/40 uppercase tracking-widest mb-4">Assigned Patient Audit List</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {doc.patients.map((p: any) => (
                        <div key={p.id} className={`p-4 rounded-xl border flex items-center justify-between ${p.has_flags ? 'bg-red-500/10 border-red-500/30' : 'bg-white/5 border-white/10'}`}>
                          <div className="flex items-center gap-3">
                            <div className={`w-2 h-2 rounded-full ${p.has_flags ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`} />
                            <span className="text-sm font-medium text-white">{p.name}</span>
                          </div>
                          {p.has_flags && (
                            <span className="text-[10px] bg-red-500 text-white font-bold px-2 py-0.5 rounded uppercase flex items-center gap-1">
                              <AlertTriangle size={10} /> Wrong Prescription Detected
                            </span>
                          )}
                          {!p.has_flags && <span className="text-[10px] text-green-500 font-bold uppercase tracking-widest">Validated History</span>}
                        </div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* --- PING MODAL --- */}
      <AnimatePresence>
        {pingModal.open && (
           <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm">
             <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-[#0f172a] border border-cyan-500/30 rounded-2xl w-full max-w-md p-6 shadow-2xl">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xl font-bold text-white">Ping Dr. {pingModal.docName}</h3>
                  <button onClick={() => setPingModal({ open: false, docId: '', docName: '' })} className="text-white/40 hover:text-white">✕</button>
                </div>
                <p className="text-sm text-white/60 mb-4">Send a priority clinical directive or warning to this staff member. This will appear as a notification in their dashboard.</p>
                <textarea 
                  className="w-full bg-black/40 border border-white/10 rounded-xl p-4 text-white focus:outline-none focus:border-cyan-500 transition-all h-32 mb-6"
                  placeholder="e.g. Audit required for Patient Aarav Gupta. Neural Consensus flags unsafe medication mismatch."
                  value={pingMessage}
                  onChange={(e) => setPingMessage(e.target.value)}
                />
                <button 
                  onClick={handleSendPing}
                  disabled={sendingPing}
                  className="w-full py-4 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl font-bold transition-all shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2"
                >
                  {sendingPing ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <><Send size={18}/> Send Priority Directive</>}
                </button>
             </motion.div>
           </div>
        )}
      </AnimatePresence>

      {/* ═══ PATIENT FEEDBACK LOG ═══ */}
      <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
        <div className="p-5 border-b border-white/10">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Mail size={18} className="text-emerald-400" />
            Patient Feedback Stream
          </h2>
        </div>
        <div className="divide-y divide-white/5 max-h-[400px] overflow-y-auto">
          {feedback.map((f, i) => (
            <div key={i} className="p-5 hover:bg-white/[0.02] transition-colors flex justify-between items-start">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-white font-bold">{f.patient_name}</span>
                  <span className="text-[10px] text-white/30 uppercase tracking-widest">{new Date(f.timestamp).toLocaleString()}</span>
                </div>
                <div className="flex items-center gap-1 mb-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Sparkles 
                      key={star} 
                      size={10} 
                      className={f.rating >= star ? 'text-yellow-400' : 'text-white/10'} 
                      fill={f.rating >= star ? 'currentColor' : 'none'} 
                    />
                  ))}
                  <span className="text-[10px] text-white/30 ml-2 font-bold uppercase tracking-widest">{f.rating}/5</span>
                </div>
                <p className="text-sm text-white/70 leading-relaxed italic">"{f.message}"</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-[10px] text-white/40 uppercase font-bold">Regarding:</span>
                  <span className="text-xs text-cyan-400 font-bold">Dr. {f.doctor_name}</span>
                </div>
              </div>
              <button 
                onClick={() => { setFlaggingDoctor(f.doctor_id); setFlagReason(`Based on patient feedback: ${f.message.substring(0, 50)}...`); }}
                className="px-3 py-1.5 bg-red-500/10 border border-red-500/30 text-red-400 text-[10px] font-bold uppercase tracking-widest rounded-lg hover:bg-red-500/20 transition-all flex items-center gap-2"
              >
                <AlertTriangle size={12} /> Flag Physician
              </button>
            </div>
          ))}
          {feedback.length === 0 && (
            <div className="p-10 text-center text-white/30 text-sm italic">
              No patient feedback entries received yet.
            </div>
          )}
        </div>
      </div>

      {/* ═══ SIGNAL MODAL ═══ */}
      <AnimatePresence>
        {signalModal.open && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm">
            <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-[#0f172a] border border-cyan-500/30 rounded-2xl w-full max-w-md p-6 shadow-2xl">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-white">Performance Signal: Dr. {signalModal.docName}</h3>
                <button onClick={() => setSignalModal({ ...signalModal, open: false })} className="text-white/40 hover:text-white">✕</button>
              </div>
              
              <div className="grid grid-cols-3 gap-4 mb-6">
                {[
                  { id: 'green', label: 'Good', color: 'bg-green-500', shadow: 'shadow-green-500/40' },
                  { id: 'yellow', label: 'Warning', color: 'bg-yellow-500', shadow: 'shadow-yellow-500/40' },
                  { id: 'red', label: 'Critical', color: 'bg-red-500', shadow: 'shadow-red-500/40' }
                ].map((s) => (
                  <button
                    key={s.id}
                    onClick={() => handleSetSignal(s.id)}
                    className={`flex flex-col items-center gap-2 p-3 rounded-xl border transition-all ${
                      signalModal.currentSignal === s.id ? 'bg-white/10 border-white/40' : 'bg-black/20 border-white/5 hover:border-white/20'
                    }`}
                  >
                    <div className={`w-8 h-8 rounded-full ${s.color} ${s.shadow} shadow-lg`} />
                    <span className="text-[10px] font-bold uppercase tracking-widest text-white/60">{s.label}</span>
                  </button>
                ))}
              </div>

              <p className="text-[10px] uppercase tracking-widest text-white/40 font-bold mb-2">Administrative Note</p>
              <textarea 
                className="w-full bg-black/40 border border-white/10 rounded-xl p-4 text-white focus:outline-none focus:border-cyan-500 transition-all h-24 mb-6 text-sm"
                placeholder="Attach a reason or instruction for this signal change..."
                value={signalNote}
                onChange={(e) => setSignalNote(e.target.value)}
              />
              
              <p className="text-[10px] text-white/30 text-center italic">Select a color to update the physician's live performance signal.</p>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ═══ FLAG MODAL ═══ */}
      <AnimatePresence>
        {flaggingDoctor && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm">
            <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-[#0f172a] border border-red-500/30 rounded-2xl w-full max-w-md p-6 shadow-2xl">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-white">Flag Physician for Review</h3>
                <button onClick={() => setFlaggingDoctor(null)} className="text-white/40 hover:text-white">✕</button>
              </div>
              <p className="text-sm text-white/60 mb-4">You are placing a formal flag on this physician. This will appear on their dashboard as a high-priority warning.</p>
              <textarea 
                className="w-full bg-black/40 border border-white/10 rounded-xl p-4 text-white focus:outline-none focus:border-red-500 transition-all h-32 mb-6"
                placeholder="Reason for flagging..."
                value={flagReason}
                onChange={(e) => setFlagReason(e.target.value)}
              />
              <button 
                onClick={handleFlagDoctor}
                disabled={submittingFlag}
                className="w-full py-4 bg-red-600 hover:bg-red-500 text-white rounded-xl font-bold transition-all shadow-lg shadow-red-500/20 flex items-center justify-center gap-2"
              >
                {submittingFlag ? <Loader2 className="w-5 h-5 animate-spin" /> : <><AlertTriangle size={18}/> Confirm Formal Flag</>}
              </button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ═══ RECENT PREDICTIONS LOG ═══ */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-5">
        <h2 className="text-sm font-bold text-white/70 uppercase tracking-widest mb-4">Recent ML Predictions Log</h2>
        <div className="space-y-1">
          {(data?.recent_predictions || []).map((p: any, i: number) => {
            const risk = RISK_CONFIG[p.risk] || RISK_CONFIG['Low'];
            return (
              <div key={i} className="flex items-center justify-between text-sm py-2.5 px-3 rounded-lg hover:bg-white/5 transition-colors">
                <span className="text-white/40 text-xs font-mono w-40">{(() => {
                  const d = new Date(p.timestamp);
                  return isNaN(d.getTime()) ? 'Date N/A' : d.toLocaleString();
                })()}</span>
                <span className="flex items-center gap-2 text-white/70 capitalize">
                  {DISEASE_ICONS[p.disease]} {p.disease}
                </span>
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${risk.bg} ${risk.color} ${risk.border} border`}>
                  {p.risk}
                </span>
                <span className="text-white/50 text-xs">{Math.round(p.confidence * 100)}%</span>
                <span className="text-cyan-400 font-mono text-xs">{p.patient_id}</span>
                <span className="text-gray-600 text-[10px] uppercase">{p.input_method}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
