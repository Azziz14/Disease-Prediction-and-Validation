import re

path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\AdminDashboard.tsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Step 1: Inject handleResolveFlag
handle_flag_block = """  const handleFlagDoctor = async () => {
    if (!flaggingDoctor || !flagReason.trim()) return;
    setSubmittingFlag(true);
    try {
      await fetch(`http://${window.location.hostname}:5000/api/flag-doctor`, {
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
      fetchDashboardData();
    } catch (e) {
      console.error(e);
    }
    setSubmittingFlag(false);
  };"""

handle_resolve_block = """  const handleFlagDoctor = async () => {
    if (!flaggingDoctor || !flagReason.trim()) return;
    setSubmittingFlag(true);
    try {
      await fetch(`http://${window.location.hostname}:5000/api/flag-doctor`, {
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
      fetchDashboardData();
    } catch (e) {
      console.error(e);
    }
    setSubmittingFlag(false);
  };

  const handleResolveFlag = async () => {
    if (!flaggingDoctor) return;
    setSubmittingFlag(true);
    try {
      await fetch(`http://${window.location.hostname}:5000/api/resolve-flag`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          doctor_id: flaggingDoctor,
          resolution_notes: 'Resolved and cleared by administrator override.',
          resolved_by: user?.name || 'admin'
        })
      });
      alert('Physician flag has been resolved successfully.');
      setFlaggingDoctor(null);
      setFlagReason('');
      fetchDashboardData();
    } catch (e) {
      console.error(e);
    }
    setSubmittingFlag(false);
  };"""

if handle_flag_block in content:
    content = content.replace(handle_flag_block, handle_resolve_block)
    print("1. Injected handleResolveFlag handler.")
else:
    print("ERROR: Could not find handleFlagDoctor block!")

# Step 2: Locate the modals blocks
# Let's locate signal modal and flag modal range
signal_modal_str = '{/* ═══ SIGNAL MODAL ═══ */}'
flag_modal_str = '{/* ═══ FLAG MODAL ═══ */}'
recent_log_str = '{/* ═══ RECENT PREDICTIONS LOG ═══ */}'

# Find the substring indices
signal_idx = content.find(signal_modal_str)
flag_idx = content.find(flag_modal_str)
recent_idx = content.find(recent_log_str)

if signal_idx != -1 and flag_idx != -1 and recent_idx != -1:
    # The modals container goes from signal_idx to recent_idx
    modals_content = content[signal_idx:recent_idx]
    
    # Erase them from original place
    content = content.replace(modals_content, "\n")
    print("2. Extracted and removed modals from original place.")
    
    # Construct new premium, hoisted modals block!
    new_modals_block = """      {/* ═══ SIGNAL MODAL (HOISTED) ═══ */}
      <AnimatePresence>
        {signalModal.open && (
          <div className="fixed inset-0 z-[99999] flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm overflow-y-auto">
            <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-[#0f172a] border border-white/10 rounded-2xl w-full max-w-md p-6 shadow-2xl relative">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Shield size={18} className="text-cyan-400" />
                  Set Performance Signal
                </h3>
                <button onClick={() => setSignalModal({ open: false, docId: '', docName: '', currentSignal: '' })} className="text-white/40 hover:text-white">✕</button>
              </div>
              <p className="text-xs text-white/50 mb-6">Updating audit performance metric for <strong className="text-white font-bold">Dr. {signalModal.docName}</strong>.</p>
              
              <div className="grid grid-cols-3 gap-3 mb-6">
                {['green', 'yellow', 'red'].map((sig) => (
                  <button
                    key={sig}
                    onClick={() => setSignalModal({ ...signalModal, currentSignal: sig })}
                    className={`py-3 rounded-xl font-black text-[10px] uppercase border transition-all tracking-widest flex items-center justify-center gap-2 ${
                      signalModal.currentSignal === sig 
                        ? sig === 'green' ? 'bg-green-600 border-green-400 text-white shadow-[0_0_15px_rgba(34,197,94,0.4)]' 
                          : sig === 'yellow' ? 'bg-yellow-600 border-yellow-400 text-black shadow-[0_0_15px_rgba(234,179,8,0.4)]' 
                          : 'bg-red-600 border-red-400 text-white shadow-[0_0_15px_rgba(239,68,68,0.4)]'
                        : 'bg-white/5 border-white/5 text-white/40 hover:bg-white/10'
                    }`}
                  >
                    <div className={`w-2 h-2 rounded-full ${sig === 'green' ? 'bg-green-400' : sig === 'yellow' ? 'bg-yellow-400' : 'bg-red-400'}`} />
                    {sig}
                  </button>
                ))}
              </div>
              
              <textarea
                className="w-full bg-black/40 border border-white/10 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-cyan-500 transition-all h-20 mb-5 placeholder:text-white/20"
                placeholder="Add permanent clinical note for signal update..."
                value={signalNote}
                onChange={(e) => setSignalNote(e.target.value)}
              />
              
              <button
                onClick={handleSetSignal}
                className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 text-white font-bold rounded-xl text-xs transition-all flex items-center justify-center gap-2 shadow-lg border border-cyan-400/30 mb-3"
              >
                Apply Audit Signal State
              </button>
              
              <p className="text-[9px] text-white/30 text-center italic">Visual updates propagate immediately to the staff console.</p>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ═══ FLAG MODAL (HOISTED WITH RESOLVE BUTTON) ═══ */}
      <AnimatePresence>
        {flaggingDoctor && (() => {
          const currentFlaggingDocObj = (data?.doctor_registry || []).find((d: any) => d.id === flaggingDoctor);
          const isCurrentlyFlagged = currentFlaggingDocObj?.is_flagged || false;
          
          return (
            <div className="fixed inset-0 z-[99999] flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm overflow-y-auto">
              <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-[#0f172a] border border-red-500/30 rounded-2xl w-full max-w-md p-6 shadow-2xl relative">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <AlertTriangle size={18} className="text-red-500 animate-pulse" />
                    {isCurrentlyFlagged ? 'Manage Active Physician Flag' : 'Flag Physician for Review'}
                  </h3>
                  <button onClick={() => setFlaggingDoctor(null)} className="text-white/40 hover:text-white">✕</button>
                </div>
                
                <p className="text-xs text-white/60 mb-5 leading-relaxed">
                  {isCurrentlyFlagged 
                    ? 'This practitioner currently has an ACTIVE high-priority warning flag. You can update the audit notes or resolve/clear this flag entirely.' 
                    : 'Place a formal warning directive flag on this practitioner dashboard for outstanding clinical audit inquiries.'
                  }
                </p>
                
                <div className="text-[10px] text-white/40 uppercase font-bold tracking-widest mb-2 px-1">Audit Reason Directive</div>
                <textarea 
                  className="w-full bg-black/40 border border-white/10 rounded-xl p-4 text-sm text-white focus:outline-none focus:border-red-500 transition-all h-28 mb-6 placeholder:text-white/20"
                  placeholder="Enter detailed justification for administrative flag..."
                  value={flagReason}
                  onChange={(e) => setFlagReason(e.target.value)}
                />
                
                <div className="space-y-3">
                  <button 
                    onClick={handleFlagDoctor}
                    disabled={submittingFlag}
                    className="w-full py-3.5 bg-red-600 hover:bg-red-500 text-white rounded-xl font-bold transition-all shadow-lg shadow-red-500/20 flex items-center justify-center gap-2 border border-red-500/40 text-sm"
                  >
                    {submittingFlag ? <Loader2 className="w-4 h-4 animate-spin" /> : <><AlertTriangle size={16}/> {isCurrentlyFlagged ? 'Update & Reactivate Flag' : 'Confirm Formal Flag'}</>}
                  </button>
                  
                  {isCurrentlyFlagged && (
                    <button 
                      onClick={handleResolveFlag}
                      disabled={submittingFlag}
                      className="w-full py-3 bg-emerald-600/10 hover:bg-emerald-600 border border-emerald-500/30 text-emerald-400 hover:text-white rounded-xl font-bold transition-all flex items-center justify-center gap-2 text-sm shadow-inner"
                    >
                      {submittingFlag ? <Loader2 className="w-4 h-4 animate-spin" /> : <><CheckCircle size={16}/> 🔓 Resolve Flag & Clear Record</>}
                    </button>
                  )}
                </div>
              </motion.div>
            </div>
          );
        })()}
      </AnimatePresence>
"""

    # Now insert new_modals_block right before the final closing tag at the bottom of the file!
    # We need to find the final "    </div>\n  );\n};\n\nexport default AdminDashboard;"
    final_closing_tag = "    </div>\n  );\n};\n\nexport default AdminDashboard;"
    if final_closing_tag in content:
        # Prepend block before the final closing div of return JSX
        final_replacement = new_modals_block + "\n    </div>\n  );\n};\n\nexport default AdminDashboard;"
        content = content.replace(final_closing_tag, final_replacement)
        print("3. Hoisted modals successfully to the absolute bottom of components!")
    else:
        # Fuzzy matching for ending
        print("WARN: Exact ending not found. Searching for final return close.")
        content = content.replace("\n    </div>\n  );\n};", "\n" + new_modals_block + "\n    </div>\n  );\n};")
        print("3. Fuzzy Hoisted modals successfully!")
        
else:
    print("ERROR: Could not isolate modal indexes!")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Refactoring finished.")
