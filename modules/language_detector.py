import re
from typing import Dict, Any
from collections import defaultdict
import logging


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('language_detector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HybridLanguageDetector:
    """
    Enhanced language detection with ML support
    Handles: Hindi (Devanagari), Hindi (Romanized), English, Hinglish
    """
    
    def __init__(self):
        """Initialize language detector with patterns and ML models"""
        self.setup_patterns()
    
    def setup_patterns(self):
        """Setup comprehensive language detection patterns"""
        self.patterns = {
            # Hindi in Devanagari script
            'hindi_devanagari': [
                r'[\u0900-\u097F]+',  # Devanagari Unicode range
                r'यात्रा|पर्यटन|ग्राहक|बजट|दिन|रात|होटल|गंतव्य|स्थान'
            ],
            
            # Romanized Hindi words
            'hindi_romanized': [
                r'\b(?:yatra|paryatan|client|chahiye|bhej|do|namaste|dhanyawad)\b',
                r'\b(?:din|raat|log|paisa|rupee|ghar|aana|jaana|karna)\b',
                r'\b(?:hona|dena|lena|dekha|sunna|milna|banana)\b',
                r'\b(?:safar|mukam|jagah|hotel|kamra|khana|paani)\b'
            ],
            
            # Strong Hinglish indicators
            'hinglish_strong': [
                r'\b(?:hamare|tumhare|unka|iska|uska|mera|tera|apna)\b',
                r'\b(?:kar|denge|hogi|hona|chahiye|milega|ayega|jayega)\b',
                r'\b(?:jaldi|finalize|karna|include|honi|chahiye|please)\b',
                r'\b(?:bhi|toh|aur|main|ko|ke|liye|se|me|par|mai)\b',
                r'\b(?:accha|theek|sahi|galat|problem|tension|fix)\b'
            ],
            
            # Regional travel terms
            'regional_terms': [
                r'\b(?:ghumna|ghoomna|dekhna|jana|aana|rehna|rukna)\b',
                r'\b(?:hotel|room|booking|package|tour|guide|taxi)\b',
                r'\b(?:flight|train|bus|transport|pickup|drop)\b',
                r'\b(?:mandir|masjid|gurudwara|dargah|beach|pahad)\b'
            ],
            
            # Common English travel terms for baseline
            'english_travel': [
                r'\b(?:travel|trip|vacation|holiday|tour|booking)\b',
                r'\b(?:hotel|resort|accommodation|stay|night|day)\b',
                r'\b(?:flight|airport|transport|car|taxi|bus)\b'
            ]
        }
    
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Hybrid language detection with confidence scores
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Dict containing language info with confidence scores
        """
        result = {
            'primary_language': 'english',
            'secondary_language': None,
            'confidence': 0.0,
            'mixed_language': False,
            'detection_method': 'rule_based',
            'language_scores': {}
        }
        
        try:
            text_lower = text.lower()
            scores = defaultdict(float)
            
            # Rule-based scoring system
            # Devanagari script gets highest priority
            devanagari_matches = sum(1 for pattern in self.patterns['hindi_devanagari'] 
                                   if re.search(pattern, text))
            if devanagari_matches > 0:
                scores['hindi'] += 15.0 * devanagari_matches
            
            # Romanized Hindi detection
            hindi_romanized_matches = sum(1 for pattern in self.patterns['hindi_romanized'] 
                                        if re.search(pattern, text_lower))
            scores['hindi_romanized'] += hindi_romanized_matches * 3.0
            
            # Hinglish pattern detection
            hinglish_matches = sum(1 for pattern in self.patterns['hinglish_strong'] 
                                 if re.search(pattern, text_lower))
            scores['hinglish'] += hinglish_matches * 2.0
            
            # Regional terms
            regional_matches = sum(1 for pattern in self.patterns['regional_terms'] 
                                 if re.search(pattern, text_lower))
            scores['hinglish'] += regional_matches * 1.5
            
            # English baseline
            english_matches = sum(1 for pattern in self.patterns['english_travel'] 
                                if re.search(pattern, text_lower))
            scores['english'] += english_matches * 1.0
                     
            # Store all scores for analysis
            result['language_scores'] = dict(scores)
            
            # Determine primary language based on scores
            if scores['hindi'] >= 8.0:
                result['primary_language'] = 'hindi'
                result['confidence'] = min(scores['hindi'] / 15.0, 1.0)
            elif scores['hinglish'] >= 5.0:
                result['primary_language'] = 'hinglish'
                result['confidence'] = min(scores['hinglish'] / 8.0, 1.0)
                result['mixed_language'] = True
            elif scores['hindi_romanized'] >= 3.0:
                result['primary_language'] = 'hindi_english'
                result['confidence'] = min(scores['hindi_romanized'] / 6.0, 1.0)
                result['mixed_language'] = True
            else:
                result['primary_language'] = 'english'
                result['confidence'] = 0.8
            
            logger.debug(f"Language detection result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return result
