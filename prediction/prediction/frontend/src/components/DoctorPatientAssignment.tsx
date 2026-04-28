import React, { useState, useEffect } from 'react';
import { Users, UserPlus, UserMinus, Search, Loader2, X, AlertTriangle, FileText, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

interface Patient {
  patient_id: string;
  patient_name: string;
  assigned_date?: string;
  predictions?: any[];
}

interface DoctorPatientAssignmentProps {
  userRole: 'doctor' | 'admin';
  userId?: string;
}

const DoctorPatientAssignment: React.FC<DoctorPatientAssignmentProps> = ({ userRole, userId }) => {
  const [assignedPatients, setAssignedPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [newPatientId, setNewPatientId] = useState('');
  const [newPatientName, setNewPatientName] = useState('');
  const [assigning, setAssigning] = useState(false);

  useEffect(() => {
    fetchData();
  }, [userRole, userId]);

  const fetchData = async () => {
    if (!userId) return;
    setLoading(true);
    try {
      const response = await fetch(`http://${window.location.hostname}:5000/api/doctor-patients?doctor_id=${userId}`);
      const result = await response.json();
      if (result.status === 'success') {
        setAssignedPatients(result.data);
      }
    } catch (error) {
      console.error('Fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const assignPatient = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId || !newPatientId || !newPatientName) return;

    setAssigning(true);
    try {
      const response = await fetch(`http://${window.location.hostname}:5000/api/assign-patient`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          doctor_id: userId,
          patient_id: newPatientId,
          patient_name: newPatientName
        })
      });

      const result = await response.json();
      if (result.status === 'success') {
        // Force refresh
        await fetchData();
        setShowAssignModal(false);
        setNewPatientId('');
        setNewPatientName('');
      } else {
        alert(result.error || 'Identity Sync Failed');
      }
    } catch (error) {
       alert('System Error during Append');
    } finally {
      setAssigning(false);
    }
  };

  const unassignPatient = async (patientId: string) => {
    if (!userId || !window.confirm('PERMANENTLY DISCONNECT PATIENT FROM REGISTRY?')) return;
    try {
      await fetch(`http://${window.location.hostname}:5000/api/unassign-patient`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doctor_id: userId, patient_id: patientId })
      });
      fetchData();
    } catch (e) { console.error(e); }
  };

  const filteredPatients = assignedPatients.filter(p =>
    p.patient_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.patient_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="flex flex-col items-center gap-4">
          <Loader2 className="text-orange-500 animate-spin" size={40} />
          <p className="text-[10px] text-orange-500 font-black uppercase tracking-[0.3em]">Querying Master Registry...</p>
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      {/* HEADER SECTION: Ultra-Neon */}
      <div className="flex items-center justify-between border-l-4 border-orange-500 pl-6 py-2">
        <div>
            <h2 className="text-2xl font-black text-white uppercase tracking-tighter italic leading-none">Clinical Cohort</h2>
            <p className="text-[10px] text-white/40 uppercase mt-1 font-bold tracking-widest">Active Practitioner Records</p>
        </div>
        <button
          onClick={() => setShowAssignModal(true)}
          className="flex items-center gap-3 px-6 py-3 bg-orange-600 hover:bg-orange-400 text-black font-black rounded-xl transition-all shadow-[0_0_20px_rgba(234,88,12,0.3)] hover:shadow-[0_0_30px_rgba(234,88,12,0.5)] active:scale-95 uppercase tracking-widest text-xs"
        >
          <UserPlus size={18} strokeWidth={3} />
          Append Registry
        </button>
      </div>

      {/* SEARCH NODE: Force visibility */}
      <div className="relative group">
        <Search size={18} className="absolute left-6 top-1/2 -translate-y-1/2 text-orange-500" />
        <input
          type="text"
          className="w-full pl-16 pr-6 py-5 bg-black border-2 border-white/5 rounded-2xl text-white font-black placeholder:text-white/10 focus:outline-none focus:border-orange-500/50 transition-all shadow-inner"
          placeholder="ENTER PATIENT NAME OR NEURAL ID..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
      </div>

      {/* PATIENT GRID: Unified Data Source */}
      <div className="grid grid-cols-1 gap-4">
        <AnimatePresence>
          {filteredPatients.length > 0 ? (
            filteredPatients.map((patient) => (
              <motion.div 
                key={patient.patient_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="bg-black/40 border-l-2 border-white/10 p-6 rounded-r-2xl hover:bg-black/60 hover:border-orange-500 transition-all group relative overflow-hidden"
              >
                <div className="flex items-center justify-between relative z-10">
                  <div className="flex items-center gap-6">
                    <div className="w-14 h-14 rounded-2xl bg-orange-600 flex items-center justify-center text-black shadow-lg shadow-orange-900/20 group-hover:scale-110 transition-transform">
                      <Users size={24} strokeWidth={2.5} />
                    </div>
                    <div>
                      <Link 
                        to={`/history?search=${patient.patient_id}`}
                        className="text-lg font-black text-white uppercase tracking-tight hover:text-orange-400 transition-colors cursor-pointer flex items-center gap-2 group/name"
                      >
                        {patient.patient_name}
                        <FileText size={14} className="opacity-0 group-hover/name:opacity-100 transition-opacity" />
                      </Link>
                      <div className="flex items-center gap-4 mt-1.5">
                          <span className="text-[10px] text-white/30 font-mono font-bold uppercase tracking-widest bg-white/5 px-2 py-0.5 rounded">ID: {patient.patient_id.substring(0,10)}</span>
                          {patient.assigned_date && (
                              <span className="text-[10px] text-orange-500/60 font-bold uppercase tracking-widest flex items-center gap-1">
                                  <Calendar size={10} />
                                  Synced {new Date(patient.assigned_date).toLocaleDateString()}
                              </span>
                          )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                      {/* Dashboard Micro-Vitals */}
                      <div className="hidden sm:flex gap-2">
                        {patient.predictions?.slice(0, 3).map((p, i) => (
                             <div key={i} className="w-2 h-2 rounded-full bg-orange-500 shadow-[0_0_5px_rgba(234,88,12,0.5)]" />
                        ))}
                      </div>
                      <Link
                        to={`/diagnosis?patientName=${encodeURIComponent(patient.patient_name)}&patientId=${patient.patient_id}`}
                        className="flex items-center gap-2 px-3 py-1.5 bg-orange-500/10 border border-orange-500/30 text-orange-400 rounded-lg text-[10px] font-black uppercase tracking-widest hover:bg-orange-500 hover:text-black transition-all"
                      >
                        <Activity size={12} />
                        Initiate Scan
                      </Link>
                      <button
                        onClick={() => unassignPatient(patient.patient_id)}
                        className="p-3 text-white/20 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all"
                        title="Disconnect Identity"
                      >
                        <UserMinus size={20} />
                      </button>
                  </div>
                </div>
                <div className="absolute top-0 right-0 w-32 h-32 bg-orange-600/5 blur-[40px] pointer-events-none group-hover:bg-orange-600/10" />
              </motion.div>
            ))
          ) : (
            <div className="py-20 flex flex-col items-center justify-center border-2 border-dashed border-white/5 rounded-[3rem] opacity-20">
              <AlertTriangle size={48} className="mb-4 text-orange-500" />
              <p className="text-[10px] font-black uppercase tracking-[0.4em]">Zero Identities Anchored</p>
            </div>
          )}
        </AnimatePresence>
      </div>

      {/* MODAL: ULTRA-CONTRAST NEON BLACK */}
      <AnimatePresence>
        {showAssignModal && (
          <div className="fixed inset-0 bg-[#06070b]/95 backdrop-blur-xl flex items-center justify-center z-[999] px-6">
            <motion.div 
               initial={{ scale: 0.9, opacity: 0 }}
               animate={{ scale: 1, opacity: 1 }}
               exit={{ scale: 0.9, opacity: 0 }}
               className="bg-[#0a0c10] border-2 border-orange-500/30 rounded-[3rem] p-12 max-w-lg w-full shadow-[0_0_100px_rgba(234,88,12,0.15)] relative overflow-hidden"
            >
              <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-orange-600 via-orange-400 to-orange-600" />
              
              <div className="flex justify-between items-center mb-10">
                <div>
                   <h3 className="text-3xl font-black text-white uppercase tracking-tighter italic">Append Registry</h3>
                   <p className="text-[10px] text-orange-500 font-bold uppercase tracking-[0.2em] mt-1">Manual Identity Synchronization</p>
                </div>
                <button onClick={() => setShowAssignModal(false)} className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center text-white/40 hover:text-white transition-colors">
                  <X size={24} />
                </button>
              </div>

              <form onSubmit={assignPatient} className="space-y-8">
                {/* ID INPUT: Forced Visibility */}
                <div className="space-y-3">
                  <label className="text-[10px] font-black text-orange-500 uppercase tracking-[0.3em] ml-1">Unique Neural ID</label>
                  <input
                    type="text"
                    required
                    autoFocus
                    className="w-full bg-black border-2 border-white/10 rounded-2xl px-8 py-5 text-xl font-black text-orange-500 placeholder:text-white/5 focus:outline-none focus:border-orange-500 shadow-2xl transition-all"
                    placeholder="pat_xxxxxxxx"
                    value={newPatientId}
                    onChange={(e) => setNewPatientId(e.target.value)}
                  />
                </div>

                {/* NAME INPUT: Forced Visibility */}
                <div className="space-y-3">
                    <label className="text-[10px] font-black text-orange-500 uppercase tracking-[0.3em] ml-1">Clinical Register Name</label>
                    <input
                      type="text"
                      required
                      className="w-full bg-black border-2 border-white/10 rounded-2xl px-8 py-5 text-xl font-black text-orange-500 placeholder:text-white/5 focus:outline-none focus:border-orange-500 shadow-2xl transition-all"
                      placeholder="e.g. SAAREDI REDDY"
                      value={newPatientName}
                      onChange={(e) => setNewPatientName(e.target.value)}
                    />
                </div>

                <div className="grid grid-cols-2 gap-6 pt-6">
                  <button
                    type="button"
                    onClick={() => setShowAssignModal(false)}
                    className="py-5 bg-white/5 text-white font-black uppercase tracking-[0.2em] text-xs rounded-2xl hover:bg-white/10 transition-all"
                  >
                    Abort
                  </button>
                  <button
                    type="submit"
                    disabled={assigning}
                    className="bg-orange-600 hover:bg-orange-400 py-5 text-black font-black uppercase tracking-[0.2em] text-xs rounded-2xl transition-all shadow-xl shadow-orange-900/40 flex items-center justify-center gap-3"
                  >
                    {assigning ? <Loader2 className="animate-spin" size={18} /> : <UserPlus size={18} strokeWidth={3} />}
                    Sync Identity
                  </button>
                </div>
              </form>
              
              {/* Security Backdrop Pattern */}
              <div className="absolute -bottom-20 -right-20 w-64 h-64 bg-orange-600/5 rounded-full blur-[80px] pointer-events-none" />
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DoctorPatientAssignment;
