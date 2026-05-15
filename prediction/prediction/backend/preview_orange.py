import re

path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\DoctorDashboard.tsx"

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print("--- Previewing lines containing 'orange' ---")
for idx, line in enumerate(lines, start=1):
    if 'orange' in line:
        print(f"L{idx}: {line.strip()}")
