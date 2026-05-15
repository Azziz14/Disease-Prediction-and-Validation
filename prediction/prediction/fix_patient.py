import os

def fix_patient_dash():
    filepath = os.path.join("frontend", "src", "pages", "dashboards", "PatientDashboard.tsx")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the broken template string with the original hostname one
    bad_str = "${process.env.REACT_APP_API_URL || `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}'}"
    good_str = "http://${window.location.hostname}:5000"
    
    content = content.replace(bad_str, good_str)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_patient_dash()
