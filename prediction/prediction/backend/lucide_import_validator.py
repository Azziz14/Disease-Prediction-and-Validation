import re

path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\DoctorDashboard.tsx"

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 1. Find Lucide imports
import_match = re.search(r'import \{(.*?)\} from \'lucide-react\'', content)
if not import_match:
    print("Could not find Lucide import block!")
    exit()

imported_icons = [x.strip() for x in import_match.group(1).split(',')]
print(f"Imported icons: {imported_icons}")

# 2. Find all potential icon usages in JSX
# React components usually start with uppercase and are used as <ComponentName ... />
potential_tags = re.findall(r'<([A-Z][a-zA-Z0-9]*)\b', content)

# Standard Lucide icons list that could be used (or we check ones that are not imported and not custom components)
known_custom_components = ['DoctorPatientAssignment', 'Link', 'motion', 'AnimatePresence']

missing = []
for tag in set(potential_tags):
    if tag in known_custom_components:
        continue
    if tag not in imported_icons:
        missing.append(tag)

if missing:
    print(f"\nWARNING: Found potential missing icon imports used in JSX: {missing}")
else:
    print("\nAll React components used in JSX are properly imported!")
