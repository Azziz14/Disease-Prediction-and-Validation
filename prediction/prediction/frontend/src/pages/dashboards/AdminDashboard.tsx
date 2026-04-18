import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { 
  Users, Stethoscope, Activity, AlertTriangle, Shield, Heart, Brain, 
  Pill, ChevronDown, ChevronUp, Search
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

  useEffect(() => {
    fetch(`http://localhost:5000/api/dashboard-data?role=admin`)
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
  }, []);

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
    if (filterRisk !== 'all' && p.risk !== filterRisk) return false;
    if (filterDisease !== 'all' && p.disease !== filterDisease) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return p.name.toLowerCase().includes(q) || p.id.toLowerCase().includes(q) || p.doctor?.toLowerCase().includes(q);
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

      {/* ═══ RECENT PREDICTIONS LOG ═══ */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-5">
        <h2 className="text-sm font-bold text-white/70 uppercase tracking-widest mb-4">Recent ML Predictions Log</h2>
        <div className="space-y-1">
          {(data?.recent_predictions || []).map((p: any, i: number) => {
            const risk = RISK_CONFIG[p.risk] || RISK_CONFIG['Low'];
            return (
              <div key={i} className="flex items-center justify-between text-sm py-2.5 px-3 rounded-lg hover:bg-white/5 transition-colors">
                <span className="text-white/40 text-xs font-mono w-40">{new Date(p.timestamp).toLocaleString()}</span>
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
