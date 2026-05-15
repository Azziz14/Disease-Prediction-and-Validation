with open(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\AdminDashboard.tsx", 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- LINES IN AdminDashboard.tsx CONTAINING 'flag' ---")
for i, line in enumerate(lines, 1):
    if 'flag' in line.lower():
        print(f"L{i}: {line.strip()}")

print("\n--- SEARCHING FOR 'doctor' AND 'api' or 'fetch' ---")
for i, line in enumerate(lines, 1):
    if 'fetch' in line.lower() and 'doctor' in line.lower():
        print(f"L{i}: {line.strip()}")
