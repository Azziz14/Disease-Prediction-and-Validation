import re

path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\AdminDashboard.tsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Extract fetchDashboardData and update useEffect
# Search for the useEffect with two fetches
fetch_pattern = r'(useEffect\(\(\) => \{\s*fetch\(`http:\/\/\${window\.location\.hostname}:5000\/api\/dashboard-data\?role=admin`\)(?:\s|\S)*?\}\);)'
match = re.search(fetch_pattern, content)
if match:
    original_effect = match.group(1)
    print("[1] Found primary fetch useEffect.")
    
    # Reconstruct into separate function and a hook
    replacement_funcs = """  const fetchDashboardData = () => {
    fetch(`http://${window.location.hostname}:5000/api/dashboard-data?role=admin`)
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
    fetch(`http://${window.location.hostname}:5000/api/all-feedback`)
      .then(res => res.json())
      .then(res => {
        if (res.status === 'success') {
          setFeedback(res.data);
        }
      })
      .catch(err => console.error(err));
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);"""
    content = content.replace(original_effect, replacement_funcs)

# 2. Modify handleFlagDoctor to call fetchDashboardData()
flag_pattern = r'(const handleFlagDoctor = async \(\) => \{(?:\s|\S)*?setFlagReason\(\'\'\);\s*)(?:\s|\S)*?(\} catch \(e\))'
match = re.search(flag_pattern, content)
if match:
    print("[2] Found handleFlagDoctor.")
    content = content.replace(
        "alert('Physician flagged successfully.');\n      setFlaggingDoctor(null);\n      setFlagReason('');",
        "alert('Physician flagged successfully.');\n      setFlaggingDoctor(null);\n      setFlagReason('');\n      fetchDashboardData();"
    )

# 3. Modify handleSetSignal to remove reload and call fetchDashboardData()
signal_pattern = r'(const handleSetSignal = async \(signal: string\) => \{(?:\s|\S)*?alert\(.*?\);\s*setSignalModal.*?;\s*)(window\.location\.reload\(\);\s*)'
match = re.search(signal_pattern, content)
if match:
    print("[3] Found handleSetSignal.")
    content = content.replace("window.location.reload();", "fetchDashboardData();")

# 4. Merge Message/Ping buttons into Inbox tab navigation & Merge patient modal button
# Replace the buttons in the doctor registry grid
doctor_buttons_pattern = r'(<button \s*onClick=\{\(e\) => \{ e\.stopPropagation\(\); setPingModal.*?<\/button>)(?:\s|\S)*?(<button \s*onClick=\{\(e\) => \{ e\.stopPropagation\(\); setChatModal.*?<\/button>)'
match = re.search(doctor_buttons_pattern, content)
if match:
    print("[4] Found doctor registry inline message/ping buttons.")
    replacement_btn = """<button 
                    onClick={(e) => { 
                      e.stopPropagation(); 
                      setActiveTab('inbox'); 
                      setSelectedAdminThread({ id: doc.id, name: doc.name, role: 'doctor' }); 
                    }}
                    className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/20 transition-all flex items-center gap-1.5 text-[10px] font-bold uppercase px-3"
                    title="Direct inbox chat"
                  >
                    <MessageSquare size={14} /> Chat
                  </button>"""
    content = content.replace(match.group(0), replacement_btn)

# Also replace patient records list chat modal hook
patient_chat_pattern = r'onClick=\{\(e\) => \{ e\.stopPropagation\(\); setUniversalChatModal.*?\}\}'
match = re.search(patient_chat_pattern, content)
if match:
    print("[4.2] Found patient record direct message modal trigger.")
    content = content.replace(match.group(0), "onClick={(e) => { e.stopPropagation(); setActiveTab('inbox'); setSelectedAdminThread({ id: patient.id, name: patient.name, role: 'patient' }); }}")

# 5. Move Clinical Staff Registry ABOVE the Patient Records Table
# Locate Doctor registry block
start_marker = "{/* ═══ CLINICAL STAFF HUB (ACCOUNTABILITY) ═══ */}"
end_marker = "</div>\n      </div>\n\n      {/* --- PING MODAL --- */}" # Let's capture the end of that container

# Use simpler lookup: Extract from start_marker to its terminal closure (2 closed divs later)
registry_match = re.search(r'({\/\* ═══ CLINICAL STAFF HUB \(ACCOUNTABILITY\) ═══ \*\/}[\s\S]*?<\/div>\s*<\/div>\s*<\/div>\s*\)\);\s*\}\)\}\s*<\/div>\s*<\/div>)', content)
if not registry_match:
    # Fallback lookup
    registry_match = re.search(r'({\/\* ═══ CLINICAL STAFF HUB \(ACCOUNTABILITY\) ═══ \*\/}[\s\S]*?<\/div>\s*<\/div>)\s*(\{\/\* --- PING MODAL --- \*\/|AnimatePresence)', content)

if registry_match:
    print("[5] Successfully extracted Doctor Registry block.")
    registry_block = registry_match.group(1)
    
    # Remove it from original spot
    content = content.replace(registry_block, "")
    
    # Insert ABOVE Patient records
    patient_start_marker = "{/* ═══ PATIENT RECORDS TABLE ═══ */}"
    if patient_start_marker in content:
        print("[5.2] Found target insertion point above Patient table.")
        content = content.replace(patient_start_marker, registry_block + "\n\n      " + patient_start_marker)
    else:
        print("[ERROR] Could not find patient_start_marker!")
else:
    print("[ERROR] Could not isolate Doctor registry block via regex!")

# Save file
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done refactoring!")
