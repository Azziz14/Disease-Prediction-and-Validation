import os

base_dir = r"C:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src"

# 1. Fix Diagnosis.tsx
diag_path = os.path.join(base_dir, "pages", "Diagnosis.tsx")
if os.path.exists(diag_path):
    with open(diag_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    bad_snippet = "{voiceResult.recommendations.lifestyle.map((r: string, i: number) => (\n                        <p key={i} className=\"text-sm text-gray-300 mb-1\">- {r}</p>\n                      ))}"
    
    # Let's use a more resilient replacement approach: find the loop line and the child element line
    # We will search for voiceResult.recommendations.lifestyle.map and replace the JSX element output
    lines = content.splitlines()
    modified = False
    for i in range(len(lines)):
        if "voiceResult.recommendations.lifestyle.map(" in lines[i]:
            # Check the next line
            if i + 1 < len(lines) and "- {r}" in lines[i+1]:
                lines[i] = lines[i].replace("(r: string, i: number)", "(r: any, i: number)")
                lines[i+1] = lines[i+1].replace("- {r}", "- {typeof r === 'object' ? String(r.name || r.purpose || 'Directive') : String(r)}")
                modified = True
    
    if modified:
        with open(diag_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print("SUCCESS: Patched Diagnosis.tsx")
    else:
        print("WARNING: Could not match Diagnosis.tsx snippet for patch")
else:
    print("ERROR: Diagnosis.tsx not found")


# 2. Fix ReportPanel.tsx
report_path = os.path.join(base_dir, "components", "ui", "ReportPanel.tsx")
if os.path.exists(report_path):
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = content.splitlines()
    modified = False
    for i in range(len(lines)):
        if "report.recommendations.map(" in lines[i]:
            if i + 2 < len(lines) and "•</span> {r}" in lines[i+2]:
                lines[i] = lines[i].replace("(r: string, i: number)", "(r: any, i: number)")
                lines[i+2] = lines[i+2].replace("•</span> {r}", "•</span> {typeof r === 'object' ? String(r.name || r.purpose || 'Directive') : String(r)}")
                modified = True
                
    if modified:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print("SUCCESS: Patched ReportPanel.tsx")
    else:
        print("WARNING: Could not match ReportPanel.tsx snippet for patch")
else:
    print("ERROR: ReportPanel.tsx not found")
