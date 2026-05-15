import os
import re

base_dir = r"C:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src"

def scan_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Look for mapping blocks where recommendations are map()ped and see if a raw interpolation {item} or {r} is nested
    # We are looking specifically for items like: 
    # .map((something) => ... {something} ...)
    # Let's find all occurrences of .map(
    
    # Just to be completely safe, let's print any suspicious lines containing maps inside files 
    # iterating recommendations, lifestyle, precautions, or medical
    lines = content.splitlines()
    suspicious = []
    keywords = ["recommendations", "lifestyle", "precautions", "medical"]
    
    for idx, line in enumerate(lines):
        if any(kw in line for kw in keywords) and ".map(" in line:
            # Collect the map block (next 5 lines)
            block = lines[idx:min(idx+5, len(lines))]
            # Check if there is a naked bracket with the variable
            # Example: .map((r) => ... {r}
            m = re.search(r"\.map\(\s*\(\s*(\w+)", line)
            if m:
                var_name = m.group(1)
                # check next lines for raw {var_name} without typeof or .name
                for block_line in block:
                    if f"{{{var_name}}}" in block_line:
                        suspicious.append((idx + 1, line, block_line))
                        
    return suspicious

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".tsx") or file.endswith(".ts"):
            path = os.path.join(root, file)
            results = scan_file(path)
            if results:
                print(f"SUSPICIOUS FILE: {path}")
                for r in results:
                    print(f"  Line {r[0]}: {r[1].strip()}")
                    print(f"    Block Match: {r[2].strip()}")
