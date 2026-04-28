"""
Clinical Index Registry
The single 'Source of Truth' for biomarker feature positioning across the entire lifecycle 
(Frontend, Voice Intake, OCR, ML Preprocessing, and Clinical AI Narrative).
"""

class ClinicalRegistry:
    # DIABETES (Pima Dataset Standard)
    # Indices: 0: Preg, 1: Gluc, 2: BP, 3: Skin, 4: Ins, 5: BMI, 6: DPF, 7: Age
    DIABETES_INDICES = {
        "pregnancies": 0,
        "glucose": 1,
        "blood_pressure": 2,
        "skin_thickness": 3,
        "insulin": 4,
        "bmi": 5,
        "pedigree": 6,
        "age": 7
    }

    # HEART (Standard Clinical 8-feature subset)
    # Indices: 0: Age, 1: Sex, 2: CP, 3: TrestBPS, 4: Chol, 5: FBS, 6: RestECG, 7: Thalach
    HEART_INDICES = {
        "age": 0,
        "gender": 1,
        "chest_pain": 2,
        "blood_pressure": 3,
        "cholesterol": 4,
        "fasting_bs": 5,
        "resting_ecg": 6,
        "max_heart_rate": 7
    }

    # MENTAL HEALTH (8-feature behavioral subset)
    # Indices: 0: Age, 1: Gender, 2: FamHist, 3: WorkInt, 4: Sleep, 5: Stress, 6: Support, 7: Seeking
    MENTAL_INDICES = {
        "age": 0,
        "gender": 1,
        "family_history": 2,
        "work_interference": 3,
        "sleep_hours": 4,
        "stress_level": 5,
        "social_support": 6,
        "treatment_seeking": 7
    }

    @classmethod
    def get_indices(cls, disease_type: str):
        if disease_type.lower() == "diabetes":
            return cls.DIABETES_INDICES
        if disease_type.lower() == "heart":
            return cls.HEART_INDICES
        if disease_type.lower() == "mental":
            return cls.MENTAL_INDICES
        return cls.DIABETES_INDICES # Fallback
