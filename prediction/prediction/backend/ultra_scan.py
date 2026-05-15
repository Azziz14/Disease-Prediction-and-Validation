import os

base_dir = r"C:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src"

def ultra_scan(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if ".map(" in line:
            # Print the map header and the next 5 lines
            block = "\n".join(lines[idx:min(idx+6, len(lines))])
            # Only print if it contains a potential JSX interpolation {something}
            # and DOES NOT contain typeof, .name, .id, String(, or JSON.stringify
            if "{" in block and "}" in block:
                # Try to find if it renders a raw variable
                print(f"MAP FOUND in {os.path.basename(path)}: Line {idx+1}")
                print(block)
                print("=" * 40)

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".tsx"):
            ultra_scan(os.path.join(root, file))
