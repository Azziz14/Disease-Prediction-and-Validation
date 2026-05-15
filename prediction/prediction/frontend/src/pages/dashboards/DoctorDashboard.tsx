import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Search, Loader2, Mic, Square, Bell, AlertCircle, CheckCircle, Send, MessageSquare, MessageCircle } from 'lucide-react';
import DoctorPatientAssignment from '../../components/DoctorPatientAssignment';
import { motion, AnimatePresence } from 'framer-motion';

const DoctorDashboard: React.FC = () => {
  const { user } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [isListening, setIsListening] = useState(false);

  // --- Unified Dashboard Inbox Refactoring ---
  const [activeTab, setActiveTab] = useState<'overview' | 'inbox'>('overview');
  const [selectedThread, setSelectedThread] = useState<'admin' | string>('admin');
  const [assignedPatients, setAssignedPatients] = useState<any[]>([]);
  const [inboxHistory, setInboxHistory] = useState<any[]>([]);
  const [inboxReply, setInboxReply] = useState('');
  const [sendingInbox, setSendingInbox] = useState(false);

  // Stable refs so polling interval never goes stale
  const selectedThreadRef = React.useRef(selectedThread);
  const userRef = React.useRef(user);
  React.useEffect(() => { selectedThreadRef.current = selectedThread; }, [selectedThread]);
  React.useEffect(() => { userRef.current = user; }, [user]);

  const BASE_URL = `${process.env.REACT_APP_API_URL || 'http://' + window.location.hostname + ':5000'}`;

  const fetchAssignedPatients = React.useCallback(() => {
    const u = userRef.current;
    if (!u?.id) return;
    fetch(`${BASE_URL}/api/doctor-patients?doctor_id=${u.id}`)
      .then(res => res.json())
      .then(res => {
        if (res.status === 'success') setAssignedPatients(res.data || []);
      })
      .catch(err => console.error("Patient list error:", err));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchInboxHistory = React.useCallback(() => {
    const u = userRef.current;
    const thread = selectedThreadRef.current;
    if (!u?.id) return;

    if (thread === 'admin') {
      fetch(`${BASE_URL}/api/chat/admin-messages?doctor_id=${u.id}`)
        .then(res => res.json())
        .then(res => {
          if (res.status === 'success') {
            const mapped = (res.messages || []).map((m: any) => ({
              ...m,
              sender_id: m.sender === 'doctor' ? u.id : 'admin',
              sender_name: m.sender === 'doctor' ? `Dr. ${u.name}` : 'PLATFORM ADMINISTRATOR'
            }));
            setInboxHistory(mapped);
          }
        });
    } else {
      fetch(`${BASE_URL}/api/chat/history?user_a=${u.id}&user_b=${thread}`)
        .then(res => res.json())
        .then(res => {
          if (res.status === 'success') setInboxHistory(res.messages || []);
        });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load patients on mount
  useEffect(() => {
    fetchAssignedPatients();
  }, [fetchAssignedPatients]);

  // Stable polling: only one interval, never recreated
  useEffect(() => {
    if (activeTab !== 'inbox') return;
    fetchInboxHistory();
    const timer = setInterval(fetchInboxHistory, 2000);
    return () => clearInterval(timer);
  }, [activeTab, fetchInboxHistory]);

  // Refresh history immediately when thread changes
  useEffect(() => {
    if (activeTab === 'inbox') {
      setInboxHistory([]);
      fetchInboxHistory();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedThread]);

  const handleSendInbox = async (e: React.FormEvent) => {
    e.preventDefault();
    const u = userRef.current;
    const thread = selectedThreadRef.current;
    if (!inboxReply.trim() || !u?.id) return;
    setSendingInbox(true);
    try {
      if (thread === 'admin') {
        await fetch(`${BASE_URL}/api/chat/send-message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            doctor_id: u.id,
            sender: 'doctor',
            sender_name: u.name || 'Doctor',
            message: inboxReply
          })
        });
      } else {
        await fetch(`${BASE_URL}/api/chat/send-universal`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sender_id: u.id,
            recipient_id: thread,
            sender_name: `Dr. ${u.name || 'Physician'}`,
            sender_role: 'doctor',
            recipient_role: 'patient',
            message: inboxReply
          })
        });
      }
      setInboxReply('');
      // Immediately fetch after send for instant feedback
      fetchInboxHistory();
    } catch (err) {
      console.error(err);
    } finally {
      setSendingInbox(false);
    }
  };

  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [inboxHistory]);

  useEffect(() => {
    fetch(`${process.env.REACT_APP_API_URL || 'http://' + window.location.hostname + ':5000'}/api/dashboard-data?role=doctor&user_id=${user?.id}`)
      .then(res => res.json())
      .then(res => {
        if(res.status === 'success') {
          setData(res.data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [user]);

  const clearNotifications = async () => {
    try {
      await fetch(`${process.env.REACT_APP_API_URL || 'http://' + window.location.hostname + ':5000'}/api/read-notifications`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ user_id: user?.id })
      });
      setData({ ...data, notifications: [] });
    } catch (e) {
      console.error(e);
    }
  };

  const handleSearch = async (e?: React.FormEvent, overrideQuery?: string) => {
    if (e) e.preventDefault();
    const query = overrideQuery || searchQuery;
    if (!query.trim()) return;
    
    setSearching(true);
    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL || 'http://' + window.location.hostname + ':5000'}/api/patient-history/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
      });
      const data = await res.json();
      setSearchResults(data.results || []);
    } catch (e) {
      console.error(e);
    }
    setSearching(false);
  };

  const startVoiceSearch = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event: any) => {
      const speechToText = event.results[0][0].transcript;
      setSearchQuery(speechToText);
      handleSearch(undefined, speechToText);
    };

    recognition.onerror = (event: any) => {
      console.error("Speech recognition error:", event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  if(loading) return <div className="text-white p-8">Loading Doctor Dashboard...</div>;

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in pb-20">
      <AnimatePresence>
        {data?.is_flagged && (
          <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-red-500 border border-red-400 rounded-2xl p-6 shadow-[0_0_30px_rgba(239,68,68,0.3)] mb-6">
            <div className="flex items-center gap-4">
              <div className="bg-white/20 p-3 rounded-xl">
                <AlertCircle className="text-white animate-pulse" size={32} />
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-black text-white uppercase tracking-tighter">System Flag Detected</h2>
                <p className="text-white/80 text-sm font-medium">Your account has been flagged for administrative review. Please audit your clinical directives immediately.</p>
              </div>
            </div>
            <div className="mt-4 bg-black/10 rounded-xl p-4 border border-white/10">
              <p className="text-[10px] text-white/50 uppercase font-bold mb-2">Flag Reason(s)</p>
              {data.active_flags?.map((flag: any, idx: number) => (
                <div key={idx} className="flex justify-between items-center text-white text-xs py-1">
                  <span>• {flag.reason}</span>
                  <span className="opacity-40 font-mono">{new Date(flag.date).toLocaleDateString()}</span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* --- CLINICAL ALERT CENTER (ADMIN PINGS) --- */}
      <AnimatePresence>
        {data?.notifications?.length > 0 && (
          <motion.div initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="bg-orange-500/10 border border-orange-500/30 rounded-2xl p-6 backdrop-blur-md">
            <div className="flex justify-between items-center mb-4">
               <div className="flex items-center gap-3">
                 <Bell className="text-orange-400 animate-bounce" size={20} />
                 <h2 className="text-lg font-bold text-white uppercase tracking-tight">Administrative Directive</h2>
               </div>
               <button onClick={clearNotifications} className="text-xs text-orange-400 font-bold hover:underline">Mark all as read</button>
            </div>
            <div className="space-y-3">
              {data.notifications.map((n: any, idx: number) => (
                <div key={idx} className="bg-white/5 p-4 rounded-xl border border-white/5 flex gap-4">
                  <AlertCircle size={18} className="text-orange-500 shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm text-white leading-relaxed">{n.message}</p>
                    <p className="text-[10px] text-white/30 mt-2 uppercase font-bold">{new Date(n.timestamp).toLocaleString()}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-black text-white tracking-tighter uppercase italic">
            Clinical Command Station
          </h1>
          <p className="text-sm text-white/50 mt-1">Lead Physician: <span className="text-orange-400 font-bold">Dr. {user?.name}</span> • Platform Rank: {user?.clinical_rank || 95}%</p>
          
          {/* PERFORMANCE SIGNAL DISPLAY */}
          <div className="mt-4 flex items-center gap-4">
            <div className={`px-4 py-1.5 rounded-xl border flex items-center gap-3 ${
              data?.performance_signal === 'red' ? 'bg-red-500/10 border-red-500/30' :
              data?.performance_signal === 'yellow' ? 'bg-yellow-500/10 border-yellow-500/30' :
              'bg-green-500/10 border-green-500/30'
            }`}>
              <div className={`w-2.5 h-2.5 rounded-full animate-pulse ${
                data?.performance_signal === 'red' ? 'bg-red-500 shadow-[0_0_10px_red]' :
                data?.performance_signal === 'yellow' ? 'bg-yellow-500 shadow-[0_0_10px_yellow]' :
                'bg-green-500 shadow-[0_0_10px_green]'
              }`} />
              <span className={`text-[10px] font-black uppercase tracking-[0.2em] ${
                data?.performance_signal === 'red' ? 'text-red-400' :
                data?.performance_signal === 'yellow' ? 'text-yellow-400' :
                'text-green-400'
              }`}>
                {data?.performance_signal || 'GREEN'} SIGNAL
              </span>
            </div>
            {data?.admin_signal_note && (
              <p className="text-xs text-white/40 italic">"{data.admin_signal_note}"</p>
            )}
          </div>
        </div>
        <div className="flex flex-col gap-3 items-end">
          <div className="bg-white/5 border border-white/10 px-4 py-2 rounded-full flex items-center gap-3">
             <div className={`w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]`} />
             <span className="text-[10px] font-bold text-white/60 uppercase tracking-widest whitespace-nowrap">Live Clinical Sync</span>
          </div>
          
          <div className="flex bg-black/40 rounded-xl p-1 border border-white/10">
            <button 
              onClick={() => setActiveTab('overview')}
              className={`px-6 py-2 rounded-lg text-sm font-bold transition-all ${
                activeTab === 'overview' 
                  ? 'bg-orange-600 text-white shadow-[0_0_15px_rgba(234,88,12,0.4)]' 
                  : 'text-white/40 hover:text-white'
              }`}
            >
              Overview
            </button>
            <button 
              onClick={() => setActiveTab('inbox')}
              className={`px-6 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${
                activeTab === 'inbox' 
                  ? 'bg-blue-600 text-white shadow-[0_0_15px_rgba(37,99,235,0.4)]' 
                  : 'text-white/40 hover:text-white'
              }`}
            >
              <MessageSquare size={16} />
              Communications Hub
            </button>
          </div>
        </div>
      </div>

      {activeTab === 'inbox' && (
        <section className="bg-[#1e293b]/40 border border-white/5 rounded-[2rem] p-8 shadow-2xl backdrop-blur-sm animate-in fade-in zoom-in-95 duration-500">
          <div className="flex items-center justify-between border-b border-white/5 pb-6 mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                <MessageCircle className="text-blue-400" />
                Communications Hub
              </h2>
              <p className="text-sm text-white/50 mt-1">Direct channel to platform administrators and patients.</p>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-white/40 uppercase tracking-widest">Active Thread:</span>
              <select 
                value={selectedThread}
                onChange={(e) => setSelectedThread(e.target.value)}
                className="bg-black/40 border border-blue-500/30 text-white text-sm rounded-xl px-4 py-2 focus:outline-none focus:border-blue-500"
              >
                <option value="admin" className="bg-[#0f172a]">🛡️ Platform Admin</option>
                <optgroup label="Your Patients" className="bg-[#0f172a]">
                  {assignedPatients.map(p => (
                    <option key={p.patient_id || p.id} value={p.patient_id || p.id} className="bg-[#0f172a]">👤 {p.patient_name || p.name}</option>
                  ))}
                </optgroup>
              </select>
            </div>
          </div>

          <div className="bg-black/40 border border-white/5 rounded-2xl h-[500px] flex flex-col overflow-hidden">
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {inboxHistory.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-white/20">
                  <MessageSquare size={48} className="mb-4 opacity-20" />
                  <p className="text-sm">No messages in this thread yet.</p>
                  <p className="text-xs mt-2 opacity-60">Messages refresh every 4 seconds automatically.</p>
                </div>
              ) : (
                inboxHistory.map((msg, idx) => {
                  const isMe = msg.sender_id === user?.id || msg.sender === 'doctor';
                  return (
                    <div key={idx} className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}>
                      <span className="text-[10px] text-white/30 mb-1 px-2 uppercase tracking-widest">{msg.sender_name || (isMe ? `Dr. ${user?.name}` : 'Patient')}</span>
                      <div className={`px-4 py-3 rounded-2xl max-w-[80%] text-sm leading-relaxed ${isMe ? 'bg-blue-600 text-white rounded-br-none' : 'bg-white/10 text-white/90 rounded-bl-none'}`}>
                        {msg.message}
                      </div>
                      <span className="text-[9px] text-white/20 mt-1 px-2">
                        {new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                      </span>
                    </div>
                  );
                })
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="p-4 bg-white/5 border-t border-white/5">
              <form onSubmit={handleSendInbox} className="flex gap-3">
                <input
                  type="text"
                  value={inboxReply}
                  onChange={e => setInboxReply(e.target.value)}
                  placeholder={`Reply to ${selectedThread === 'admin' ? 'Admin' : 'Patient'}...`}
                  className="flex-1 bg-black/40 border border-white/10 rounded-xl px-4 text-white placeholder:text-white/30 focus:outline-none focus:border-blue-500"
                />
                <button
                  type="submit"
                  disabled={sendingInbox || !inboxReply.trim()}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-xl font-bold flex items-center gap-2"
                >
                  {sendingInbox ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                  Send
                </button>
              </form>
            </div>
          </div>
        </section>
      )}

      {activeTab === 'overview' && (

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          {/* Semantic Search */}
          <div className="bg-[#1e293b]/40 border border-white/5 rounded-[2rem] p-8 shadow-2xl backdrop-blur-sm">
            <h2 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
              <Search size={18} className="text-orange-400" />
              Intelligence Query Node
            </h2>
            <form onSubmit={handleSearch} className="flex gap-4">
              <input 
                type="text" 
                placeholder="Query patient repository via Neural-NLP..."
                className="flex-1 bg-black/40 border border-white/10 rounded-2xl px-6 py-4 text-white placeholder:text-white/20 focus:outline-none focus:border-orange-500/50 transition-all shadow-inner"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button
                type="button"
                onClick={startVoiceSearch}
                className={`w-14 h-14 rounded-2xl border flex items-center justify-center transition-all ${
                  isListening 
                    ? 'bg-red-500 text-white border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.3)]' 
                    : 'bg-white/5 text-white/40 border-white/10 hover:bg-white/10'
                }`}
              >
                {isListening ? <Square className="w-6 h-6 animate-pulse" /> : <Mic className="w-6 h-6" />}
              </button>
              <button 
                type="submit"
                disabled={searching}
                className="px-8 bg-orange-600 hover:bg-orange-500 text-white rounded-2xl font-bold transition-all shadow-lg shadow-orange-500/20 flex items-center gap-3 group"
              >
                {searching ? <Loader2 className="w-5 h-5 animate-spin"/> : <Search className="w-5 h-5 group-hover:scale-110 transition-transform"/>}
                Execute
              </button>
            </form>

            {/* Results */}
            {searchResults.length > 0 && (
              <div className="mt-8 space-y-4">
                {searchResults.map((res: any, idx: number) => (
                  <div key={idx} className="bg-black/40 p-5 rounded-2xl border border-white/5 flex justify-between items-center group hover:border-orange-500/30 transition-all">
                    <div className="flex items-center gap-4">
                       <div className="w-10 h-10 rounded-xl bg-orange-500/10 flex items-center justify-center text-orange-400 font-bold text-xs">
                         ID
                       </div>
                       <div>
                         <p className="text-white font-bold">{res.patient_name || res.patient_id}</p>
                         <p className="text-xs text-white/30 font-mono uppercase">{res.diagnosis}</p>
                       </div>
                    </div>
                    <Link 
                      to={`/history?search=${res.patient_id}`}
                      className="px-4 py-2 text-[10px] bg-white/5 hover:bg-white/10 text-white/60 font-bold uppercase tracking-widest rounded-lg transition-all"
                    >
                      View Dossier
                    </Link>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Doctor-Patient Assignment */}
          <div className="bg-[#1e293b]/40 border border-white/5 rounded-[2rem] p-8">
            <DoctorPatientAssignment userRole="doctor" userId={user?.id} />
          </div>
        </div>

        <div className="space-y-8">
          {/* Clinical Vitals Summary */}
          <div className="bg-orange-600 rounded-[2rem] p-8 shadow-2xl shadow-orange-900/20 relative overflow-hidden group">
            <div className="relative z-10">
              <h2 className="text-white/60 text-[10px] font-bold uppercase tracking-[0.2em] mb-4">Patient Throughput</h2>
              <p className="text-5xl font-black text-white italic">{data?.patients_count || 0}</p>
              <p className="text-white/80 text-sm mt-2 font-medium">Active Clinical Files</p>
              <div className="mt-8 pt-8 border-t border-white/20 flex justify-between items-center">
                 <div className="flex -space-x-3">
                   {[1,2,3,4].map(i => <div key={i} className="w-8 h-8 rounded-full border-2 border-orange-600 bg-white/20" />)}
                 </div>
                 <span className="text-[10px] text-white/50 font-bold">+12 this week</span>
              </div>
            </div>
            <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-white/10 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-1000" />
          </div>

          {/* Recent Records */}
          <div className="bg-[#1e293b]/40 border border-white/5 rounded-[2rem] p-8 backdrop-blur-sm">
            <h2 className="text-sm font-bold text-white/50 uppercase tracking-widest mb-6 border-b border-white/5 pb-4">Recent Transmissions</h2>
            <div className="space-y-4">
              {data?.recent_records?.slice(0,5).map((r: any, idx: number) => (
                <div key={idx} className="flex gap-4 items-start group cursor-pointer">
                  <div className={`mt-1.5 w-1.5 h-1.5 rounded-full shrink-0 ${r.flagged ? 'bg-red-500 shadow-[0_0_8px_red]' : 'bg-green-500'}`} />
                  <div>
                    <p className={`text-sm font-bold transition-colors ${r.flagged ? 'text-red-400' : 'text-white/80 group-hover:text-orange-400'}`}>{r.diagnosis || "Consultation"}</p>
                    <p className="text-[10px] text-white/30 uppercase mt-1">{new Date(r.date).toLocaleDateString()} • ID: {r.patient_id?.substring(0,8)}</p>
                  </div>
                </div>
              ))}
            </div>
            <button className="w-full mt-8 py-3 text-[10px] font-bold text-orange-400 uppercase tracking-widest bg-orange-500/5 hover:bg-orange-500/10 rounded-xl border border-orange-500/20 transition-all">Audit Full Stream</button>
          </div>
        </div>
      </div>
      )}
    </div>
  );
};

export default DoctorDashboard;
