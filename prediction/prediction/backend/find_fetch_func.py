with open(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\AdminDashboard.tsx", 'r', encoding='utf-8') as f:
    content = f.read()

import re
fetch_defs = re.findall(r'const (\w+)\s*=\s*(?:async\s*)?\(\)\s*=>\s*\{[^}]*fetch', content)
print(f"Fetch-like function candidates: {fetch_defs}")

# Let's view lines 130 to 160
lines = content.split('\n')
for i in range(120, 150):
    if i < len(lines):
        print(f"L{i+1}: {lines[i]}")
