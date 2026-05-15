import os
import re

path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\DoctorDashboard.tsx"

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 1. Add layoutDashboard, Lock and other icons to imports if missing
if 'LayoutDashboard,' not in content:
    content = content.replace('import { Search,', 'import { LayoutDashboard, Lock, Shield, MessageCircle,')

# 2. Inject state hooks for Tabs and Advanced Inbox
state_hooks = """  const [isListening, setIsListening] = useState(false);

  // --- Unified Dashboard Inbox Refactoring ---
  const [activeTab, setActiveTab] = useState<'overview' | 'inbox'>('overview');
  const [selectedThread, setSelectedThread] = useState<'admin' | string>('admin');
  const [assignedPatients, setAssignedPatients] = useState<any[]>([]);
  const [inboxHistory, setInboxHistory] = useState<any[]>([]);
  const [inboxReply, setInboxReply] = useState('');
  const [sendingInbox, setSendingInbox] = useState(false);

  const fetchAssignedPatients = React.useCallback(() => {
    if (!user?.id) return;
    fetch(`http://${window.location.hostname}:5000/api/doctor-patients?doctor_id=${user.id}`)
      .then(res => res.json())
      .then(res => {
        if (res.status === 'success') setAssignedPatients(res.data || []);
      })
      .catch(err => console.error("Inbox load error:", err));
  }, [user?.id]);

  const fetchInboxHistory = React.useCallback(() => {
    if (!user?.id) return;
    if (selectedThread === 'admin') {
      fetch(`http://${window.location.hostname}:5000/api/chat/admin-messages?doctor_id=${user.id}`)
        .then(res => res.json())
        .then(res => {
          if (res.status === 'success') {
            const mapped = (res.messages || []).map((m: any) => ({
              ...m,
              sender_id: m.sender === 'doctor' ? user.id : 'admin',
              sender_name: m.sender === 'doctor' ? `Dr. ${user.name}` : 'PLATFORM ADMINISTRATOR'
            }));
            setInboxHistory(mapped);
          }
        });
    } else {
      fetch(`http://${window.location.hostname}:5000/api/chat/history?user_a=${user.id}&user_b=${selectedThread}`)
        .then(res => res.json())
        .then(res => {
          if (res.status === 'success') setInboxHistory(res.messages || []);
        });
    }
  }, [user, selectedThread]);

  useEffect(() => {
    if (activeTab === 'inbox') {
      fetchAssignedPatients();
      fetchInboxHistory();
      const timer = setInterval(fetchInboxHistory, 6000);
      return () => clearInterval(timer);
    }
  }, [activeTab, selectedThread, fetchInboxHistory, fetchAssignedPatients]);

  const handleSendInbox = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inboxReply.trim() || !user?.id) return;
    setSendingInbox(true);
    try {
      if (selectedThread === 'admin') {
        await fetch(`http://${window.location.hostname}:5000/api/chat/send-message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            doctor_id: user.id,
            sender: 'doctor',
            sender_name: user.name || 'Doctor',
            message: inboxReply
          })
        });
      } else {
        await fetch(`http://${window.location.hostname}:5000/api/chat/send-universal`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sender_id: user.id,
            recipient_id: selectedThread,
            sender_name: `Dr. ${user.name || 'Physician'}`,
            sender_role: 'doctor',
            recipient_role: 'patient',
            message: inboxReply
          })
        });
      }
      setInboxReply('');
      fetchInboxHistory();
    } catch (e) {
      console.error(e);
    }
    setSendingInbox(false);
  };
"""

content = content.replace("const [isListening, setIsListening] = useState(false);", state_hooks)

# Remove the old chat polling effect to prevent duplicates
content = content.replace("""  // Poll secure messaging network every 8 seconds
  useEffect(() => {
    fetchChat();
    const interval = setInterval(fetchChat, 8000);
    return () => clearInterval(interval);
  }, [user]);""", "")

# 3. Locate the old Admin Chat section and EXTRACT it so we can completely delete it from the Overview layout!
old_chat_section_pattern = r"\{/\* SECURE ADMIN COMMUNICATION WORKSPACE \*/\}(.*?)</form>\s*</div>"
# Let's just cut it using string splitting to be absolutely sure we grab the exact text block
chat_start_anchor = "{/* SECURE ADMIN COMMUNICATION WORKSPACE */}"
chat_end_anchor = "</form>\n          </div>"
if chat_start_anchor in content:
    parts = content.split(chat_start_anchor)
    post_chat = parts[1].split(chat_end_anchor, 1)
    # Reconstruct content WITHOUT the old workspace
    content = parts[0] + post_chat[1]
    print("Successfully extracted and removed old bottom workspace!")

# 4. Inject tab buttons below the Header and wrap the Grid in dynamic tab evaluation
header_end_anchor = """      <div className="flex justify-between items-end">"""
# Wait! Let's find exactly where the header ends in the layout. Line 262 has: </div>\n      </div>
target_header_end = """          <div className="bg-white/5 border border-white/10 px-4 py-2 rounded-full flex items-center gap-3">
             <div className={`w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]`} />
             <span className="text-[10px] font-bold text-white/60 uppercase tracking-widest whitespace-nowrap">Live Clinical Sync</span>
          </div>
        </div>
      </div>"""

replacement_with_tabs = target_header_end + """

      {/* UNIVERSAL DASHBOARD SYNCHRONIZATION TABS */}
      <div className="flex gap-3 bg-white/[0.03] p-1.5 border border-white/5 rounded-2xl self-start inline-flex">
        <button 
          onClick={() => setActiveTab('overview')}
          className={`flex items-center gap-2.5 px-6 py-3 rounded-xl text-xs font-black uppercase tracking-wider transition-all ${
            activeTab === 'overview' 
              ? 'bg-orange-600 text-white shadow-[0_0_20px_rgba(234,88,12,0.3)] border border-orange-400/30' 
              : 'text-white/40 hover:text-white hover:bg-white/5 border border-transparent'
          }`}
        >
          <LayoutDashboard size={15} />
          Overview Cockpit
        </button>
        <button 
          onClick={() => setActiveTab('inbox')}
          className={`flex items-center gap-2.5 px-6 py-3 rounded-xl text-xs font-black uppercase tracking-wider transition-all relative ${
            activeTab === 'inbox' 
              ? 'bg-orange-600 text-white shadow-[0_0_20px_rgba(234,88,12,0.3)] border border-orange-400/30' 
              : 'text-white/40 hover:text-white hover:bg-white/5 border border-transparent'
          }`}
        >
          <MessageSquare size={15} />
          Communications Hub
          <div className="absolute -top-1.5 -right-1.5 w-2.5 h-2.5 rounded-full bg-orange-500 shadow-[0_0_8px_rgba(234,88,12,1)] animate-pulse" />
        </button>
      </div>

      {activeTab === 'overview' && ("""

content = content.replace(target_header_end, replacement_with_tabs)

# 5. Now close the Overview conditional and add the Inbox Tab content right at the end of the main grid!
# The main grid ends right before the layout close.
# Lines 441-443:
#       </div>
#     </div>
#   );
grid_end_anchor = """      </div>
    </div>
  );"""

# Advanced STUNNING Unified Inbox Template for Doctors
unified_inbox_jsx = """      )}

      {activeTab === 'inbox' && (
        <motion.section initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-[2rem] border border-white/10 bg-[rgba(15,23,42,0.35)] p-8 backdrop-blur-xl shadow-[0_0_40px_rgba(255,255,255,0.02)] animate-in fade-in duration-500">
          <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-8">
            
            {/* Sidebar thread navigation */}
            <div className="space-y-6 border-r border-white/5 pr-6">
              <div>
                <p className="text-[10px] font-black uppercase tracking-[0.25em] text-orange-500/60">Secure Telemetry Grid</p>
                <h3 className="text-xl font-black text-white uppercase tracking-tight italic mt-1">Correspondence</h3>
              </div>
              
              <div className="space-y-3 overflow-y-auto max-h-[500px] custom-scrollbar">
                <p className="text-[9px] font-black uppercase tracking-widest text-white/30 px-2">Administrative Nodes</p>
                {/* Central Command Thread */}
                <button 
                  onClick={() => setSelectedThread('admin')}
                  className={`w-full p-4 rounded-2xl border transition-all text-left relative flex items-center gap-3 ${
                    selectedThread === 'admin' 
                      ? 'bg-orange-600/10 border-orange-500/40 text-white shadow-lg' 
                      : 'bg-white/[0.02] border-white/5 text-white/50 hover:bg-white/[0.04]'
                  }`}
                >
                   <div className={`p-2.5 rounded-xl ${selectedThread === 'admin' ? 'bg-orange-600 text-black' : 'bg-white/5 text-white/30'}`}>
                     <Shield size={18} />
                   </div>
                   <div>
                     <p className="text-[9px] uppercase tracking-widest font-black opacity-60">System Network</p>
                     <p className="text-sm font-black tracking-tight mt-0.5 flex items-center gap-1.5">
                        Central Admin <Lock size={10} className="text-orange-500/60"/>
                     </p>
                   </div>
                </button>

                <div className="h-px bg-white/5 my-4" />
                <p className="text-[9px] font-black uppercase tracking-widest text-white/30 px-2">Active Ward Registry</p>
                {assignedPatients.length === 0 ? (
                  <p className="text-xs text-white/20 italic p-4">No bound telemetry records synced.</p>
                ) : (
                  assignedPatients.map((pat: any) => (
                    <button 
                      key={pat.patient_id}
                      onClick={() => setSelectedThread(pat.patient_id)}
                      className={`w-full p-4 rounded-2xl border transition-all text-left relative flex items-center gap-3 ${
                        selectedThread === pat.patient_id 
                          ? 'bg-orange-600/10 border-orange-500/40 text-white shadow-lg' 
                          : 'bg-white/[0.02] border-white/5 text-white/50 hover:bg-white/[0.04]'
                      }`}
                    >
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-black text-xs ${selectedThread === pat.patient_id ? 'bg-orange-600 text-black' : 'bg-white/5 text-white/40'}`}>
                         {pat.patient_name.charAt(0).toUpperCase()}
                      </div>
                      <div className="min-w-0 flex-1">
                         <p className="text-xs font-extrabold text-white truncate">{pat.patient_name}</p>
                         <p className="text-[9px] font-mono opacity-40 mt-0.5 uppercase">ID: {pat.patient_id.substring(0,8)}</p>
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>

            {/* Active Communication Viewport */}
            <div className="bg-black/40 rounded-3xl border border-white/5 flex flex-col h-[580px] relative shadow-2xl overflow-hidden">
              {/* Viewport Header */}
              <div className="p-6 border-b border-white/5 bg-white/[0.01] flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_green]"/>
                  <div>
                    <h4 className="text-sm font-black text-white uppercase tracking-wider">
                      {selectedThread === 'admin' ? 'Central Security Overrides' : `Clinical Wire: ${assignedPatients.find(p => p.patient_id === selectedThread)?.patient_name || 'Secure Node'}`}
                    </h4>
                    <p className="text-[9px] text-white/30 uppercase font-bold tracking-widest mt-0.5">
                      {selectedThread === 'admin' ? 'Administrative Audit-Logged Conduit' : 'Bi-Directional Clinical Synchronizer'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Logged Packets Container */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar flex flex-col">
                {inboxHistory.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center p-10 opacity-30">
                     <MessageCircle size={40} className="text-orange-400 mb-4 animate-pulse"/>
                     <p className="text-[10px] font-black uppercase tracking-[0.2em]">No Signals Extracted</p>
                     <p className="text-xs mt-2 font-medium">Enter text below to establish synchronization packet stream.</p>
                  </div>
                ) : (
                  inboxHistory.map((msg: any, index: number) => {
                    const isMe = msg.sender_id === user?.id;
                    return (
                      <div key={msg._id || index} className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}>
                        <div className={`max-w-[75%] rounded-2xl p-4 border text-sm shadow-lg ${
                          isMe 
                            ? 'bg-orange-600 border-orange-500 text-black font-bold rounded-br-none' 
                            : 'bg-white/5 border-white/10 text-white rounded-bl-none'
                        }`}>
                          <p className="text-[8px] font-black uppercase tracking-widest opacity-50 mb-1.5">
                            {isMe ? 'OPERATOR (YOU)' : msg.sender_name}
                          </p>
                          <p className="leading-relaxed">{msg.message}</p>
                        </div>
                        <span className="text-[8px] opacity-30 mt-1.5 px-2 font-mono">
                           {new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </span>
                      </div>
                    );
                  })
                )}
              </div>

              {/* Dispatch Input Console */}
              <div className="p-4 border-t border-white/5 bg-black/20">
                <form onSubmit={handleSendInbox} className="flex gap-3">
                  <input 
                    type="text"
                    value={inboxReply}
                    onChange={(e) => setInboxReply(e.target.value)}
                    disabled={sendingInbox}
                    className="flex-1 bg-black/50 border border-white/10 rounded-2xl px-5 py-4 text-xs text-white focus:outline-none focus:border-orange-500/50 placeholder:text-white/20 shadow-inner font-bold"
                    placeholder={selectedThread === 'admin' ? 'Submit operational inquiry to Admin...' : `Dispatch directive override to patient...`}
                  />
                  <button 
                    type="submit"
                    disabled={sendingInbox || !inboxReply.trim()}
                    className={`px-8 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all shadow-lg ${
                      sendingInbox || !inboxReply.trim() 
                        ? 'bg-white/5 border-white/5 text-white/20 cursor-not-allowed' 
                        : 'bg-orange-600 border border-orange-400 text-black active:scale-95 hover:bg-orange-500'
                    }`}
                  >
                    {sendingInbox ? <Loader2 size={14} className="animate-spin"/> : <><Send size={12} className="inline mr-2"/> Dispatch</>}
                  </button>
                </form>
              </div>
            </div>
          </div>
        </motion.section>
      )}

      </div>
    </div>
  );"""

content = content.replace(grid_end_anchor, unified_inbox_jsx)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: DoctorDashboard.tsx fully refactored to include a unified, stunning Inbox section!")
