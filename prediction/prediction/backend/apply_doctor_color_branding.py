import re

path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\DoctorDashboard.tsx"

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 1. Replace RGBA color hashes for orange with cyan
# Orange RGB: 234, 88, 12
# Cyan RGB: 6, 182, 212
content = content.replace('rgba(234,88,12', 'rgba(6,182,212')

# 2. Replace Tailwind color shades
content = content.replace('orange-400', 'cyan-400')
content = content.replace('orange-500', 'cyan-500')
content = content.replace('orange-600', 'cyan-600')
content = content.replace('orange-900', 'cyan-950') # map deep orange shadow to deep cyan

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully applied premium Cyan branding to DoctorDashboard.tsx!")
