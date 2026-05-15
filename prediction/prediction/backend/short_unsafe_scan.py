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
            match = re.search(r"\.map\(\s*\(?\s*(\w+)", line)
            if match:
                var_name = match.group(1)
                for b_line in block:
                    interps = re.findall(r"\{([^{}]+)\}", b_line)
                    for interp in interps:
                        clean_interp = interp.strip()
                        if clean_interp == var_name:
                            # Verify it's not a primitive list like [1,2,3].map(i => ...)
                            if not any(hint in line for hint in ["[1,", "[1 ,", "['", '["', "steps.map"]):
                                print(f"!!! PATH: {path} : Line {idx + 1 + block.index(b_line)}")
                                print(f"    Line: {b_line.strip()}")

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".tsx"):
            # Exclude the ones we know are safe
            if file in ["InsightsPanel.tsx", "ReportPanel.tsx", "ResultCard.tsx", "Diagnosis.tsx", "History.tsx"]:
                continue
            safe_scan(os.path.join(root, file))
