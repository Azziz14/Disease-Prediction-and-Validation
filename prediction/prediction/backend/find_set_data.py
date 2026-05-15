with open(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\AdminDashboard.tsx", 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines, 1):
    if 'setData(' in line:
        print(f"L{i}: {line.strip()}")

# Also find the enclosing function around it
for i, line in enumerate(lines, 1):
    if 'useEffect(() =>' in line:
        # Print 10 lines after
        print(f"\n--- useEffect at L{i} ---")
        for j in range(i, min(i+20, len(lines))):
            print(f"L{j+1}: {lines[j]}")
