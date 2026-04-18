import csv
import os
from difflib import get_close_matches

drug_map = {}

# We specify absolute or relative carefully, bypassing pandas
csv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'drugs_for_common_treatments.csv')

try:
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            if len(row) >= 2:
                disease = str(row[0]).lower().strip()
                drug = str(row[1]).lower().strip()
                if disease not in drug_map:
                    drug_map[disease] = []
                drug_map[disease].append(drug)
except FileNotFoundError:
    print(f"Warning: Could not load mock drugs database at {csv_path}")

def validate_prescription(disease, prescription):
    words = prescription.lower().split()
    valid_drugs = drug_map.get(disease.lower(), [])

    matched = []
    for w in words:
        match = get_close_matches(w, valid_drugs, n=1, cutoff=0.7)
        if match:
            matched.append(match[0])

    # If dataset wasn't found or parsed, return mock fallback
    if not valid_drugs:
        valid_drugs = ["metformin", "insulin", "glipizide"]

    return {
        "matched_drugs": list(set(matched)),
        "suggestions": valid_drugs[:3]
    }