import os

base_dir = r"C:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src"

def brute_scan(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if ".map" in line:
            # Look at this line and the next 4 lines
            block = "\n".join(lines[idx:min(idx+5, len(lines))])
            # If ANY of our risk keywords are in this block
            if any(kw in block.lower() for kw in ["recommendation", "lifestyle", "precautions", "medical", "routine"]):
                print(f"MATCH: {path} : Line {idx+1}")
                print(block)
                print("-" * 50)

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".tsx") or file.endswith(".ts"):
            brute_scan(os.path.join(root, file))
