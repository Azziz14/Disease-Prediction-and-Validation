with open(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\PatientDashboard.tsx", 'r', encoding='utf-8') as f:
    content = f.read()

variables = ['latestRisk', 'latestConfidence', 'latestPrediction', 'selectedDisease', 'recommendationCount']
for var in variables:
    if var in content:
        print(f"FOUND variable: {var}")
    else:
        print(f"MISSING variable: {var} !!!")
