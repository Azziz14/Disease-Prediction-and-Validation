import os

path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\AdminDashboard.tsx"

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 1. Inject Advanced Admin Inbox Hooks and State
new_state_hooks = """  const [activeDoctorTab, setActiveDoctorTab] = useState<string | null>(null);

  // --- Unified Admin Inbox Refactoring ---
  const [activeTab, setActiveTab] = useState<'dashboard' | 'inbox'>('dashboard');
  const [selectedAdminThread, setSelectedAdminThread] = useState<{ id: string; name: string; role: 'doctor' | 'patient' } | null>(null);
  const [adminInboxHistory, setAdminInboxHistory] = useState<any[]>([]);
  const [adminInboxReply, setAdminInboxReply] = useState('');
  const [sendingInboxReply, setSendingInboxReply] = useState(false);

  const fetchAdminInboxHistory = React.useCallback(() => {
    if (!selectedAdminThread) return;
    if (selectedAdminThread.role === 'doctor') {
      fetch(`http://${window.location.hostname}:5000/api/chat/admin-messages?doctor_id=${selectedAdminThread.id}`)
        .then(res => res.json())
        .then(res => {
          if (res.status === 'success') {
            const mapped = (res.messages || []).map((m: any) => ({
              ...m,
              sender_id: m.sender === 'doctor' ? selectedAdminThread.id : 'admin',
              sender_name: m.sender === 'doctor' ? selectedAdminThread.name : 'PLATFORM ADMINISTRATOR'
            }));
            setAdminInboxHistory(mapped);
          }
        });
    } else {
      fetch(`http://${window.location.hostname}:5000/api/chat/history?user_a=${user?.id || 'admin'}&user_b=${selectedAdminThread.id}`)
        .then(res => res.json())
        .then(res => {
          if (res.status === 'success') setAdminInboxHistory(res.messages || []);
        });
    }
  }, [selectedAdminThread, user?.id]);

  useEffect(() => {
    let timer: NodeJS.Timeout | null = null;
    if (activeTab === 'inbox' && selectedAdminThread) {
      fetchAdminInboxHistory();
      timer = setInterval(fetchAdminInboxHistory, 5000);
    }
    return () => { if (timer) clearInterval(timer); };
  }, [activeTab, selectedAdminThread, fetchAdminInboxHistory]);

  const handleSendAdminInboxMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!adminInboxReply.trim() || !selectedAdminThread) return;
    setSendingInboxReply(true);
    try {
      if (selectedAdminThread.role === 'doctor') {
        await fetch(`http://${window.location.hostname}:5000/api/chat/send-message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            doctor_id: selectedAdminThread.id,
            sender: 'admin',
            sender_name: 'System Administrator',
            message: adminInboxReply
          })
        });
      } else {
        await fetch(`http://${window.location.hostname}:5000/api/chat/send-universal`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sender_id: user?.id || 'admin',
            recipient_id: selectedAdminThread.id,
            sender_name: 'System Administrator',
            sender_role: 'admin',
            recipient_role: 'patient',
            message: adminInboxReply
          })
        });
      }
      setAdminInboxReply('');
      fetchAdminInboxHistory();
    } catch(e) {
      console.error(e);
    }
    setSendingInboxReply(false);
  };
"""

content = content.replace("const [activeDoctorTab, setActiveDoctorTab] = useState<string | null>(null);", new_state_hooks)

# 2. Inject UI Tab Switcher at start of grid
header_end_target = """        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
          <Shield className="text-cyan-400" size={28} />
          System Administration
        </h1>
        <p className="text-sm text-white/50 mt-1">Welcome, {user?.name} — Full platform overview with patient analytics.</p>
      </div>"""

tabs_injection = header_end_target + """

      {/* UNIVERSAL SYNCHRONIZATION TABS */}
      <div className="flex gap-3 bg-white/[0.03] p-1.5 border border-white/5 rounded-2xl self-start inline-flex mb-6">
        <button 
          onClick={() => setActiveTab('dashboard')}
          className={`flex items-center gap-2.5 px-6 py-3 rounded-xl text-xs font-black uppercase tracking-wider transition-all ${
            activeTab === 'dashboard' 
              ? 'bg-cyan-600 text-white shadow-[0_0_20px_rgba(34,211,238,0.3)] border border-cyan-400/30' 
              : 'text-white/40 hover:text-white hover:bg-white/5 border border-transparent'
          }`}
        >
          <Activity size={15} />
          Intelligence Dashboard
        </button>
        <button 
          onClick={() => setActiveTab('inbox')}
          className={`flex items-center gap-2.5 px-6 py-3 rounded-xl text-xs font-black uppercase tracking-wider transition-all relative ${
            activeTab === 'inbox' 
              ? 'bg-cyan-600 text-white shadow-[0_0_20px_rgba(34,211,238,0.3)] border border-cyan-400/30' 
              : 'text-white/40 hover:text-white hover:bg-white/5 border border-transparent'
          }`}
        >
          <MessageSquare size={15} />
          Correspondence Inbox
          <div className="absolute -top-1.5 -right-1.5 w-2.5 h-2.5 rounded-full bg-cyan-500 shadow-[0_0_8px_cyan] animate-pulse" />
        </button>
      </div>

      {activeTab === 'dashboard' && (
        <>"""

content = content.replace(header_end_target, tabs_injection)

# 3. Inject closing tag for activeTab evaluation and the full UNIFIED ADMIN INBOX UI block before the Signal Modal
target_end_anchor = """        </div>
      </div>

      {/* ═══ SIGNAL MODAL ═══ */}"""

# Stunning Unified Inbox JSX for the Administration Suite
unified_admin_inbox_jsx = """        </div>
      </div>
      </>
      )}

      {activeTab === 'inbox' && (
        <motion.section initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-[2rem] border border-white/10 bg-[rgba(15,23,42,0.25)] p-8 backdrop-blur-xl shadow-[0_0_40px_rgba(0,243,255,0.02)]">
          <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-8">
            
            {/* Left Sidebar thread directory */}
            <div className="space-y-6 border-r border-white/5 pr-6">
              <div>
                <p className="text-[10px] font-black uppercase tracking-[0.25em] text-cyan-400/60">Central Command Mesh</p>
                <h3 className="text-xl font-black text-white uppercase tracking-tight italic mt-1">Secure Routing</h3>
              </div>

              <div className="space-y-4 overflow-y-auto max-h-[600px] custom-scrollbar">
                {/* ═══ Physicians Section ═══ */}
                <div>
                   <p className="text-[9px] font-black uppercase tracking-widest text-white/30 px-2 mb-2 flex items-center gap-1.5"><Stethoscope size={10} className="text-purple-400"/> Registered Physicians</p>
                   <div className="space-y-1.5">
                     {(data?.doctor_registry || []).map((doc: any) => (
                       <button 
                         key={doc.id}
                         onClick={() => setSelectedAdminThread({ id: doc.id, name: doc.name, role: 'doctor' })}
                         className={`w-full p-3 rounded-xl border transition-all text-left flex items-center gap-3 text-xs font-bold ${
                           selectedAdminThread?.id === doc.id 
                             ? 'bg-cyan-600/10 border-cyan-500/30 text-white shadow-lg' 
                             : 'bg-white/[0.02] border-white/5 text-white/50 hover:bg-white/[0.04]'
                         }`}
                       >
                          <div className={`w-2 h-2 rounded-full ${doc.performance_signal === 'red' ? 'bg-red-500' : 'bg-green-500'}`}/>
                          <span className="truncate">Dr. {doc.name}</span>
                       </button>
                     ))}
                   </div>
                </div>

                <div className="h-px bg-white/5 my-4" />

                {/* ═══ Patients Section ═══ */}
                <div>
                   <p className="text-[9px] font-black uppercase tracking-widest text-white/30 px-2 mb-2 flex items-center gap-1.5"><Users size={10} className="text-cyan-400"/> Registered Patients</p>
                   <div className="space-y-1.5">
                     {(data?.patients || []).map((pat: any) => (
                       <button 
                         key={pat.id}
                         onClick={() => setSelectedAdminThread({ id: pat.id, name: pat.name, role: 'patient' })}
                         className={`w-full p-3 rounded-xl border transition-all text-left flex items-center gap-3 text-xs font-bold ${
                           selectedAdminThread?.id === pat.id 
                             ? 'bg-cyan-600/10 border-cyan-500/30 text-white shadow-lg' 
                             : 'bg-white/[0.02] border-white/5 text-white/50 hover:bg-white/[0.04]'
                         }`}
                       >
                          <div className="w-2 h-2 bg-cyan-500/40 rounded-full" />
                          <span className="truncate">{pat.name}</span>
                       </button>
                     ))}
                   </div>
                </div>
              </div>
            </div>

            {/* Right Active Viewport Container */}
            <div className="bg-black/40 rounded-3xl border border-white/5 flex flex-col h-[600px] relative overflow-hidden">
              
              {/* Active Header */}
              <div className="p-6 border-b border-white/5 bg-white/[0.01] flex justify-between items-center">
                {selectedAdminThread ? (
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_8px_cyan]"/>
                    <div>
                      <h4 className="text-sm font-black text-white uppercase tracking-wider">
                         Direct Telemetry Conduit: {selectedAdminThread.role === 'doctor' ? `Dr. ${selectedAdminThread.name}` : selectedAdminThread.name}
                      </h4>
                      <p className="text-[9px] text-white/30 uppercase font-bold tracking-widest mt-0.5">
                         Operational Log Route • Role: {selectedAdminThread.role.toUpperCase()}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-white/20 rounded-full"/>
                    <span className="text-xs text-white/40 uppercase tracking-widest font-black">No route active. Select a node to initialize.</span>
                  </div>
                )}
              </div>

              {/* Chat Packet Logs */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar flex flex-col">
                {!selectedAdminThread ? (
                  <div className="flex flex-col items-center justify-center h-full text-center p-12 text-white/20">
                     <MessageSquare size={44} className="mb-4 animate-pulse text-cyan-500/40"/>
                     <p className="text-xs font-black uppercase tracking-widest">Awaiting Node Initialization</p>
                     <p className="text-[11px] mt-2">Select a registered practitioner or patient from the directory to pull historical sync logs.</p>
                  </div>
                ) : adminInboxHistory.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center text-white/20">
                     <MessageCircle size={36} className="mb-3 text-cyan-500/40"/>
                     <p className="text-[10px] font-black uppercase tracking-[0.2em]">Audit Log Clean</p>
                     <p className="text-[11px] mt-1">Type operational directives below to begin textual logging.</p>
                  </div>
                ) : (
                  adminInboxHistory.map((msg: any, idx: number) => {
                    const isMe = msg.sender === 'admin' || msg.sender_id === user?.id || msg.sender_role === 'admin';
                    return (
                      <div key={msg._id || idx} className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}>
                        <div className={`max-w-[75%] rounded-2xl p-4 border text-sm shadow-lg ${
                          isMe 
                            ? 'bg-cyan-600 border-cyan-500 text-black font-bold rounded-br-none' 
                            : 'bg-white/5 border-white/10 text-white rounded-bl-none'
                        }`}>
                          <p className="text-[8px] font-black uppercase tracking-widest opacity-50 mb-1.5">
                             {isMe ? 'SYSTEM COMMAND (YOU)' : msg.sender_name}
                          </p>
                          <p className="leading-relaxed font-medium">{msg.message}</p>
                        </div>
                        <span className="text-[8px] opacity-30 mt-1.5 font-mono px-2">
                           {new Date(msg.timestamp).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}
                        </span>
                      </div>
                    );
                  })
                )}
              </div>

              {/* Dispatch Input Control */}
              {selectedAdminThread && (
                <div className="p-4 border-t border-white/5 bg-black/20">
                  <form onSubmit={handleSendAdminInboxMessage} className="flex gap-3">
                    <input 
                      type="text"
                      value={adminInboxReply}
                      onChange={(e) => setAdminInboxReply(e.target.value)}
                      disabled={sendingInboxReply}
                      placeholder={`Submit command override/directive directly to user...`}
                      className="flex-1 bg-black/50 border border-white/10 rounded-2xl px-5 py-4 text-xs text-white placeholder:text-white/20 focus:outline-none focus:border-cyan-500/50 shadow-inner font-bold"
                    />
                    <button 
                      type="submit"
                      disabled={sendingInboxReply || !adminInboxReply.trim()}
                      className={`px-8 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all shadow-lg ${
                        sendingInboxReply || !adminInboxReply.trim() 
                          ? 'bg-white/5 border-white/5 text-white/20 cursor-not-allowed' 
                          : 'bg-cyan-600 border border-cyan-500 text-black active:scale-95 hover:bg-cyan-500'
                      }`}
                    >
                      {sendingInboxReply ? <Loader2 size={14} className="animate-spin"/> : <><Send size={12} className="inline mr-2"/> Send Directive</>}
                    </button>
                  </form>
                </div>
              )}
            </div>
          </div>
        </motion.section>
      )}

      {/* ═══ SIGNAL MODAL ═══ */}"""

content = content.replace(target_end_anchor, unified_admin_inbox_jsx)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: AdminDashboard.tsx fully modernized with a fully integrated Correspondence Inbox Tab!")
