with open(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\AdminDashboard.tsx", 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'setPingModal' in line or 'setChatModal' in line:
        print(f"L{i}: {line.strip()}")
    if 'window.location.reload' in line:
        print(f"L{i}: {line.strip()}")
