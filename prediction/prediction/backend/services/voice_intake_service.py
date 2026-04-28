"""
Voice Intake Service - NLP-based medical parameter extraction from natural speech.

Extracts numerical medical parameters (glucose, BP, BMI, age, etc.) from free-form
voice-transcribed text using regex patterns and keyword matching.

Missing values are imputed with medically-informed population defaults so the
prediction engine always receives a complete 8-feature input vector.
"""

import re
import logging

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════
# Parameter extraction patterns per disease
# Each pattern has: keyword aliases, regex to capture numbers, and a default value
# ══════════════════════════════════════════════════════════

DIABETES_PARAMS = [
    {
        "key": "glucose",
        "aliases": ["glucose", "blood sugar", "sugar level", "blood glucose", "fasting glucose", "sugar", "glycemia"],
        "pattern": r"(?:glucose|blood\s*sugar|sugar\s*level?|fasting\s*glucose|sugar|glycemia)\s*(?:is|of|at|level|reading|:)?\s*(\d+(?:\.\d+)?)",
        "default": 120,
        "unit": "mg/dL"
    },
    {
        "key": "bloodPressure",
        "aliases": ["blood pressure", "bp", "diastolic", "pressure"],
        "pattern": r"(?:blood\s*pressure|bp|diastolic|pressure)\s*(?:is|of|at|reading|:)?\s*(\d+(?:\.\d+)?)",
        "default": 72,
        "unit": "mmHg"
    },
    {
        "key": "bmi",
        "aliases": ["bmi", "body mass", "body mass index", "mass index"],
        "pattern": r"(?:bmi|body\s*mass\s*(?:index)?|mass\s*index)\s*(?:is|of|at|reading|:)?\s*(\d+(?:\.\d+)?)",
        "default": 26.0,
        "unit": "kg/m2"
    },
    {
        "key": "age",
        "aliases": ["age", "years old", "year old", "aged"],
        "pattern": r"(?:age\s*(?:is|of|:)?\s*(\d+)|(\d+)\s*years?\s*old|i\s*am\s*(\d+)|aged?\s*(\d+))",
        "default": 35,
        "unit": "years"
    },
    {
        "key": "insulin",
        "aliases": ["insulin", "insulin level"],
        "pattern": r"(?:insulin\s*(?:level|reading)?\s*(?:is|of|at|:)?\s*(\d+(?:\.\d+)?))",
        "default": 80,
        "unit": "uU/mL"
    },
    {
        "key": "skinThickness",
        "aliases": ["skin", "skin thickness", "tricep", "skin fold"],
        "pattern": r"(?:skin\s*(?:thickness|fold)?|tricep)\s*(?:is|of|at|:)?\s*(\d+(?:\.\d+)?)",
        "default": 29,
        "unit": "mm"
    },
    {
        "key": "pregnancies",
        "aliases": ["pregnancies", "pregnant", "pregnancy", "children", "kids"],
        "pattern": r"(?:pregnanc(?:ies|y)|pregnant|children|kids)\s*(?:is|of|at|:)?\s*(\d+)|(\d+)\s*(?:pregnanc(?:ies|y)|children|kids)",
        "default": 1,
        "unit": ""
    },
    {
        "key": "dpf",
        "aliases": ["dpf", "pedigree", "diabetes pedigree", "family history score", "genetic"],
        "pattern": r"(?:dpf|pedigree|diabetes\s*pedigree|family\s*history\s*score|genetic\s*score)\s*(?:is|of|at|:)?\s*(\d+(?:\.\d+)?)",
        "default": 0.47,
        "unit": ""
    },
]

HEART_PARAMS = [
    {
        "key": "age",
        "aliases": ["age", "years old", "year old"],
        "pattern": r"(?:age\s*(?:is|of|:)?\s*(\d+)|(\d+)\s*years?\s*old|i\s*am\s*(\d+)|aged?\s*(\d+))",
        "default": 50,
        "unit": "years"
    },
    {
        "key": "sex",
        "aliases": ["sex", "gender", "male", "female"],
        "pattern": r"(?:sex|gender)\s*(?:is|:)?\s*(male|female|man|woman|\d)",
        "default": 1,
        "unit": "",
        "map": {"male": 1, "man": 1, "female": 0, "woman": 0}
    },
    {
        "key": "chestPain",
        "aliases": ["chest pain", "angina", "chest"],
        "pattern": r"(?:chest\s*pain\s*(?:type)?\s*(?:is|of|:)?\s*(\d)|(?:typical|atypical|non.?anginal|asymptomatic)\s*(?:angina|pain)?)",
        "default": 0,
        "unit": "",
        "map": {"typical": 0, "atypical": 1, "non-anginal": 2, "nonanginal": 2, "asymptomatic": 3}
    },
    {
        "key": "restingBP",
        "aliases": ["blood pressure", "bp", "resting bp", "resting blood pressure", "systolic"],
        "pattern": r"(?:(?:resting\s*)?blood\s*pressure|(?:resting\s*)?bp|systolic)\s*(?:is|of|at|:)?\s*(\d+)",
        "default": 130,
        "unit": "mmHg"
    },
    {
        "key": "cholesterol",
        "aliases": ["cholesterol", "chol", "serum cholesterol"],
        "pattern": r"(?:cholesterol|chol|serum\s*cholesterol)\s*(?:is|of|at|level|reading|:)?\s*(\d+)",
        "default": 200,
        "unit": "mg/dL"
    },
    {
        "key": "fastingBS",
        "aliases": ["fasting blood sugar", "fasting sugar", "fasting bs"],
        "pattern": r"(?:fasting\s*(?:blood\s*)?sugar|fasting\s*bs)\s*(?:is|of|at|:)?\s*(?:(\d+)|yes|no|high|normal)",
        "default": 0,
        "unit": "",
        "map": {"yes": 1, "high": 1, "no": 0, "normal": 0}
    },
    {
        "key": "maxHR",
        "aliases": ["heart rate", "max heart rate", "maximum heart rate", "pulse", "hr"],
        "pattern": r"(?:(?:max(?:imum)?\s*)?heart\s*rate|pulse|hr)\s*(?:is|of|at|:)?\s*(\d+)",
        "default": 150,
        "unit": "bpm"
    },
    {
        "key": "exerciseAngina",
        "aliases": ["exercise angina", "exercise induced", "angina"],
        "pattern": r"(?:exercise\s*(?:induced\s*)?angina)\s*(?:is|:)?\s*(yes|no|1|0)",
        "default": 0,
        "unit": "",
        "map": {"yes": 1, "no": 0}
    },
]

MENTAL_PARAMS = [
    {
        "key": "age",
        "aliases": ["age", "years old"],
        "pattern": r"(?:age\s*(?:is|of|:)?\s*(\d+)|(\d+)\s*years?\s*old|i\s*am\s*(\d+))",
        "default": 30,
        "unit": "years"
    },
    {
        "key": "gender",
        "aliases": ["gender", "sex", "male", "female"],
        "pattern": r"(?:gender|sex)\s*(?:is|:)?\s*(male|female|man|woman|non.?binary|\d)",
        "default": 0,
        "unit": "",
        "map": {"male": 0, "man": 0, "female": 1, "woman": 1, "non-binary": 2, "nonbinary": 2}
    },
    {
        "key": "familyHistory",
        "aliases": ["family history", "family mental", "hereditary"],
        "pattern": r"(?:family\s*(?:history|mental)|hereditary)\s*(?:is|of|:)?\s*(yes|no|1|0)",
        "default": 0,
        "unit": "",
        "map": {"yes": 1, "no": 0}
    },
    {
        "key": "workInterfere",
        "aliases": ["work interfere", "work interference", "work affect"],
        "pattern": r"(?:work\s*(?:interfere|interference|affect))\s*(?:is|of|:)?\s*(never|rarely|sometimes|often|\d)",
        "default": 1,
        "unit": "",
        "map": {"never": 0, "rarely": 1, "sometimes": 2, "often": 3}
    },
    {
        "key": "sleepHours",
        "aliases": ["sleep", "sleep hours", "sleeping"],
        "pattern": r"(?:sleep(?:ing)?\s*(?:hours?)?\s*(?:is|of|at|:)?\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*hours?\s*(?:of\s*)?sleep)",
        "default": 7,
        "unit": "hours"
    },
    {
        "key": "stressLevel",
        "aliases": ["stress", "stress level"],
        "pattern": r"(?:stress\s*(?:level)?\s*(?:is|of|at|:)?\s*(\d+))",
        "default": 5,
        "unit": "/10"
    },
    {
        "key": "socialSupport",
        "aliases": ["social support", "support level", "support"],
        "pattern": r"(?:(?:social\s*)?support\s*(?:level)?\s*(?:is|of|at|:)?\s*(\d+))",
        "default": 5,
        "unit": "/10"
    },
    {
        "key": "treatmentSeeking",
        "aliases": ["treatment", "seeking treatment", "therapy"],
        "pattern": r"(?:(?:seeking\s*)?treatment|therapy)\s*(?:is|:)?\s*(yes|no|1|0)",
        "default": 0,
        "unit": "",
        "map": {"yes": 1, "no": 0}
    },
]

DISEASE_PARAMS = {
    "diabetes": DIABETES_PARAMS,
    "heart": HEART_PARAMS,
    "mental": MENTAL_PARAMS,
}

# ══════════════════════════════════════════════════════════
# AUTO MEDICATION SUGGESTIONS
# Tier-1 evidence-based medications with proper dosages
# ══════════════════════════════════════════════════════════

AUTO_MEDICATIONS = {
    "diabetes": {
        "High": [
            {"name": "Metformin", "dosage": "500mg", "frequency": "twice daily", "note": "First-line therapy for Type 2 Diabetes. Start low, titrate up to 2000mg/day."},
            {"name": "Glipizide", "dosage": "5mg", "frequency": "once daily before breakfast", "note": "Sulfonylurea for additional glycemic control."},
            {"name": "Empagliflozin", "dosage": "10mg", "frequency": "once daily", "note": "SGLT2 inhibitor with cardiovascular and renal benefits."},
        ],
        "Moderate": [
            {"name": "Metformin", "dosage": "500mg", "frequency": "once daily with dinner", "note": "First-line therapy. Monitor HbA1c in 3 months."},
            {"name": "Sitagliptin", "dosage": "100mg", "frequency": "once daily", "note": "DPP-4 inhibitor for moderate glucose elevation."},
        ],
        "Low": [
            {"name": "No pharmacological intervention required", "dosage": "-", "frequency": "-", "note": "Lifestyle modification sufficient. Recheck HbA1c in 6 months."},
        ],
    },
    "heart": {
        "High": [
            {"name": "Atorvastatin", "dosage": "40mg", "frequency": "once daily at bedtime", "note": "High-intensity statin for aggressive lipid lowering."},
            {"name": "Aspirin", "dosage": "81mg", "frequency": "once daily", "note": "Low-dose antiplatelet therapy for cardiovascular prevention."},
            {"name": "Lisinopril", "dosage": "10mg", "frequency": "once daily", "note": "ACE inhibitor for blood pressure and cardiac remodeling."},
            {"name": "Metoprolol", "dosage": "25mg", "frequency": "twice daily", "note": "Beta-blocker for rate control. Titrate to resting HR 55-65."},
        ],
        "Moderate": [
            {"name": "Atorvastatin", "dosage": "20mg", "frequency": "once daily at bedtime", "note": "Moderate-intensity statin therapy."},
            {"name": "Amlodipine", "dosage": "5mg", "frequency": "once daily", "note": "Calcium channel blocker for blood pressure control."},
        ],
        "Low": [
            {"name": "No pharmacological intervention required", "dosage": "-", "frequency": "-", "note": "Continue healthy diet and exercise. Annual lipid panel recommended."},
        ],
    },
    "mental": {
        "High": [
            {"name": "Sertraline (Zoloft)", "dosage": "50mg", "frequency": "once daily", "note": "First-line SSRI. Start at 50mg, may titrate to 200mg over 4-6 weeks."},
            {"name": "Hydroxyzine", "dosage": "25mg", "frequency": "as needed for acute anxiety", "note": "Non-addictive anxiolytic for acute episodes."},
            {"name": "Melatonin", "dosage": "3mg", "frequency": "30 min before bedtime", "note": "For circadian rhythm regulation if sleep is disrupted."},
        ],
        "Moderate": [
            {"name": "Escitalopram (Lexapro)", "dosage": "10mg", "frequency": "once daily", "note": "SSRI with favorable side-effect profile for moderate symptoms."},
            {"name": "Vitamin D3", "dosage": "2000 IU", "frequency": "once daily", "note": "Supplement for mood support. Deficiency correlates with depression."},
        ],
        "Low": [
            {"name": "No pharmacological intervention required", "dosage": "-", "frequency": "-", "note": "Consider cognitive behavioral therapy (CBT) and lifestyle optimization."},
        ],
    },
}


class VoiceIntakeService:
    """
    Extracts medical parameters from free-form voice/text input.
    Fills missing values with medically-informed defaults.
    Generates auto-medication suggestions when no prescription is provided.
    """

    def extract_parameters(self, text: str, disease: str) -> dict:
        """
        Parse transcribed speech and extract medical feature values.
        
        Returns:
            {
                "features": [8 numbers],
                "extracted": {"glucose": 150, ...},   # values found in speech
                "defaults_used": ["skinThickness", ...],  # values that were defaulted
                "confidence": 0.0-1.0,
                "raw_text": "..."
            }
        """
        text_lower = text.lower().strip()
        params = DISEASE_PARAMS.get(disease, DIABETES_PARAMS)
        
        extracted = {}
        defaults_used = []
        
        for param in params:
            value = self._extract_value(text_lower, param)
            if value is not None:
                extracted[param["key"]] = value
            else:
                extracted[param["key"]] = param["default"]
                defaults_used.append(param["key"])
        
        # Build the 8-feature vector in order
        features = [extracted[p["key"]] for p in params]
        
        # Confidence = ratio of extracted vs total params
        extraction_ratio = 1.0 - (len(defaults_used) / len(params))
        confidence = round(max(0.3, extraction_ratio), 2)
        
        return {
            "features": features,
            "extracted": extracted,
            "defaults_used": defaults_used,
            "extraction_confidence": confidence,
            "raw_text": text
        }
    
    def _extract_value(self, text: str, param: dict):
        """Extract a single parameter value from text using regex."""
        try:
            pattern = param["pattern"]
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Get first non-None group
                for group in match.groups():
                    if group is not None:
                        group = group.strip().lower()
                        # Check if it's a mapped value (e.g., "male" -> 1)
                        if "map" in param and group in param["map"]:
                            return param["map"][group]
                        try:
                            val = float(group)
                            return int(val) if val == int(val) else val
                        except ValueError:
                            if "map" in param and group in param["map"]:
                                return param["map"][group]
                            continue
            
            # Try simple keyword + number proximity (fallback)
            for alias in param.get("aliases", []):
                # Find alias in text, look for nearby number
                idx = text.find(alias)
                if idx >= 0:
                    # Look for a number within 30 chars after the keyword
                    after = text[idx + len(alias):idx + len(alias) + 40]
                    num_match = re.search(r"(\d+(?:\.\d+)?)", after)
                    if num_match:
                        val = float(num_match.group(1))
                        return int(val) if val == int(val) else val
                        
        except Exception as e:
            logger.debug(f"Extraction error for {param['key']}: {e}")
        
        return None
    
    def get_auto_medications(self, disease: str, risk: str) -> list:
        """
        Get evidence-based medication suggestions with proper dosages.
        Used when the user does not provide a prescription.
        """
        risk_key = risk if risk in ["High", "Moderate", "Low"] else "Moderate"
        meds = AUTO_MEDICATIONS.get(disease, AUTO_MEDICATIONS["diabetes"])
        return meds.get(risk_key, meds.get("Low", []))
    
    def get_extraction_summary(self, extracted: dict, defaults_used: list, params: list) -> list:
        """Generate a human-readable summary of what was extracted vs defaulted."""
        summary = []
        for p in params:
            key = p["key"]
            val = extracted.get(key, p["default"])
            unit = p.get("unit", "")
            if key in defaults_used:
                summary.append(f"{key}: {val} {unit} (auto-filled default)")
            else:
                summary.append(f"{key}: {val} {unit} (extracted from voice)")
        return summary

    def detect_disease(self, text: str) -> str:
        """
        Intelligent autonomous disease detection from free-form voice text.
        Uses weighted keyword & symptom proximity scoring to determine the
        most likely clinical context without user intervention.
        
        Returns: 'diabetes', 'heart', or 'mental'
        """
        text_lower = text.lower()
        
        # Weighted keyword dictionaries — higher weight = stronger signal
        DISEASE_SIGNALS = {
            "diabetes": {
                # Direct mentions (weight 10)
                "diabetes": 10, "diabetic": 10, "type 2": 8, "type 1": 8,
                # Core biomarkers (weight 6)
                "glucose": 6, "blood sugar": 6, "sugar level": 6, "insulin": 6,
                "hba1c": 7, "a1c": 7, "glycemic": 6, "hyperglycemia": 8,
                # Symptoms (weight 4)
                "frequent urination": 5, "thirsty": 4, "thirst": 4, "blurred vision": 4,
                "weight loss": 3, "fatigue": 2, "numbness": 3, "tingling": 3,
                # Related terms (weight 2-3)
                "bmi": 3, "obesity": 3, "overweight": 3, "pancreas": 4,
                "metformin": 7, "glipizide": 7, "endocrinologist": 6,
                "sugar": 3, "carbohydrate": 2, "glycemia": 5,
                "pedigree": 4, "pregnancies": 3, "skin thickness": 3,
            },
            "heart": {
                # Direct mentions (weight 10)
                "heart": 8, "cardiac": 10, "cardiovascular": 10, "heart disease": 10,
                "heart attack": 10, "coronary": 9,
                # Core biomarkers (weight 6)
                "cholesterol": 6, "blood pressure": 5, "bp": 4, "systolic": 6,
                "diastolic": 6, "ecg": 7, "ekg": 7, "electrocardiogram": 8,
                # Symptoms (weight 4-5)
                "chest pain": 7, "angina": 7, "shortness of breath": 5,
                "palpitation": 6, "arrhythmia": 7, "irregular heartbeat": 7,
                # Related terms
                "statin": 6, "aspirin": 4, "atorvastatin": 7, "lisinopril": 7,
                "metoprolol": 7, "amlodipine": 7,
                "pulse": 3, "heart rate": 4, "tachycardia": 6, "bradycardia": 6,
                "exercise angina": 7, "resting bp": 5,
            },
            "mental": {
                # Direct mentions (weight 10)
                "mental health": 10, "depression": 10, "anxiety": 10,
                "mental illness": 10, "psychiatric": 9, "psychological": 8,
                # Core signals (weight 5-7)
                "stress": 5, "stressed": 5, "panic attack": 8, "panic": 5,
                "insomnia": 6, "sleep disorder": 6, "bipolar": 9, "ptsd": 9,
                "ocd": 8, "adhd": 7, "schizophrenia": 10,
                # Symptoms (weight 3-5)
                "sad": 4, "hopeless": 5, "worthless": 5, "suicide": 10, "suicidal": 10,
                "can't sleep": 5, "sleep": 3, "nightmare": 4, "crying": 4,
                "lonely": 4, "isolation": 5, "anxious": 6, "worry": 4, "worrying": 4,
                "mood": 5, "mood swing": 6, "irritable": 4, "anger": 3,
                # Related terms
                "therapy": 5, "therapist": 5, "counseling": 5, "psychiatrist": 7,
                "sertraline": 7, "fluoxetine": 7, "escitalopram": 7,
                "social support": 4, "family history": 3, "work interfere": 5,
                "stress level": 5, "burnout": 5,
            }
        }
        
        scores = {}
        for disease, keywords in DISEASE_SIGNALS.items():
            score = 0
            for keyword, weight in keywords.items():
                # Count occurrences and multiply by weight
                count = text_lower.count(keyword)
                if count > 0:
                    score += weight * count
            scores[disease] = score
        
        logger.info(f"[AUTO-DETECT] Disease scores: {scores}")
        
        # Pick highest score; if all zero, default to diabetes (most common)
        best = max(scores, key=scores.get)
        if scores[best] == 0:
            logger.info("[AUTO-DETECT] No disease signals found, defaulting to diabetes")
            return "diabetes"
        
        logger.info(f"[AUTO-DETECT] Detected disease: {best} (score: {scores[best]})")
        return best

