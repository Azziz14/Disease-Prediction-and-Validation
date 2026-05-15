import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"C:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src"

def safe_scan(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if ".map(" in line:
            block = lines[idx:min(idx+6, len(lines))]
            block_str = "\n".join(block)
            
            # Check for unsafe render:
            # 1. It renders something in curly braces {...}
            # 2. It DOES NOT use typeof, String, .name, JSON.stringify
            # 3. It belongs to arrays related to recommendations, precautions, lifestyle, features, meds, etc.
            
            # Identify loop variable name
            match = re.search(r"\.map\(\s*\(?\s*(\w+)", line)
            if match:
                var_name = match.group(1)
                
                # Does any of the next 5 lines contain {var_name} but without a safeguard?
                for b_line in block:
                    # Simple check: is {var_name} inside the JSX node?
                    # E.g. <span>{var_name}</span> or <div>{var_name}</div>
                    # Also make sure there is no typeof, JSON.stringify, or .name before/after it in that same interpolation
                    interps = re.findall(r"\{([^{}]+)\}", b_line)
                    for interp in interps:
                        # Trim it
                        clean_interp = interp.strip()
                        # If the interpolation is JUST the variable name, it's unsafe!
                        if clean_interp == var_name:
                            print(f"🚨 CRITICAL UNSAFE RENDER: {os.path.basename(path)} : Line {idx + 1 + block.index(b_line)}")
                            print(f"  Loop: {line.strip()}")
                            print(f"  Unsafe Line: {b_line.strip()}")
                            print("-" * 60)
                        # If it's a concatenation or something but contains var_name and lacks safeguard
                        elif var_name in clean_interp and not any(safe in clean_interp for safe in ["typeof", "String", "JSON.stringify", ".name", ".id", ".message", ".date", ".dosage", ".label", ".fill", ".icon", ".reason", ".text", ".msg"]):
                             # Just in case, also flag suspicious interpolations
                             print(f"⚠️ SUSPICIOUS RENDER: {os.path.basename(path)} : Line {idx + 1 + block.index(b_line)}")
                             print(f"  Loop: {line.strip()}")
                             print(f"  Unsafe Line: {b_line.strip()}")
                             print("-" * 60)

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".tsx"):
            # Filter files already proven perfectly audited
            if file in ["InsightsPanel.tsx", "ReportPanel.tsx", "ResultCard.tsx", "Diagnosis.tsx", "History.tsx"]:
                continue
            safe_scan(os.path.join(root, file))
