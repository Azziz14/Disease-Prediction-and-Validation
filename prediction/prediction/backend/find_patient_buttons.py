with open(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\AdminDashboard.tsx", 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

for i, line in enumerate(lines, 1):
    if 'setUniversalChatModal' in line:
        print(f"L{i}: {line.strip()}")
