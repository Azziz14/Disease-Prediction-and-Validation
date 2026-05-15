import re

path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\DoctorDashboard.tsx"

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find all unique occurrences of strings matching 'orange-\d+' or 'orange'
matches = re.findall(r'orange-\d+|orange', content)
from collections import Counter
counts = Counter(matches)

print("--- Occurrences of Orange classes in DoctorDashboard.tsx ---")
for item, count in counts.most_common():
    print(f"{item}: {count} times")
