import re

def check_balance(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    opens = content.count('{')
    closes = content.count('}')
    
    print(f"File: {path.split('\\')[-1]}")
    print(f"Brackets - Opens: {opens}, Closes: {closes}")
    if opens != closes:
        print("WARNING!!! Unbalanced brackets detected!")
    else:
        print("SUCCESS: Balanced curly brackets.")
        
check_balance(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\DoctorDashboard.tsx")
check_balance(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\AdminDashboard.tsx")
