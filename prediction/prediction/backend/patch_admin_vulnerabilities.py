import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"C:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src"

# 1. Target dashboards/AdminDashboard.tsx
active_admin_path = os.path.join(base_dir, "pages", "dashboards", "AdminDashboard.tsx")
if os.path.exists(active_admin_path):
    with open(active_admin_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    lines = content.splitlines()
    modified = False
    for idx, line in enumerate(lines):
        if "patient.prescribed_medicines?.map(" in line:
            if idx + 3 < len(lines) and '<span className="text-cyan-300">{med}</span>' in lines[idx+3]:
                lines[idx] = lines[idx].replace("(med: string, i: number)", "(med: any, i: number)")
                lines[idx+3] = lines[idx+3].replace("{med}", "{typeof med === 'object' ? String(med.name || med.purpose || 'Medication') : String(med)}")
                modified = True
        
        if "patient.symptoms?.map(" in line:
            if idx + 2 < len(lines) and "{s}" in lines[idx+2]:
                lines[idx] = lines[idx].replace("(s: string, i: number)", "(s: any, i: number)")
                lines[idx+2] = lines[idx+2].replace("{s}", "{typeof s === 'object' ? String(s.name || s.purpose || 'Symptom') : String(s)}")
                modified = True
                
    if modified:
        with open(active_admin_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        print("SUCCESS: Patched dashboards/AdminDashboard.tsx")
    else:
        print("WARNING: Could not match target snippets in dashboards/AdminDashboard.tsx")
else:
    print("ERROR: dashboards/AdminDashboard.tsx not found")


# 2. Target the legacy pages/AdminDashboard.tsx (Just in case)
legacy_admin_path = os.path.join(base_dir, "pages", "AdminDashboard.tsx")
if os.path.exists(legacy_admin_path):
    with open(legacy_admin_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    lines = content.splitlines()
    modified = False
    for idx, line in enumerate(lines):
        if "patient.matched_drugs.slice(" in line:
            if idx + 1 < len(lines) and "- {drug}</p>" in lines[idx+1]:
                lines[idx+1] = lines[idx+1].replace("{drug}", "{typeof drug === 'object' ? String(drug.name || drug.purpose || 'Drug') : String(drug)}")
                modified = True
        
        if "].slice(0, 4).map((item, idx) => (" in line:
            if idx + 1 < len(lines) and "- {item}</p>" in lines[idx+1]:
                lines[idx+1] = lines[idx+1].replace("{item}", "{typeof item === 'object' ? String(item.name || item.purpose || 'Directive') : String(item)}")
                modified = True
                
    if modified:
        with open(legacy_admin_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        print("SUCCESS: Patched legacy pages/AdminDashboard.tsx")
    else:
        print("WARNING: Could not match targets in legacy pages/AdminDashboard.tsx")
