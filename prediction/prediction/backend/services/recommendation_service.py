class RecommendationService:
    def __init__(self):
        # Professional Clinical Protocols with Structured Medications
        self.protocols = {
            "heart": {
                "lifestyle": [
                    "Sodium restriction (< 2g/day) to manage fluid retention.",
                    "Complete cessation of tobacco and secondary smoke exposure.",
                    "DASH diet compliance with focus on potassium-rich foods.",
                    "Limit fluid intake if edema is present (consult physician)."
                ],
                "daily_routine": [
                    "08:00 AM: Manual blood pressure and weight monitoring.",
                    "10:00 AM: 20-minute light aerobic walk (RPE scale 11-13).",
                    "02:00 PM: 15-minute mindfulness/stress reduction session.",
                    "08:00 PM: Evening vital check and sodium review."
                ],
                "medical": [
                    {"name": "Atorvastatin", "dosage": "20mg", "frequency": "Once Daily (Evening)", "note": "Lipid management protocol"},
                    {"name": "Lisinopril", "dosage": "5mg", "frequency": "Once Daily (Morning)", "note": "ACE inhibition for BP control"},
                    {"name": "Aspirin", "dosage": "75mg", "frequency": "Once Daily", "note": "Anti-platelet therapy"}
                ],
                "precautions": [
                    "Monitor for sudden weight gain (>1kg in 24h).",
                    "Immediate ER visit if chest pressure or dyspnea occurs.",
                    "Avoid NSAIDs (Ibuprofen/Naproxen) as they worsen heart failure."
                ]
            },
            "diabetes": {
                "lifestyle": [
                    "Complex carbohydrate monitoring (Glycemic Index focus).",
                    "Consistent meal timing to stabilize serum glucose.",
                    "Hydration: Minimum 2.5L water daily to support kidney function.",
                    "Daily foot inspections to monitor for neuropathy/ulcers."
                ],
                "daily_routine": [
                    "07:30 AM: Fasting blood glucose check.",
                    "08:00 AM: High-protein breakfast + Medication.",
                    "12:30 PM: 15-minute post-meal brisk walk.",
                    "09:00 PM: Evening glucose log and pre-rest hydration."
                ],
                "medical": [
                    {"name": "Metformin", "dosage": "500mg", "frequency": "Twice Daily (With Meals)", "note": "Insulin sensitivity enhancement"},
                    {"name": "Glipizide", "dosage": "5mg", "frequency": "Once Daily (Morning)", "note": "Pancreatic stimulation"},
                    {"name": "Vitamin B12", "dosage": "1000mcg", "frequency": "Once Daily", "note": "Counteract Metformin depletion"}
                ],
                "precautions": [
                    "Carry rapid-acting glucose (tabs/juice) for hypoglycemia.",
                    "Monitor for 'Kussmaul breathing' or fruity breath (DKA risk).",
                    "Avoid high-impact exercise if retinopathy is present."
                ]
            },
            "mental": {
                "lifestyle": [
                    "Strict sleep hygiene: 8 hours consistent rest cycle.",
                    "Alcohol and stimulant avoidance to stabilize neurotransmitters.",
                    "Social engagement: Minimum 1 meaningful interaction daily.",
                    "Nutritional support: Omega-3 and Magnesium rich diet."
                ],
                "daily_routine": [
                    "07:00 AM: Exposure to 30 mins of natural morning light.",
                    "09:00 AM: Guided cognitive reframing or journaling.",
                    "05:00 PM: Screen-free period and light physical movement.",
                    "10:00 PM: Deep breathing exercises and digital detox."
                ],
                "medical": [
                    {"name": "Sertraline", "dosage": "50mg", "frequency": "Once Daily (Morning)", "note": "SSRI therapeutic baseline"},
                    {"name": "Melatonin", "dosage": "3mg", "frequency": "30 mins before rest", "note": "Circadian rhythm regulation"},
                    {"name": "Magnesium Glycinate", "dosage": "200mg", "frequency": "Once Daily (Evening)", "note": "Anxiolytic support"}
                ],
                "precautions": [
                    "Monitor for sudden changes in mood or ideation.",
                    "Avoid erratic caffeine intake as it mimics panic symptoms.",
                    "Consistent therapeutic check-ins are mandatory."
                ]
            }
        }

    def get_recommendations(self, disease_type: str):
        # Normalize disease type
        dt = disease_type.lower()
        if "heart" in dt: key = "heart"
        elif "diabet" in dt: key = "diabetes"
        elif "mental" in dt or "depress" in dt or "anxiety" in dt: key = "mental"
        else: return self._get_default_protocol()

        return self.protocols.get(key, self._get_default_protocol())

    def _get_default_protocol(self):
        return {
            "lifestyle": ["Maintain clinical baseline and monitor symptoms."],
            "daily_routine": ["08:00 AM: Vital signs check.", "08:00 PM: Health log update."],
            "medical": [
                {"name": "Clinical Therapy", "dosage": "As Directed", "frequency": "Daily", "note": "Primary Care"}
            ],
            "precautions": ["Consult medical professional if symptoms persistent."]
        }
