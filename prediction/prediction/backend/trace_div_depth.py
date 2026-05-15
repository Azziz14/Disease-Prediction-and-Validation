path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\AdminDashboard.tsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find return statement
ret_idx = content.find("return (")
print(f"Return statement starts at index {ret_idx}")
if ret_idx != -1:
    # Print first 300 chars of return statement
    print("--- RETURN WRAPPERS ---")
    print(content[ret_idx:ret_idx+300])
