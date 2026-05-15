with open(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\PatientDashboard.tsx", 'r', encoding='utf-8') as f:
    content = f.read()

import re
# Find downloadReport
lines = content.split('\n')
for i, line in enumerate(lines, 1):
    if 'downloadReport' in line or 'pdf' in line.lower():
        print(f"L{i}: {line.strip()}")

# Let's also look for id="clinical-print-template" or similar
for i, line in enumerate(lines, 1):
    if 'id=' in line and ('print' in line.lower() or 'pdf' in line.lower() or 'report' in line.lower()):
        print(f"Print Template found at L{i}: {line.strip()}")
