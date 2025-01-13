from typing import Dict, Any, List
import re
import spacy
from pathlib import Path
import json

class MedicalNLPService:
    def __init__(self):
        # Load SpaCy model for general text processing
        self.nlp = spacy.load("en_core_web_sm")
        
        # Load medical terminology
        self.medical_terms = self._load_medical_terms()
    
    def _load_medical_terms(self) -> Dict[str, List[str]]:
        """Load medical terminology from JSON file"""
        terms_path = Path(__file__).parent / "medical_terms.json"
        if terms_path.exists():
            with open(terms_path) as f:
                return json.load(f)
        return {
            "risk_factors": [
                "diabetes", "hypertension", "smoking", "obesity",
                "hyperlipidemia", "cardiovascular disease"
            ],
            "conditions": [
                "asthma", "copd", "cancer", "arthritis",
                "depression", "anxiety"
            ],
            "medical_entities": [
                "pain", "fever", "cough", "fatigue",
                "headache", "nausea", "vomiting", "diarrhea",
                "shortness of breath", "chest pain"
            ]
        }
    
    def extract_demographics(self, text: str) -> Dict[str, Any]:
        """Extract demographic information from text"""
        # Age extraction
        age_pattern = r'\b(\d{1,3})\s*(?:years?|yrs?|y/o)\s*(?:old)?\b'
        age_match = re.search(age_pattern, text.lower())
        age = int(age_match.group(1)) if age_match else None
        
        # Gender extraction
        gender_terms = {
            "male": ["male", "man", "gentleman", "boy"],
            "female": ["female", "woman", "lady", "girl"]
        }
        
        gender = None
        text_lower = text.lower()
        for g, terms in gender_terms.items():
            if any(term in text_lower for term in terms):
                gender = g
                break
        
        return {"age": age, "gender": gender}
    
    def extract_risk_factors(self, text: str) -> List[str]:
        """Extract risk factors from text"""
        risk_factors = []
        text_lower = text.lower()
        
        # Check for known risk factors
        for factor in self.medical_terms["risk_factors"]:
            if factor in text_lower:
                risk_factors.append(factor)
        
        # Use SpaCy's NER to find additional entities
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["DISEASE", "CONDITION"]:
                risk_factors.append(ent.text.lower())
        
        return list(set(risk_factors))
    
    def extract_medical_history(self, text: str) -> Dict[str, List[str]]:
        """Extract medical history information"""
        doc = self.nlp(text)
        
        family_history = []
        surgical_history = []
        medical_entities = []
        
        # Process each sentence
        for sent in doc.sents:
            sent_text = sent.text.lower()
            
            # Family history
            if any(term in sent_text for term in ["family", "father", "mother", "sister", "brother"]):
                family_history.append(sent.text.strip())
            
            # Surgical history
            if any(term in sent_text for term in ["surgery", "operation", "procedure", "surgical"]):
                surgical_history.append(sent.text.strip())
            
            # Check for medical entities
            for entity in self.medical_terms["medical_entities"]:
                if entity in sent_text:
                    medical_entities.append(entity)
        
        return {
            "family_history": family_history,
            "surgical_history": surgical_history,
            "medical_entities": list(set(medical_entities))
        }
    
    async def process_medical_text(self, text: str) -> Dict[str, Any]:
        """Process medical text and extract all relevant information"""
        # Extract demographics
        demographics = self.extract_demographics(text)
        
        # Extract risk factors
        risk_factors = self.extract_risk_factors(text)
        
        # Extract medical history
        history = self.extract_medical_history(text)
        
        return {
            "demographics": demographics,
            "risk_factors": risk_factors,
            "family_history": history["family_history"],
            "surgical_history": history["surgical_history"],
            "medical_entities": history["medical_entities"]
        }

medical_nlp_service = MedicalNLPService()
