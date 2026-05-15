with open(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\AdminDashboard.tsx", 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- FINDING FLAG OR FLAGGED IN DOCTOR RENDERING ---")
for i, line in enumerate(lines, 1):
    if 'flag' in line.lower() and ('doc.' in line or 'doc[' in line):
        print(f"L{i}: {line.strip()}")
