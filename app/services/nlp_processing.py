import spacy
from typing import Dict, Any, List
import re

# Load English language model
nlp = spacy.load("en_core_web_sm")

async def extract_medical_data(text: str) -> Dict[str, Any]:
    """
    Extract medical information from transcribed text using spaCy.
    """
    doc = nlp(text)
    
    # Initialize data structure
    data = {
        "demographics": {
            "age": None,
            "gender": None
        },
        "symptoms": [],
        "diagnoses": [],
        "medications": [],
        "vital_signs": {
            "blood_pressure": None,
            "heart_rate": None,
            "temperature": None,
            "respiratory_rate": None,
            "oxygen_saturation": None
        },
        "lab_results": [],
        "procedures": [],
        "allergies": [],
        "risk_factors": []
    }
    
    # Extract age
    age_pattern = r'\b(\d+)[\s-]*(year|yr|years|y)[s]?\s+old\b'
    age_match = re.search(age_pattern, text, re.IGNORECASE)
    if age_match:
        data["demographics"]["age"] = int(age_match.group(1))
    
    # Extract gender
    gender_terms = {
        "male": ["male", "man", "gentleman", "boy"],
        "female": ["female", "woman", "lady", "girl"]
    }
    for gender, terms in gender_terms.items():
        if any(term in text.lower() for term in terms):
            data["demographics"]["gender"] = gender
            break
    
    # Extract vital signs
    bp_pattern = r'\b(\d{2,3})/(\d{2,3})\b'
    bp_match = re.search(bp_pattern, text)
    if bp_match:
        data["vital_signs"]["blood_pressure"] = f"{bp_match.group(1)}/{bp_match.group(2)}"
    
    hr_pattern = r'\b(\d{2,3})\s*(bpm|beats per minute)\b'
    hr_match = re.search(hr_pattern, text, re.IGNORECASE)
    if hr_match:
        data["vital_signs"]["heart_rate"] = int(hr_match.group(1))
    
    # Extract medications
    medication_patterns = [
        r'\b\d+\s*mg\s+\w+\b',
        r'\b\w+\s+\d+\s*mg\b',
        r'\btablet[s]?\s+of\s+\w+\b',
        r'\b\w+\s+tablet[s]?\b'
    ]
    
    for pattern in medication_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            if match.group() not in data["medications"]:
                data["medications"].append(match.group())
    
    # Extract diagnoses using NER
    for ent in doc.ents:
        if ent.label_ == "DISEASE":
            if ent.text not in data["diagnoses"]:
                data["diagnoses"].append(ent.text)
    
    # Extract symptoms
    symptom_keywords = [
        "pain", "ache", "discomfort", "fever", "cough", "headache",
        "nausea", "vomiting", "diarrhea", "fatigue", "weakness"
    ]
    
    for sentence in doc.sents:
        for keyword in symptom_keywords:
            if keyword in sentence.text.lower():
                symptom = sentence.text.strip()
                if symptom not in data["symptoms"]:
                    data["symptoms"].append(symptom)
    
    return data
