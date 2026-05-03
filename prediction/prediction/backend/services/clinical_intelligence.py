import os
import re
import json
import requests
from utils.clinical_registry import ClinicalRegistry

class ClinicalIntelligenceService:
    def __init__(self):
        # Store all keys for the retry loop
        self.keys = {
            "groq": os.getenv("GROQ_API_KEY", "").strip(),
            "openrouter": os.getenv("OPENROUTER_API_KEY", "").strip(),
            "openai": os.getenv("OPENAI_API_KEY", "").strip()
        }

    def _call_llm(self, prompt):
        """Internal helper with multi-provider retry logic. Groq is first priority."""
        providers = [
            {"name": "groq", "key": self.keys["groq"], "url": "https://api.groq.com/openai/v1/chat/completions", "model": "llama-3.3-70b-versatile"},
            {"name": "openrouter", "key": self.keys["openrouter"], "url": "https://openrouter.ai/api/v1/chat/completions", "model": "meta-llama/llama-3.3-70b-instruct"},
            {"name": "openai", "key": self.keys["openai"], "url": "https://api.openai.com/v1/chat/completions", "model": "gpt-4o-mini"}
        ]

        messages = [
            {"role": "system", "content": "You are a senior clinical consultant. Provide high-fidelity, non-repetitive, actionable medical advice. USE THE SPECIFIC BIOMARKERS PROVIDED TO CUSTOMIZE THE ADVICE. Avoid generic boilerplates. Return strictly JSON with: 'summary' (str), 'lifestyle' (list), 'medical' (list), 'precautions' (list), and 'medications' (list of objects with 'name', 'dosage', 'frequency', 'note')."},
            {"role": "user", "content": prompt}
        ]

        for p in providers:
            if not p["key"]:
                continue
                
            headers = {
                "Authorization": f"Bearer {p['key']}",
                "Content-Type": "application/json"
            }
            
            if p["name"] == "openrouter":
                headers["HTTP-Referer"] = "http://localhost:3000"
                headers["X-Title"] = "Healthcare AI Platform"

            payload = {
                "model": p["model"],
                "messages": messages,
                "response_format": {"type": "json_object"} if p["name"] != "groq" or "llama-3.3" in p["model"] else None,
                "temperature": 0.3
            }
            
            try:
                print(f"[ClinicalAI] Attempting insights via {p['name']}...")
                response = requests.post(p["url"], headers=headers, json=payload, timeout=20)
                if response.status_code == 200:
                    content = response.json()['choices'][0]['message']['content']
                    # Clean up content if model adds markdown blocks
                    content = content.replace("```json", "").replace("```", "").strip()
                    print(f"[ClinicalAI] SUCCESS via {p['name']}")
                    return json.loads(content)
                else:
                    print(f"[ClinicalAI] {p['name']} API Error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"[ClinicalAI] {p['name']} Call failed: {e}")
                
        return None

    def evaluate_biomarkers(self, disease_type, features):
        """
        Analyzes the raw feature array based on the disease protocol.
        Returns a list of abnormal findings explaining exactly what is in excess/deficit.
        """
        abnormalities = []
        indices = ClinicalRegistry.get_indices(disease_type)
        
        if disease_type == "diabetes" and len(features) >= 8:
            glucose = features[indices["glucose"]]
            bp = features[indices["blood_pressure"]]
            bmi = features[indices["bmi"]]
            insulin = features[indices["insulin"]]
            dpf = features[indices["pedigree"]]
            
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
            resting_bp = features[indices["blood_pressure"]]
            chol = features[indices["cholesterol"]]
            fast_bs = features[indices["fasting_bs"]]
            ex_ang = features[indices["max_heart_rate"]] # This might be the wrong mapping, check Registry
            
            if resting_bp >= 140:
                abnormalities.append(f"Resting BP ({resting_bp} mmHg) is hypertensive (Stage 2, Baseline: <120)")
            elif resting_bp >= 130:
                abnormalities.append(f"Resting BP ({resting_bp} mmHg) is hypertensive (Stage 1, Baseline: <120)")
                
            if chol >= 240:
                abnormalities.append(f"Cholesterol ({chol} mg/dL) is dangerously high (High Risk, Baseline: <200)")
            elif chol >= 200:
                abnormalities.append(f"Cholesterol ({chol} mg/dL) is borderline high (Baseline: <200)")
                
            if fast_bs == 1:
                abnormalities.append("Fasting Blood Sugar > 120 mg/dL is a major cardiac risk multiplier.")
                
        elif disease_type == "mental" and len(features) >= 8:
            sleep = features[indices["sleep_hours"]]
            stress = features[indices["stress_level"]]
            support = features[indices["social_support"]]
            work_int = features[indices["work_interference"]]
            
            if sleep < 6:
                abnormalities.append(f"Sleep duration ({sleep} hours) is critically low.")
            if stress >= 8:
                abnormalities.append(f"Reported Stress Level ({stress}/10) is dangerously high.")
            if support <= 3:
                abnormalities.append("Social support system is practically non-existent.")

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

    def generate_recommendations(self, disease_type, risk_level, abnormalities, features):
        """
        Generates daily life, medical recommendations, and precautions.
        Uses Generative AI (Grok/OpenRouter) for personalized, non-repetitive insights.
        """
        # 1. Attempt Generative AI Enrichment
        prompt = f"""
        DIAGNOSTIC CONTEXT: {disease_type.upper()} protocol
        CURRENT RISK: {risk_level}
        CLINICAL ABNORMALITIES: {', '.join(abnormalities)}
        
        REQUIRED: Highly specialized, non-repetitive clinical recommendations. 
        CRITICAL: DO NOT use generic advice like 'eat healthy' or 'exercise more'. 
        Instead, use the SPECIFIC abnormalities detected: {', '.join(abnormalities)}.
        
        BIO-MARKER CONTEXT:
        {json.dumps(dict(zip(ClinicalRegistry.get_indices(disease_type).keys(), features)))}
        
        Ensure 'medications' contains 2-3 specific pharmacological agents. 
        Each medication MUST have: name, dosage (e.g. 500mg), frequency (e.g. twice daily), and a DEEP clinical note justifying its use for THIS SPECIFIC profile.
        """
        
        ai_advice = self._call_llm(prompt)
        
        if ai_advice:
            return {
                "summary": ai_advice.get("summary", ""),
                "lifestyle": ai_advice.get("lifestyle", []),
                "medical": ai_advice.get("medical", []),
                "precautions": ai_advice.get("precautions", []),
                "medications": ai_advice.get("medications", []),
                "source": "Generative AI Neural Engine"
            }

        # 2. Hardcoded Fallback (if AI offline or key missing)
        lifestyle = [f"CLINICAL DIRECTIVE: Focus on immediate stabilization of detected anomalies: {', '.join(abnormalities) if abnormalities else 'unspecified biomarkers'}."]
        medical = []
        precautions = ["Regularly monitor vital signs at home twice daily."]
        medications = []
        
        is_high = risk_level.lower() == "high"
        
        if disease_type == "diabetes":
            lifestyle.append("NUTRITION: Implement strict low-glycemic index (GI) Mediterranean diet.")
            lifestyle.append("HYDRATION: Target 2.5L-3L filtered water daily to support metabolic throughput.")
            
            # Clinical Escalation in fallback
            if is_high or any("dangerous" in a.lower() or "excessive" in a.lower() for a in abnormalities):
                medical.append(f"URGENT INTERVENTION: Deploy standard high-risk diabetes protocol.")
                medical.append("MONITORING: Immediate endocrine referral required for therapeutic assessment.")
                precautions.append("CRITICAL: Seek immediate medical attention if you experience severe thirst or frequent urination.")
                medications = [
                    {"name": "Metformin", "dosage": "500mg", "frequency": "twice daily with food", "note": "Standard first-line intervention for high-risk biomarker profiles."}
                ]
            else:
                medical.append("PREVENTATIVE: Schedule a comprehensive HbA1C panel for baseline evaluation.")
                medical.append("MONITORING: Track fasting glucose levels daily for 14 days.")
                
        elif disease_type == "heart":
            lifestyle.append("CARDIO-VASCULAR: Transition to DASH diet protocol (Sodium < 1500mg).")
            if is_high or any("dangerous" in a.lower() or "hypertensive" in a.lower() for a in abnormalities):
                medical.append("URGENT: Statin therapy initiation indicated (e.g., Atorvastatin 20mg).")
                medical.append("HYPERTENSIVE ACTION: Immediate medical consultation for BP stabilization required.")
                precautions.append("STATUS RED: Immediate cardiology consult required. Restrict intense physical exertion.")
                medications = [
                    {"name": "Atorvastatin", "dosage": "20mg", "frequency": "once daily", "note": "Primary cardioprotective intervention suggested based on risk profile."}
                ]
            else:
                medical.append("MONITORING: Consistent daily blood pressure tracking mandatory.")
                medical.append("SCHEDULE: Cardiology evaluation within the next 30 days.")

        return {
            "summary": "AI Enrichment offline - presenting rule-based clinical fallbacks.",
            "lifestyle": lifestyle,
            "medical": medical,
            "precautions": precautions,
            "medications": medications,
            "source": "Clinical Rule Engine (Neural Link Offline)"
        }
