import re

def list_nested_containers(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Find start of container 29
    target = "{activeTab === 'inbox' && ("
    start_idx = content.find(target)
    if start_idx == -1:
        print("Could not find target!")
        return

    sub_content = content[start_idx:]
    # Find matching close } for top level
    stack = []
    end_idx = -1
    for i, c in enumerate(sub_content):
        if c == '{':
            stack.append(i)
        elif c == '}':
            if stack:
                stack.pop()
                if not stack:
                    end_idx = i
                    break
                    
    if end_idx == -1:
        print("Could not find end of container!")
        return

    inner_content = sub_content[1:end_idx] # Content inside the top-level { and }
    
    # Now find all nested expression containers inside inner_content
    nested = []
    stack = []
    for i, c in enumerate(inner_content):
        if c == '{':
            stack.append(i)
        elif c == '}':
            if stack:
                start = stack.pop()
                if not stack: # Direct nested child!
                    nested.append(inner_content[start:i+1])

    print(f"Found {len(nested)} direct nested expression containers inside Container 29:")
    for idx, expr in enumerate(nested):
        lines = expr.split('\n')
        summary = lines[0] if len(lines) == 1 else f"{lines[0]} ... ({len(lines)} lines) ... {lines[-1]}"
        print(f"{idx+1}: {summary}")

list_nested_containers(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\DoctorDashboard.tsx")
