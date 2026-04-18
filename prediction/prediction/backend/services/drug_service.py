import json
import os
import csv
from difflib import get_close_matches

class DrugIntelligenceService:
    def __init__(self):
        self.drug_map = {}
        self.interactions = {}  # Mock memory map for dangerous combinatorics
        self.load_datasets()

    def load_datasets(self):
        """Loads available datasets safely."""
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'raw', 'drugs_for_common_treatments.csv')
        try:
            with open(csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # skip header
                for row in reader:
                    if len(row) >= 2:
                        disease = str(row[0]).lower().strip()
                        drug = str(row[1]).lower().strip()
                        if disease not in self.drug_map:
                            self.drug_map[disease] = []
                        if drug not in self.drug_map[disease]:
                            self.drug_map[disease].append(drug)
        except Exception as e:
            print(f"Warning: Drug Intelligence DB failed to load: {e}")

        # Static Mock Dangerous Combinations
        self.interactions = {
            "metformin": ["contrast dye", "alcohol"],
            "lisinopril": ["potassium", "aliskiren"],
            "ibuprofen": ["aspirin", "warfarin", "lisinopril"]
        }

        # Static Mock Drug Details
        self.drug_details = {
            "metformin": {
                "usage": "Controls high blood sugar.",
                "side_effects": ["Nausea", "Vomiting", "Upset stomach"],
                "alternatives": ["Glipizide", "Insulin"]
            },
            "lisinopril": {
                "usage": "Treats high blood pressure.",
                "side_effects": ["Dry cough", "Dizziness"],
                "alternatives": ["Losartan", "Amlodipine"]
            }
        }

    def evaluate_prescription(self, extracted_drugs, disease_context):
        """
        Takes extracted NLP drug names and checks interactions, relevancy, and details.
        """
        valid_drugs = self.drug_map.get(disease_context.lower(), ["metformin", "insulin", "glipizide"])
        
        matched_drugs = []
        dangerous_interactions = []
        details = {}
        typo_suggestions = {}

        try:
            import rapidfuzz
            from rapidfuzz import process, fuzz
            use_rapidfuzz = True
        except ImportError:
            use_rapidfuzz = False

        for drug in extracted_drugs:
            best_match = None
            if use_rapidfuzz:
                result = rapidfuzz.process.extractOne(drug.lower(), valid_drugs, scorer=rapidfuzz.fuzz.WRatio)
                if result and result[1] >= 70:  # 70% match threshold
                    best_match = result[0]
            else:
                match = get_close_matches(drug.lower(), valid_drugs, n=1, cutoff=0.7)
                if match:
                    best_match = match[0]

            if best_match:
                matched_drugs.append(best_match)
                if best_match != drug.lower():
                    typo_suggestions[drug] = f"Did you mean {best_match.capitalize()}?"
            else:
                matched_drugs.append(drug) # Not standard list, but keeping it
            
            # 2. Interactions Check
            check_drug = best_match if best_match else drug.lower()
            for interacting_med in self.interactions.get(check_drug, []):
                if interacting_med in [d.lower() for d in extracted_drugs]:
                    dangerous_interactions.append(f"{check_drug.capitalize()} clashes with {interacting_med.capitalize()}")

            # 3. Fetch drug intelligence profiles
            if check_drug in self.drug_details:
                details[check_drug] = self.drug_details[check_drug]

        return {
            "matched_drugs": list(set(matched_drugs)),
            "typo_suggestions": typo_suggestions,
            "suggestions": valid_drugs[:3] if valid_drugs else [],
            "drug_interactions": list(set(dangerous_interactions)),
            "drug_details": details
        }
