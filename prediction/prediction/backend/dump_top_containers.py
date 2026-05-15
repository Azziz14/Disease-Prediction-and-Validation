import re

def dump_top_containers(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    start_idx = content.find('return (')
    jsx_content = content[start_idx:]
    
    containers = []
    stack = []
    for i, c in enumerate(jsx_content):
        if c == '{': stack.append(i)
        elif c == '}':
            if stack:
                start = stack.pop()
                if not stack:
                    containers.append(jsx_content[start:i+1])
                    
    print("Dumping first 7 containers found after 'return (':")
    for i in range(min(7, len(containers))):
        print(f"\n=== CONTAINER {i+1} ===")
        print(containers[i])

dump_top_containers(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\DoctorDashboard.tsx")
