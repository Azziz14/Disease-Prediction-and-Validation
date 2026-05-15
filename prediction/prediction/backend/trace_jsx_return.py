path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\AdminDashboard.tsx"

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if line.strip().startswith('return (') and not '() =>' in line:
        print(f"L{i}: {line.strip()}")
        # Print next 5 lines
        for j in range(1, 6):
            print(f"L{i+j}: {lines[i+j-1].strip()}")
