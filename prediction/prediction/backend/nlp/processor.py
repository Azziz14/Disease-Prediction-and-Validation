"""
NLP Processor with Medical Zero-Shot Classification
- spaCy NER: Extracts drug names + symptoms from prescription text
- Zero-shot classification for medical intent (instead of SST-2 sentiment)
- Dosage extraction with regex patterns
- Frequency extraction (BID, TID, PRN, etc.)
"""

import re
import spacy
from transformers import pipeline as hf_pipeline


# Expanded drug and symptom lexicons
KNOWN_DRUGS = {
    "metformin", "glipizide", "insulin", "lisinopril", "amoxicillin",
    "atorvastatin", "amlodipine", "losartan", "omeprazole", "sertraline",
    "aspirin", "ibuprofen", "acetaminophen", "prednisone", "warfarin",
    "simvastatin", "levothyroxine", "albuterol", "gabapentin", "furosemide",
    "hydrochlorothiazide", "clopidogrel", "pantoprazole", "ranitidine",
    "ciprofloxacin", "azithromycin", "doxycycline", "fluoxetine",
    "escitalopram", "duloxetine", "venlafaxine", "aripiprazole",
    "quetiapine", "risperidone", "clonazepam", "diazepam", "lorazepam",
    "tramadol", "morphine", "oxycodone", "naproxen", "celecoxib",
    "pioglitazone", "sitagliptin", "empagliflozin", "dapagliflozin",
    "liraglutide", "semaglutide", "canagliflozin"
}

KNOWN_SYMPTOMS = {
    "headache", "fever", "nausea", "vomiting", "fatigue", "dizziness",
    "chest pain", "shortness of breath", "cough", "diarrhea", "constipation",
    "abdominal pain", "joint pain", "muscle pain", "back pain", "insomnia",
    "anxiety", "depression", "numbness", "tingling", "blurred vision",
    "frequent urination", "excessive thirst", "weight loss", "weight gain",
    "swelling", "rash", "itching", "palpitations", "sweating",
    "vsd", "septal defect", "down syndrome", "congenital", "surgery",
    "cardiac surgery", "pediatric surgery", "surgical plan"
}

# Dosage extraction patterns
DOSAGE_PATTERN = re.compile(
    r'(\d+(?:\.\d+)?)\s*(mg|ml|mcg|g|units?|iu|tablets?|capsules?|drops?)',
    re.IGNORECASE
)

FREQUENCY_PATTERN = re.compile(
    r'(once|twice|thrice|one|two|three|four)\s*(daily|a day|per day|times?\s*(?:a|per)?\s*day)|'
    r'(q\d+h|bid|tid|qid|prn|qd|qhs|stat|q\.?\s*\d+\s*h)',
    re.IGNORECASE
)


class NLPProcessor:
    def __init__(self):
        print("Loading spaCy NLP model...")
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess
            print("Downloading en_core_web_sm...")
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"],
                           capture_output=True)
            self.nlp = spacy.load("en_core_web_sm")

        # Use zero-shot classification instead of SST-2 sentiment
        print("Loading zero-shot medical text classifier...")
        self.classifier = None
        try:
            self.classifier = hf_pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            print("  [OK] Zero-shot classifier loaded (BART-MNLI)")
        except Exception as e:
            print(f"  [ERROR] Zero-shot classifier failed: {e}")
            # Fallback to simple DistilBERT sentiment
            try:
                self.classifier = hf_pipeline(
                    "text-classification",
                    model="distilbert-base-uncased-finetuned-sst-2-english"
                )
                self._is_zero_shot = False
                print("  -> Fallback to DistilBERT sentiment")
            except Exception as e2:
                print(f"  [ERROR] All classifiers failed: {e2}")
                self._is_zero_shot = False

        self._is_zero_shot = hasattr(self.classifier, '__call__') and \
            'zero-shot' in str(type(self.classifier)).lower() if self.classifier else False

    def process_prescription(self, text: str) -> dict:
        """
        Full NLP analysis with zero-shot medical classification.
        """
        if not text or len(text.strip()) == 0:
            return {
                "drugs": [],
                "symptoms": [],
                "entities": {},
                "is_valid": False,
                "context": "Missing Prescription",
                "confidence": 0.0
            }

        # 1. spaCy NER
        doc = self.nlp(text)
        ner_entities = {}
        for ent in doc.ents:
            label = ent.label_
            if label not in ner_entities:
                ner_entities[label] = []
            if ent.text not in ner_entities[label]:
                ner_entities[label].append(ent.text)

        # 2. Drug extraction (NER + lexicon matching)
        ner_drugs = [ent.text for ent in doc.ents if ent.label_ in ('PRODUCT', 'ORG', 'GPE')]
        words = text.lower().replace(',', ' ').replace('.', ' ').replace(';', ' ').split()
        lexicon_drugs = [w for w in words if w in KNOWN_DRUGS]

        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        bigram_drugs = [b for b in bigrams if b in KNOWN_DRUGS]
        all_drugs = list(set([d.lower() for d in ner_drugs] + lexicon_drugs + bigram_drugs))

        # 3. Symptom extraction
        symptoms = []
        text_lower = text.lower()
        for symptom in KNOWN_SYMPTOMS:
            if symptom in text_lower:
                symptoms.append(symptom)

        # 4. Dosage extraction
        dosages = DOSAGE_PATTERN.findall(text)
        dosage_list = [f"{amount} {unit}" for amount, unit in dosages]

        # 5. Frequency extraction
        frequencies = FREQUENCY_PATTERN.findall(text)
        freq_list = [f for group in frequencies for f in group if f]

        # 6. Medical intent classification (zero-shot or fallback)
        classification, confidence, is_valid = self._classify_medical_text(text, all_drugs)

        return {
            "drugs": all_drugs,
            "symptoms": symptoms,
            "entities": ner_entities,
            "dosages": dosage_list,
            "frequencies": freq_list,
            "is_valid": is_valid,
            "context": classification,
            "confidence": confidence
        }

    def _classify_medical_text(self, text, drugs_found):
        """
        Classify medical intent using zero-shot classification.
        Candidate labels are medical-domain-specific.
        """
        if self.classifier is None:
            # Pure rule-based fallback
            has_drugs = len(drugs_found) > 0
            return (
                "Prescription" if has_drugs else "Non-Medical",
                0.8 if has_drugs else 0.3,
                has_drugs
            )

        try:
            if self._is_zero_shot:
                # Zero-shot classification with medical candidate labels
                candidate_labels = [
                    "medical prescription",
                    "patient complaint",
                    "clinical notes",
                    "surgical instruction",
                    "congenital assessment",
                    "non-medical text"
                ]
                result = self.classifier(text[:512], candidate_labels)
                classification = result['labels'][0]
                confidence = round(float(result['scores'][0]), 4)

                is_valid = classification != "non-medical text" or len(drugs_found) > 0 or any(kw in text.lower() for kw in ["bp", "ecg", "echo", "cardiology", "history of", "mg", "syndrome"])
                return classification, confidence, is_valid
            else:
                # SST-2 fallback
                result = self.classifier(text[:512])[0]
                classification = result['label']
                confidence = round(result['score'], 4)
                is_valid = not (classification == "NEGATIVE" and confidence > 0.85)
                return classification, confidence, is_valid

        except Exception as e:
            print(f"Classification error: {e}")
            has_drugs = len(drugs_found) > 0
            return "Prescription" if has_drugs else "Unknown", 0.5, has_drugs
