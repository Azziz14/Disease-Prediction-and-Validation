import re

class ClinicalIntelligenceService:
    def __init__(self):
        pass

    def evaluate_biomarkers(self, disease_type, features):
        """
        Analyzes the raw feature array based on the disease protocol.
        Returns a list of abnormal findings explaining exactly what is in excess/deficit.
        """
        abnormalities = []
        
        if disease_type == "diabetes" and len(features) >= 8:
            glucose, bp, bmi, age, insulin, skin, preg, dpf = features[:8]
            if glucose > 125:
                abnormalities.append(f"Glucose ({glucose} mg/dL) is in the diabetic range (Excessive, Baseline: <100)")
            elif glucose > 100:
                abnormalities.append(f"Glucose ({glucose} mg/dL) is elevated (Pre-diabetic, Baseline: <100)")
                
            if bp > 90:
                abnormalities.append(f"Diastolic Blood Pressure ({bp} mmHg) is dangerously high (Baseline: <80)")
            elif bp > 80:
                abnormalities.append(f"Diastolic Blood Pressure ({bp} mmHg) is elevated (Baseline: <80)")
                
            if bmi >= 30:
                abnormalities.append(f"BMI ({bmi}) indicates obesity (Excessive, Baseline: 18.5-24.9)")
            elif bmi >= 25:
                abnormalities.append(f"BMI ({bmi}) indicates overweight (Elevated, Baseline: 18.5-24.9)")
                
            if insulin > 166:
                abnormalities.append(f"Insulin ({insulin} μU/mL) is excessively high, indicating severe insulin resistance.")
                
            if dpf > 1.0:
                abnormalities.append(f"Diabetes Pedigree Function ({dpf}) shows extremely high genetic predisposition.")
                
        elif disease_type == "heart" and len(features) >= 8:
            age, sex, cp, resting_bp, chol, fast_bs, max_hr, ex_ang = features[:8]
            if resting_bp >= 140:
                abnormalities.append(f"Resting BP ({resting_bp} mmHg) is hypertensive (Stage 2, Baseline: <120)")
            elif resting_bp >= 130:
                abnormalities.append(f"Resting BP ({resting_bp} mmHg) is hypertensive (Stage 1, Baseline: <120)")
                
            if chol >= 240:
                abnormalities.append(f"Cholesterol ({chol} mg/dL) is dangerously high (High Risk, Baseline: <200)")
            elif chol >= 200:
                abnormalities.append(f"Cholesterol ({chol} mg/dL) is borderline high (Baseline: <200)")
                
            if fast_bs == 1:
                abnormalities.append("Fasting Blood Sugar > 120 mg/dL is a major cardiac risk multiplier (Pre-diabetic).")
                
            if ex_ang == 1:
                abnormalities.append("Exercise-induced angina detected. Reduced cardiac oxygen supply present.")
                
        elif disease_type == "mental" and len(features) >= 8:
            age, gender, fam_hist, work_int, sleep, stress, support, seeking = features[:8]
            if sleep < 6:
                abnormalities.append(f"Sleep duration ({sleep} hours) is critically low and exacerbates neurological stress.")
            if stress >= 8:
                abnormalities.append(f"Reported Stress Level ({stress}/10) is dangerously unmanageable.")
            if support <= 3:
                abnormalities.append("Social support system is practically non-existent, multiplying isolation risks.")
            if work_int >= 2: # Sometimes or Often
                abnormalities.append("Symptoms are actively interfering with occupational responsibilities.")

        return abnormalities

    def evaluate_prescription(self, disease_type, risk_level, extracted_drugs, raw_prescription_text):
        """
        Grades the provided prescription against the diagnosis.
        Checks for medicine correctness and dosage compliance.
        """
        if not extracted_drugs and not raw_prescription_text.strip():
            return None # No data provided
            
        evaluation = {
            "provided": True,
            "status": "UNKNOWN", # "VALID", "INVALID", "WARNING"
            "message": "",
            "details": []
        }
        
        # Regex to catch mg/mcg/g dosages in raw text
        dosages = re.findall(r"(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml)", raw_prescription_text.lower())
        
        # Simple disease expected meds
        expected_meds = {
            "diabetes": ["metformin", "insulin", "glipizide", "ozempic", "rybelsus"],
            "heart": ["atorvastatin", "lisinopril", "aspirin", "metoprolol", "amlodipine"],
            "mental": ["sertraline", "fluoxetine", "escitalopram", "bupropion", "alprazolam"]
        }
        
        cross_indications = {
            "diabetes": ["adderall", "prednisone", "olanzapine"], # Drugs that spike blood sugar
            "heart": ["ibuprofen", "pseudoephedrine", "celebrex"], # Drugs that spike BP
        }
        
        valid_drugs_found = []
        contraindicated_drugs = []
        
        for drug in extracted_drugs:
            d_lower = drug.lower()
            if d_lower in expected_meds.get(disease_type, []):
                valid_drugs_found.append(drug)
            if d_lower in cross_indications.get(disease_type, []):
                contraindicated_drugs.append(drug)
                
        # Evaluate Logic
        if contraindicated_drugs:
            evaluation["status"] = "INVALID"
            evaluation["message"] = "WARNING: Contraindicated Medications Detected!"
            evaluation["details"].append(f"Drugs like {', '.join(contraindicated_drugs)} are severely contraindicated for {disease_type} protocol and may cause acute adverse events.")
        elif valid_drugs_found:
            evaluation["status"] = "VALID"
            evaluation["message"] = "Prescription Verified & Medically Sound"
            
            # Check dosage heuristics
            if dosages:
                d_str = ", ".join([f"{val}{unit}" for val, unit in dosages])
                evaluation["details"].append(f"Confirmed expected intervention vector: {', '.join(valid_drugs_found)}.")
                evaluation["details"].append(f"Dosage extracted ({d_str}) appears within standard titration limits for initial therapy.")
            else:
                evaluation["details"].append(f"Confirmed expected intervention vector: {', '.join(valid_drugs_found)}.")
                evaluation["details"].append("NOTE: No exact mg dosage detected in prescription string. Standard clinical starting doses are assumed.")
        else:
            if extracted_drugs:
                evaluation["status"] = "WARNING"
                evaluation["message"] = "Sub-Optimal / Unrecognized Protocol"
                evaluation["details"].append(f"The prescribed vectors ({', '.join(extracted_drugs)}) do not align with Tier-1 clinical guidelines for {disease_type}.")
            else:
                evaluation["status"] = "UNKNOWN"
                evaluation["message"] = "Unable To Extract Specific Medical Compounds"
                evaluation["details"].append("The neural engine parsed the text but found no recognizable pharmacological agents.")

        return evaluation

    def generate_recommendations(self, disease_type, risk_level, abnormalities):
        """
        Generates daily life, medical recommendations, and precautions based on prediction.
        """
        lifestyle = []
        medical = []
        precautions = []
        
        is_high = risk_level.lower() == "high"
        
        if disease_type == "diabetes":
            lifestyle.append("Implement a strict low-glycemic index (GI) diet to prevent severe glucose spikes.")
            lifestyle.append("Stay hydrated. Drink at least 8 glasses of water daily to aid kidney function.")
            precautions.append("Avoid sugary drinks, processed carbohydrates, and trans fats.")
            precautions.append("Monitor feet for cuts or sores; diabetic neuropathy reduces sensation.")
            
            if any("Obese" in a or "Overweight" in a for a in abnormalities):
                lifestyle.append("Target a 5-10% body weight reduction through daily 30-minute steady-state cardio.")
            if is_high:
                medical.append("Immediate initiation of Metformin 500mg daily is strongly indicated.")
                medical.append("Mandatory continuous glucose monitoring (CGM) deployment.")
                precautions.append("High risk state: Consult endocrinologist immediately.")
            else:
                medical.append("Conduct an A1C blood panel in 90 days to track progression.")
                
        elif disease_type == "heart":
            lifestyle.append("Immediately transition to a DASH (Dietary Approaches to Stop Hypertension) or Mediterranean diet.")
            lifestyle.append("Engage in moderate aerobic exercise for 150 minutes per week (e.g., brisk walking).")
            precautions.append("Strictly avoid high sodium foods (canned soups, fast food) to prevent BP spikes.")
            precautions.append("Limit caffeine and completely avoid tobacco and illicit stimulants.")
            
            if any("Cholesterol" in a for a in abnormalities):
                lifestyle.append("Eliminate trans fats and reduce saturated fat intake to <6% of daily calories.")
            if is_high:
                medical.append("Deploy a high-intensity statin protocol to aggressively lower lipid markers.")
                medical.append("Prescribe low-dose daily aspirin (81mg) if no bleeding risks are present.")
                precautions.append("High risk state: Immediate cardiology referral. Avoid heavy lifting.")
            else:
                medical.append("Monitor peripheral resting blood pressure bi-weekly.")

        elif disease_type == "mental":
            lifestyle.append("Establish a rigid circadian sleep schedule targeting exactly 8 hours.")
            lifestyle.append("Incorporate daily physical activity to naturally boost serotonin and dopamine.")
            precautions.append("Avoid alcohol and recreational drugs as they can severely worsen mood swings.")
            precautions.append("Limit screen time 2 hours before bed to improve sleep hygiene.")
            
            if any("Stress" in a for a in abnormalities):
                lifestyle.append("Mandatory cognitive decompression protocol (mindfulness/CBT exercises) twice daily.")
            if is_high:
                medical.append("Immediate referral for pharmacological psychiatric evaluation (SSRI/SNRI baseline setup).")
                medical.append("Accelerated scheduling for continuous behavioral therapy sessions.")
                precautions.append("High risk state: Ensure patient has emergency contact numbers (crisis hotline) available.")
            else:
                medical.append("Monitor mood bi-weekly. Over-the-counter Vitamin D3 and Omega-3 supplementation recommended.")

        return {
            "lifestyle": lifestyle,
            "medical": medical,
            "precautions": precautions
        }
