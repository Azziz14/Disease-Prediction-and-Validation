import os
import sys

# Explicitly enforce utf-8 output to prevent console encoding crashes on Windows
sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"C:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src"

def ultra_scan(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if ".map(" in line:
            block = "\n".join(lines[idx:min(idx+6, len(lines))])
            if "{" in block and "}" in block:
                print(f"MAP FOUND in {os.path.basename(path)}: Line {idx+1}")
                print(block)
                print("=" * 40)

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".tsx"):
            # Skip files that we know are perfectly safe to reduce noise
            if file in ["InsightsPanel.tsx", "ReportPanel.tsx", "ResultCard.tsx", "Diagnosis.tsx", "History.tsx"]:
                continue
            ultra_scan(os.path.join(root, file))
