import re

def dump_specific_containers(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    target = "{activeTab === 'inbox' && ("
    start_idx = content.find(target)
    if start_idx == -1: return

    sub_content = content[start_idx:]
    stack = []
    end_idx = -1
    for i, c in enumerate(sub_content):
        if c == '{': stack.append(i)
        elif c == '}':
            if stack:
                stack.pop()
                if not stack:
                    end_idx = i
                    break
                    
    inner_content = sub_content[1:end_idx]
    
    nested = []
    stack = []
    for i, c in enumerate(inner_content):
        if c == '{': stack.append(i)
        elif c == '}':
            if stack:
                start = stack.pop()
                if not stack:
                    nested.append(inner_content[start:i+1])

    print("=== CONTAINER 10 ===")
    print(nested[9])
    print("=== CONTAINER 13 ===")
    print(nested[12])
    print("=== CONTAINER 14 ===")
    print(nested[13])
    print("=== CONTAINER 16 ===")
    print(nested[15])

dump_specific_containers(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\DoctorDashboard.tsx")
