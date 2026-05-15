import os

file_path = r"C:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\AdminDashboard.tsx"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Locate the line: {/* --- SECURE DOCTOR CORRESPONDENCE HUB (CHAT) --- */}
target = "{/* --- SECURE DOCTOR CORRESPONDENCE HUB (CHAT) --- */}"

if target in content:
    # Insert </AnimatePresence> right before the line
    # We need to maintain the preceding spaces / formatting
    lines = content.splitlines()
    new_lines = []
    inserted = False
    for line in lines:
        if target in line and not inserted:
            new_lines.append("      </AnimatePresence>")
            inserted = True
        new_lines.append(line)
    
    new_content = "\n".join(new_lines)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("SUCCESS: Balancing complete!")
else:
    print("ERROR: Target phrase not found!")
