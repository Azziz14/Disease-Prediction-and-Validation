path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\AdminDashboard.tsx"

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'flaggingDoctor' in line:
        print(f"L{i}: {line.strip()}")
