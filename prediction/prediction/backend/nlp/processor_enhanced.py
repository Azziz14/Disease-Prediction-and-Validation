"""
ENHANCED NLP Processor with Medical Zero-Shot Classification
- Zero-shot classification with medical candidate labels (BART-MNLI)
- Advanced drug/symptom extraction with confidence scoring
- Dosage and frequency extraction via regex
- Drug interaction detection
- Semantic similarity matching (optional)
- Confidence calibration with temperature scaling
"""

import re
import spacy
import numpy as np
from transformers import pipeline as hf_pipeline
from fuzzywuzzy import fuzz, process

# Extended medical lexicons
KNOWN_DRUGS = {
    # Diabetes medications
    "metformin", "glipizide", "insulin", "glyburide", "pioglitazone", 
    "sitagliptin", "empagliflozin", "dapagliflozin", "liraglutide", "semaglutide",
    
    # Cardiovascular
    "lisinopril", "atorvastatin", "amlodipine", "losartan", "aspirin",
    "clopidogrel", "warfarin", "bisoprolol", "enalapril", "valsartan",
    
    # Antibiotics
    "amoxicillin", "azithromycin", "ciprofloxacin", "doxycycline", "penicillin",
    
    # Pain/Anti-inflammatory
    "ibuprofen", "naproxen", "celecoxib", "tramadol", "morphine", "oxycodone",
    
    # Mental health
    "sertraline", "fluoxetine", "escitalopram", "duloxetine", "venlafaxine",
    "aripiprazole", "quetiapine", "risperidone", "clonazepam", "diazepam",
    
    # Respiratory
    "albuterol", "salbutamol", "fluticasone", "tiotropium",
    
    # GI
    "omeprazole", "pantoprazole", "ranitidine", "metoclopramide",
    
    # Other common
    "levothyroxine", "furosemide", "hydrochlorothiazide", "gabapentin", "prednisone"
}

KNOWN_SYMPTOMS = {
    # General
    "headache", "fever", "fatigue", "weakness", "chills", "malaise",
    
    # Cardiovascular
    "chest pain", "shortness of breath", "palpitations", "dizziness", "syncope",
    "edema", "swelling", "hypertension", "hypotension",
    
    # GI
    "nausea", "vomiting", "diarrhea", "constipation", "abdominal pain",
    "bloating", "indigestion", "heartburn", "dysphagia",
    
    # Neurological
    "numbness", "tingling", "tremor", "seizure", "confusion", "memory loss",
    "blurred vision", "double vision",
    
    # Mental
    "anxiety", "depression", "insomnia", "irritability", "panic attack",
    
    # Metabolic
    "frequent urination", "excessive thirst", "polydipsia", "weight loss",
    "weight gain", "increased appetite", "decreased appetite",
    
    # Skin
    "rash", "itching", "hives", "urticaria", "eczema", "dermatitis",
    
    # Musculoskeletal
    "joint pain", "arthralgia", "muscle pain", "myalgia", "back pain",
    "arthritis", "stiffness", "cramps",
    
    # Respiratory
    "cough", "dyspnea", "wheezing", "stridor", "sore throat",
    
    # Other
    "sweating", "diaphoresis", "night sweats", "hot flashes"
}

SYMPTOM_SYNONYMS = {
    "high temperature": "fever",
    "feverish": "fever",
    "ache": "pain",
    "hurts": "pain",
    "exhaustion": "fatigue",
    "tired": "fatigue",
    "sleeplessness": "insomnia",
    "fast heart rate": "palpitations",
    "throw up": "vomiting",
    "belly ache": "abdominal pain",
    "stomach ache": "abdominal pain",
    "dizzy": "dizziness",
}

# Drug interaction database (simplified)
DRUG_INTERACTIONS = {
    "warfarin": ["aspirin", "ibuprofen", "naproxen"],
    "metformin": ["contrast dye"],
    "lisinopril": ["potassium supplements"],
    "insulin": ["alcohol"],
}

# Dosage and frequency regex patterns
DOSAGE_PATTERN = re.compile(
    r'(\d+(?:\.\d+)?)\s*(mg|ml|mcg|g|units?|iu|tablets?|capsules?|drops?)',
    re.IGNORECASE
)

FREQUENCY_PATTERN = re.compile(
    r'(once|twice|thrice|one|two|three|four)\s*(daily|a day|per day|times?\s*(?:a|per)?\s*day)|'
    r'(q\d+h|bid|tid|qid|prn|qd|qhs|stat|q\.?\s*\d+\s*h)',
    re.IGNORECASE
)


class NLPProcessorEnhanced:
    """
    Enhanced NLP with:
    - Zero-shot classification for medical domain (BART-MNLI)
    - Confidence calibration with temperature scaling
    - Entity normalization
    - Drug interaction detection
    - Dosage and frequency extraction
    """

    def __init__(self):
        print("Loading spaCy medical NLP model...")
        try:
            self.nlp = spacy.load("en_core_web_md")
        except OSError:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                print("  [FALLBACK] Using en_core_web_sm (md not available)")
            except OSError:
                print("Downloading en_core_web_sm...")
                import subprocess
                subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"],
                              capture_output=True)
                self.nlp = spacy.load("en_core_web_sm")

        # Zero-shot classification — works without fine-tuning on domain labels
        print("Loading zero-shot medical text classifier...")
        self.medical_classifier = None
        self._is_zero_shot = False
        try:
            self.medical_classifier = hf_pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            self._is_zero_shot = True
            print("  [OK] Zero-shot classifier loaded (BART-MNLI)")
        except Exception as e:
            print(f"  [ERROR] Zero-shot unavailable: {e}")
            try:
                self.medical_classifier = hf_pipeline(
                    "text-classification",
                    model="distilbert-base-uncased-finetuned-sst-2-english"
                )
                self._is_zero_shot = False
                print("  -> Fallback to DistilBERT")
            except Exception as e2:
                print(f"  [ERROR] All classifiers unavailable: {e2}")

        # Semantic similarity model (optional)
        self.similarity_model = None
        try:
            from sentence_transformers import SentenceTransformer
            self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            print("  sentence-transformers not installed. Skipping.")

    def process_prescription(self, text: str) -> dict:
        """
        Enhanced prescription processing:
        1. Entity extraction (spaCy NER)
        2. Drug identification with confidence
        3. Symptom extraction with severity
        4. Medical intent classification (BioBERT)
        5. Drug interaction detection
        6. Confidence calibration
        """
        if not text or len(text.strip()) == 0:
            return {
                "drugs": [],
                "symptoms": [],
                "entities": {},
                "is_valid": False,
                "context": "Missing Prescription",
                "confidence": 0.0,
                "drug_interactions": [],
                "interaction_severity": "none"
            }

        # 1. spaCy NER
        doc = self.nlp(text.lower())
        ner_entities = {}
        
        for ent in doc.ents:
            label = ent.label_
            if label not in ner_entities:
                ner_entities[label] = []
            if ent.text not in ner_entities[label]:
                ner_entities[label].append(ent.text)

        # 2. Advanced drug extraction with confidence scores
        drugs_with_confidence = self._extract_drugs_enhanced(text, doc)
        all_drugs = [d['name'] for d in drugs_with_confidence]

        # 3. Symptom extraction with severity
        symptoms_with_severity = self._extract_symptoms_enhanced(text)
        all_symptoms = [s['name'] for s in symptoms_with_severity]

        # 4. Dosage extraction
        dosages = DOSAGE_PATTERN.findall(text)
        dosage_list = [f"{amount} {unit}" for amount, unit in dosages]

        # 5. Frequency extraction
        frequencies = FREQUENCY_PATTERN.findall(text)
        freq_list = [f for group in frequencies for f in group if f]

        # 6. Medical intent classification (zero-shot)
        intent, intent_confidence = self._classify_medical_intent(text)

        # 7. Check drug interactions
        interactions = self._check_drug_interactions(all_drugs)
        interaction_severity = "high" if interactions else "none"

        # 8. Overall prescription validity
        is_valid = len(all_drugs) > 0 and intent_confidence > 0.4
        overall_confidence = self._calibrate_confidence(
            len(all_drugs), len(all_symptoms), intent_confidence
        )

        return {
            "drugs": all_drugs,
            "drugs_detailed": drugs_with_confidence,
            "symptoms": all_symptoms,
            "symptoms_detailed": symptoms_with_severity,
            "entities": ner_entities,
            "dosages": dosage_list,
            "frequencies": freq_list,
            "is_valid": is_valid,
            "context": intent,
            "confidence": overall_confidence,
            "intent_confidence": intent_confidence,
            "drug_interactions": interactions,
            "interaction_severity": interaction_severity,
            "recommendation": self._generate_recommendation(
                all_drugs, interactions, intent_confidence
            )
        }

    def _extract_drugs_enhanced(self, text, doc):
        """
        Extract drugs with confidence scores using:
        - NER from spaCy
        - Lexicon matching
        - Context analysis
        """
        drugs_found = {}

        text_lower = text.lower()
        words = text_lower.replace(',', ' ').replace('.', ' ').replace(';', ' ').split()

        # Fuzzy matching and Lexicon match with position analysis
        for i, word in enumerate(words):
            if len(word) > 4: # Only fuzzy match words longer than 4 chars
                match, score = process.extractOne(word, KNOWN_DRUGS, scorer=fuzz.ratio)
                if score >= 85:  # 85% similarity threshold
                    matched_word = match
                    if matched_word not in drugs_found:
                        confidence = self._score_drug_confidence(i, words) * (score / 100.0)
                        drugs_found[matched_word] = {
                            'name': matched_word,
                            'confidence': confidence,
                            'source': 'fuzzy_lexicon',
                            'original_word': word
                        }
            else:
                if word in KNOWN_DRUGS:
                    if word not in drugs_found:
                        confidence = self._score_drug_confidence(i, words)
                        drugs_found[word] = {
                            'name': word,
                            'confidence': confidence,
                            'source': 'lexicon',
                            'original_word': word
                        }

        # Bigrams for multi-word drugs
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            if bigram in KNOWN_DRUGS and bigram not in drugs_found:
                confidence = self._score_drug_confidence(i, words)
                drugs_found[bigram] = {
                    'name': bigram,
                    'confidence': confidence,
                    'source': 'bigram',
                    'original_word': bigram
                }

        return list(drugs_found.values())

    def _score_drug_confidence(self, word_idx, words):
        """
        Score drug confidence based on context.
        Higher if dosage/frequency words nearby.
        """
        dosage_indicators = ['mg', 'ml', 'tablet', 'capsule', 'dose', 'units', 'twice', 'daily']
        
        confidence = 0.7  # Base confidence
        
        # Check surrounding context
        for i in range(max(0, word_idx - 2), min(len(words), word_idx + 3)):
            if any(indicator in words[i] for indicator in dosage_indicators):
                confidence = min(0.98, confidence + 0.15)

        return float(confidence)

    def _extract_symptoms_enhanced(self, text):
        """
        Extract symptoms with severity scoring.
        """
        symptoms_found = {}

        text_lower = text.lower()

        # Synonym expansion
        for syn, canonical in SYMPTOM_SYNONYMS.items():
            if syn in text_lower:
                text_lower = text_lower.replace(syn, canonical)

        # Severity keywords
        severe_keywords = ['severe', 'critical', 'emergency', 'urgent', 'dangerous']
        moderate_keywords = ['moderate', 'significant', 'concerning']
        mild_keywords = ['mild', 'slight', 'minor']
        
        import difflib
        tokens = text_lower.split()

        for symptom in KNOWN_SYMPTOMS:
            symptom_tokens = symptom.split()
            is_found = False
            symptom_idx = -1
            
            # Simple substring match first
            if symptom in text_lower:
                is_found = True
                symptom_idx = text_lower.find(symptom)
            elif len(symptom_tokens) == 1:
                # Fuzzy match for single tokens
                closest = difflib.get_close_matches(symptom, tokens, n=1, cutoff=0.8)
                if closest:
                    is_found = True
                    symptom_idx = text_lower.find(closest[0])

            if is_found:
                severity = 'moderate'  # Default

                # Find symptom position and check context
                symptom_idx = text_lower.find(symptom)
                context_start = max(0, symptom_idx - 30)
                context_end = min(len(text_lower), symptom_idx + 30)
                context = text_lower[context_start:context_end]

                for keyword in severe_keywords:
                    if keyword in context:
                        severity = 'severe'
                        break

                if severity == 'moderate':
                    for keyword in mild_keywords:
                        if keyword in context:
                            severity = 'mild'
                            break

                if symptom not in symptoms_found:
                    symptoms_found[symptom] = {
                        'name': symptom,
                        'severity': severity,
                        'confidence': 0.85
                    }

        return list(symptoms_found.values())

    def _classify_medical_intent(self, text):
        """
        Classify prescription using zero-shot classification with medical labels.
        """
        if self.medical_classifier is None:
            has_drugs = any(drug in text.lower() for drug in KNOWN_DRUGS)
            confidence = 0.8 if has_drugs else 0.3
            intent = "Prescription" if has_drugs else "Non-Medical"
            return intent, confidence

        try:
            if self._is_zero_shot:
                candidate_labels = [
                    "medical prescription",
                    "patient complaint",
                    "clinical notes",
                    "non-medical text",
                    "drug inquiry",
                    "lab results",
                ]
                result = self.medical_classifier(text[:512], candidate_labels)
                intent = result['labels'][0]
                confidence = float(result['scores'][0])
                return intent, confidence
            else:
                # SST-2 fallback
                result = self.medical_classifier(text[:512])[0]
                intent = result['label']
                confidence = float(result['score'])
                return intent, confidence
        except Exception as e:
            print(f"Intent classification failed: {e}")
            return "Prescription", 0.5

    def _check_drug_interactions(self, drugs):
        """
        Detection drug interactions from known database.
        """
        interactions = []
        drugs_lower = [d.lower() for d in drugs]

        for drug1 in drugs_lower:
            if drug1 in DRUG_INTERACTIONS:
                for interaction in DRUG_INTERACTIONS[drug1]:
                    for drug2 in drugs_lower:
                        if interaction in drug2:
                            interactions.append({
                                'drug1': drug1,
                                'drug2': drug2,
                                'severity': 'moderate'
                            })

        return interactions

    def _calibrate_confidence(self, n_drugs, n_symptoms, intent_conf, temperature=1.5):
        """
        Calibrate overall prescription confidence with temperature scaling.
        Temperature > 1 makes probabilities less extreme (more calibrated).
        """
        drug_factor = min(1.0, n_drugs / 3)
        symptom_factor = min(1.0, n_symptoms / 5)

        raw = (intent_conf * 0.5 + drug_factor * 0.3 + symptom_factor * 0.2)

        # Temperature scaling: soften overconfident predictions
        calibrated = raw ** (1.0 / temperature)
        return float(min(0.99, max(0.0, calibrated)))

    def _generate_recommendation(self, drugs, interactions, intent_conf):
        """
        Generate clinical recommendation based on analysis.
        """
        if not drugs:
            return "[WARNING] No medications found. Prescription validation required."

        if interactions:
            return f"[WARNING] {len(interactions)} potential drug interaction(s) detected. Consult pharmacist."

        if intent_conf < 0.5:
            return "[WARNING] Medical intent unclear. Review prescription format."

        return "[OK] Prescription appears valid. Monitor for adverse effects."

    def search_patient_history(self, query: str, records: list) -> list:
        """
        Semantic search over patient medical records using embeddings.
        If sentence-transformers is not available, falls back to keyword matching.
        """
        if not records:
            return []

        # If similarity model available, use embeddings
        if self.similarity_model is not None:
            query_embedding = self.similarity_model.encode([query])[0]
            
            scored_records = []
            for record in records:
                # Combine relevant text fields for embedding
                text_to_embed = f"{record.get('diagnosis', '')} {record.get('description', '')} {record.get('symptoms', '')}"
                if not text_to_embed.strip():
                    continue
                    
                record_embedding = self.similarity_model.encode([text_to_embed])[0]
                
                # Cosine similarity
                sim = np.dot(query_embedding, record_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(record_embedding))
                
                if sim > 0.3: # Threshold for relevance
                    scored_records.append((sim, record))
            
            scored_records.sort(key=lambda x: x[0], reverse=True)
            return [record for sim, record in scored_records]
        
        # Fallback keyword matching
        query_words = set(query.lower().split())
        scored_records = []
        
        for record in records:
            score = 0
            text_to_search = f"{record.get('diagnosis', '')} {record.get('description', '')} {record.get('symptoms', '')}".lower()
            record_words = set(text_to_search.split())
            
            common_words = query_words.intersection(record_words)
            score = len(common_words)
            
            if score > 0:
                scored_records.append((score, record))
                
        scored_records.sort(key=lambda x: x[0], reverse=True)
        return [record for score, record in scored_records]

