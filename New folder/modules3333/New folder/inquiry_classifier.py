import re
from typing import Dict, Any
import logging
from modules.extractor import EnhancedNERExtractor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('inquiry_classifier.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InquiryClassifier:
    """
    Classify inquiry type: SINGLE_LEG, MULTI_LEG, or MODIFICATION
    """
    
    def __init__(self):
        """Initialize inquiry classifier with patterns"""
        self.modification_patterns = [
            r'(?:re:|reply:|modification|change|update|modify)',
            r'(?:skip|remove|delete|cancel)',
            r'(?:upgrade|downgrade|different|alternative)',
            r'(?:resend|update.*quote|new.*quote)',
            r'(?:client.*change|made.*change|some.*change)'
        ]
        
        self.multi_leg_indicators = [
            r'(?:first|then|after|next|following)',
            r'(?:location|destination|place).*(?:location|destination|place)',
            r'(?:for\s+\w+.*for\s+\w+)',
            r'(?:in\s+\w+.*in\s+\w+)',
            r'(?:stay.*night.*stay.*night)',
            r'(?:\d+\s*night.*\d+\s*night)'
        ]
    
    def classify_inquiry(self, text: str, subject: str = "") -> Dict[str, Any]:
        """
        Classify the inquiry type with confidence
        
        Args:
            text (str): Email body text
            subject (str): Email subject line
            
        Returns:
            Dict with classification result and confidence
        """
        combined_text = f"{subject} {text}".lower()
        
        # Check for modification indicators
        modification_score = sum(1 for pattern in self.modification_patterns 
                                if re.search(pattern, combined_text, re.IGNORECASE))
        
        # Check for multi-leg indicators
        multi_leg_score = sum(1 for pattern in self.multi_leg_indicators 
                             if re.search(pattern, combined_text, re.IGNORECASE))
        
        # Count destinations mentioned
        ner_extractor = EnhancedNERExtractor()
        destinations = ner_extractor.extract_with_confidence(text, 'destinations')
        dest_count = len(destinations.get('value', []))
        
        # Classification logic
        if modification_score >= 2:
            return {
                'type': 'MODIFICATION',
                'confidence': min(0.9, 0.5 + modification_score * 0.1),
                'details': f"Modification indicators: {modification_score}"
            }
        elif multi_leg_score >= 2 or dest_count >= 2:
            return {
                'type': 'MULTI_LEG',
                'confidence': min(0.9, 0.6 + max(multi_leg_score, dest_count) * 0.1),
                'details': f"Multi-leg indicators: {multi_leg_score}, Destinations: {dest_count}"
            }
        else:
            return {
                'type': 'SINGLE_LEG',
                'confidence': 0.8,
                'details': "Simple single destination inquiry"
            }
