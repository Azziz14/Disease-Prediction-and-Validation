import re

def find_jsx_expression_containers(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # We want to find the return block
    # And then find all { } expressions that are NOT inside tags but are children
    start_idx = content.find('return (')
    if start_idx == -1:
        print("Could not find return block!")
        return
        
    jsx_content = content[start_idx:]
    
    # Let's parse { } containers by tracking bracket depths
    containers = []
    stack = []
    for i, c in enumerate(jsx_content):
        if c == '{':
            stack.append(i)
        elif c == '}':
            if stack:
                start = stack.pop()
                if not stack: # Top-level container!
                    containers.append(jsx_content[start:i+1])
                    
    print(f"Found {len(containers)} top-level expression containers inside return:")
    for idx, container in enumerate(containers):
        # Limit print to first 100 chars to make it readable
        lines = container.split('\n')
        summary = lines[0] if len(lines) == 1 else f"{lines[0]} ... ({len(lines)} lines) ... {lines[-1]}"
        print(f"{idx+1}: {summary}")

find_jsx_expression_containers(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\DoctorDashboard.tsx")
