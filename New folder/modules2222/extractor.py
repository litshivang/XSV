import re
from typing import Dict, Any
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extractor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedNERExtractor:
    """
    Named Entity Recognition with ML support
    Extracts: travelers, budget, duration, destinations, preferences
    """
    
    def __init__(self):
        """Initialize NER extractor with patterns and ML models"""
        self.setup_patterns()
    
    def setup_patterns(self):
        """Setup comprehensive extraction patterns"""
        self.patterns = {
            # Enhanced traveler patterns
            'travelers': [
                r'(?:family\s+of\s+|group\s+of\s+|total\s+of\s+|total\s+)(\d+)(?:\s+(?:people|pax|log|travelers?|adults?|व्यक्ति|यात्री))?',
                r'(\d+)\s*(?:adults?)\s*(?:\+|and|\&|तथा)\s*(\d+)\s*(?:kids?|children?|child|बच्चे|बच्चा)',
                r'(\d+)\s*(?:people|persons?|travelers?|pax|adults?|log|यात्री|व्यक्ति|लोग)',
                r'we\s+are\s+a?\s*(?:group\s+of\s+)?(\d+)',
                r'for\s+(\d+)\s+(?:people|adults?|pax|व्यक्ति)',
                r'(\d+)\s+(?:log|व्यक्ति|यात्री|लोग)',
                r'हम\s+(\d+)\s+लोग|(\d+)\s+व्यक्ति\s+के\s+लिए'
            ],
            
            # Enhanced budget patterns with Indian context
            'budget': [
                r'budget.*?(?:Rs\.?|INR|₹|rupees?|रुपए|रुपये)\s*([\d,]+)(?:\.\d{2})?(?:\s*(?:per\s+person|pp|each|प्रति\s+व्यक्ति))?',
                r'(?:Rs\.?|INR|₹|rupees?|रुपए)\s*([\d,]+)(?:\.\d{2})?\s*(?:per\s+person|pp|each|प्रति\s+व्यक्ति)',
                r'around\s+(?:Rs\.?|INR|₹|rupees?)\s*([\d,]+)',
                r'approx\.?\s+(?:Rs\.?|INR|₹|rupees?)\s*([\d,]+)',
                r'maximum\s+(?:Rs\.?|INR|₹|rupees?)\s*([\d,]+)',
                r'within\s+(?:Rs\.?|INR|₹|rupees?)\s*([\d,]+)',
                r'(\d+)\s*(?:lakh|lakhs?|लाख)\s*(?:rupees?|Rs\.?|रुपए)?',
                r'(\d+)\s*(?:thousand|k|हजार)\s*(?:rupees?|Rs\.?|रुपए)?',
                r'(\d+)\s*(?:crore|करोड़)\s*(?:rupees?|Rs\.?|रुपए)?'
            ],
            
            # Enhanced duration patterns
            'duration': [
                r'(\d+)\s*nights?\s*/?(?:\s*(\d+)\s*days?)?',
                r'(\d+)\s*days?\s*/?(?:\s*(\d+)\s*nights?)?',
                r'(\d+)N\s*/?\s*(\d+)D',
                r'(\d+)D\s*/?\s*(\d+)N',
                r'stay\s+(?:for\s+)?(\d+)\s*(?:nights?|days?)',
                r'(\d+)\s*(?:रात|रातें|दिन)',
                r'(\d+)\s*night\s*(\d+)\s*day',
                r'(\d+)\s*दिन\s*(\d+)\s*रात'
            ],
            
            # Comprehensive Indian and International destinations
            'destinations': [
                # Popular Indian destinations
                'kashmir', 'srinagar', 'gulmarg', 'pahalgam', 'sonmarg', 'jammu',
                'kerala', 'kochi', 'munnar', 'alleppey', 'kumarakom', 'thekkady',
                'goa', 'panaji', 'calangute', 'baga', 'anjuna', 'arambol',
                'rajasthan', 'jaipur', 'udaipur', 'jodhpur', 'jaisalmer', 'pushkar',
                'himachal', 'manali', 'shimla', 'dharamshala', 'kasol', 'kufri',
                'uttarakhand', 'nainital', 'mussoorie', 'rishikesh', 'haridwar',
                'delhi', 'mumbai', 'bangalore', 'hyderabad', 'chennai', 'kolkata',
                'pune', 'ahmedabad', 'surat', 'agra', 'varanasi', 'amritsar',
                'darjeeling', 'ooty', 'kodaikanal', 'coorg', 'hampi', 'mysore',
                'pondicherry', 'andaman', 'nicobar', 'lakshadweep', 'ladakh', 'spiti',
                
                # International destinations
                'maldives', 'thailand', 'bangkok', 'phuket', 'pattaya', 'krabi',
                'bali', 'indonesia', 'ubud', 'kintamani', 'seminyak', 'nusa dua',
                'singapore', 'malaysia', 'kuala lumpur', 'penang', 'langkawi',
                'sri lanka', 'colombo', 'kandy', 'galle', 'sigiriya',
                'bhutan', 'thimphu', 'paro', 'punakha',
                'nepal', 'kathmandu', 'pokhara', 'chitwan',
                'dubai', 'abu dhabi', 'sharjah',
                'europe', 'switzerland', 'france', 'italy', 'germany', 'austria',
                'paris', 'rome', 'zurich', 'interlaken', 'venice', 'amsterdam',
                'uk', 'london', 'scotland', 'ireland',
                'usa', 'new york', 'los angeles', 'las vegas', 'san francisco',
                'canada', 'toronto', 'vancouver', 'montreal',
                'australia', 'sydney', 'melbourne', 'perth',
                'japan', 'tokyo', 'kyoto', 'osaka', 'hiroshima',
                'south korea', 'seoul', 'busan', 'jeju',
                'vietnam', 'ho chi minh', 'hanoi', 'ha long bay',
                'cambodia', 'siem reap', 'phnom penh',
                'philippines', 'manila', 'cebu', 'boracay',
                'turkey', 'istanbul', 'cappadocia', 'antalya',
                'egypt', 'cairo', 'luxor', 'aswan'
            ],
            
            # Hotel preferences and accommodation
            'hotel_preferences': [
                r'(?:3|4|5)\s*star\s*hotel',
                r'(?:luxury|budget|mid-range|premium|deluxe)\s*(?:hotel|resort)',
                r'(?:beach|water|overwater|ocean)\s*villa',
                r'resort|homestay|guest\s*house|lodge|cottage',
                r'ac|non-ac|air\s*conditioned',
                r'breakfast\s*(?:included|only|complimentary)',
                r'all\s*meals|half\s*board|full\s*board|meal\s*plan',
                r'room\s*service|wifi|pool|spa|gym|parking'
            ],
            
            # Activities and experiences
            'activities': [
                'sightseeing', 'city tour', 'cultural tour', 'heritage walk',
                'snorkeling', 'diving', 'scuba diving', 'water sports',
                'safari', 'wildlife safari', 'tiger safari', 'elephant safari',
                'trekking', 'hiking', 'mountain climbing', 'adventure sports',
                'paragliding', 'river rafting', 'bungee jumping', 'zip lining',
                'boating', 'boat ride', 'cruise', 'sunset cruise',
                'cable car', 'ropeway', 'gondola', 'chairlift',
                'spa', 'massage', 'ayurveda', 'wellness',
                'shopping', 'local market', 'street food',
                'temple visit', 'monastery', 'palace tour',
                'beach time', 'beach activities', 'swimming',
                'romantic dinner', 'candlelight dinner', 'rooftop dining'
            ],
            
            # Special requirements
            'special_requirements': [
                'vegetarian', 'veg meals', 'jain food', 'halal food', 'kosher',
                'wheelchair', 'accessibility', 'disabled friendly',
                'honeymoon', 'anniversary', 'birthday', 'celebration',
                'children friendly', 'baby cot', 'high chair',
                'elderly friendly', 'senior citizen',
                'visa support', 'visa assistance', 'passport help',
                'travel insurance', 'medical insurance',
                'late checkout', 'early checkin', 'flexible timing',
                'airport pickup', 'airport drop', 'transfer',
                'private transport', 'private car', 'chauffeur',
                'guide', 'local guide', 'english speaking guide'
            ]
        }    
    
    def extract_with_confidence(self, text: str, field_type: str) -> Dict[str, Any]:
        """
        Extract information with confidence scoring
        
        Args:
            text (str): Input text to extract from
            field_type (str): Type of field to extract
            
        Returns:
            Dict with extracted value, confidence, method, and alternatives
        """
        result = {
            'value': None,
            'confidence': 0.0,
            'method': 'rule_based',
            'alternatives': [],
            'extraction_details': {}
        }
        
        try:
            # Route to specific extraction methods
            if field_type == 'travelers':
                result.update(self._extract_travelers(text))
            elif field_type == 'budget':
                result.update(self._extract_budget(text))
            elif field_type == 'duration':
                result.update(self._extract_duration(text))
            elif field_type == 'destinations':
                result.update(self._extract_destinations(text))
            elif field_type == 'hotel_preferences':
                result.update(self._extract_hotel_preferences(text))
            elif field_type == 'activities':
                result.update(self._extract_activities(text))
            elif field_type == 'special_requirements':
                result.update(self._extract_special_requirements(text))
            elif field_type == 'phone':
                result.update(self._extract_phone(text))
            elif field_type == 'email':
                result.update(self._extract_email(text))
            
            logger.debug(f"Extracted {field_type}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Extraction error for {field_type}: {e}")
            return result
    
    def _extract_travelers(self, text: str) -> Dict[str, Any]:
        """Enhanced traveler extraction with adult+child logic"""
        results = []
        confidence_scores = []
        extraction_details = []
        
        for pattern in self.patterns['travelers']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                matched_text = match.group(0)
                
                if len(groups) >= 2 and groups[1]:  # Adults + Children format
                    adults = int(groups[0])
                    children = int(groups[1])
                    total = adults + children
                    results.append(total)
                    confidence_scores.append(0.95)  # High confidence for explicit breakdown
                    extraction_details.append(f"Adults: {adults}, Children: {children}")
                elif groups[0]:  # Single number
                    total = int(groups[0])
                    results.append(total)
                    
                    # Confidence based on context
                    if any(word in matched_text.lower() for word in ['people', 'pax', 'travelers', 'adults']):
                        confidence_scores.append(0.9)
                    else:
                        confidence_scores.append(0.75)
                    
                    extraction_details.append(f"Total travelers: {total}")
        
        
        if results:
            # Return highest confidence result
            best_idx = confidence_scores.index(max(confidence_scores))
            return {
                'value': results[best_idx],
                'confidence': confidence_scores[best_idx],
                'method': 'rule_based',
                'alternatives': list(set(results)),
                'extraction_details': extraction_details[best_idx]
            }
        
        return {
            'value': None,
            'confidence': 0.0,
            'method': 'rule_based',
            'alternatives': [],
            'extraction_details': 'No traveler count found'
        }
    
    def _extract_budget(self, text: str) -> Dict[str, Any]:
        """Enhanced budget extraction with Indian currency handling"""
        results = []
        confidence_scores = []
        extraction_details = []
        
        for pattern in self.patterns['budget']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount_str = match.group(1).replace(',', '')
                    matched_text = match.group(0).lower()
                    
                    # Handle special multipliers
                    if any(word in matched_text for word in ['lakh', 'lakhs', 'लाख']):
                        amount = int(amount_str) * 100000
                        unit = 'lakh'
                    elif any(word in matched_text for word in ['crore', 'करोड़']):
                        amount = int(amount_str) * 10000000
                        unit = 'crore'
                    elif any(word in matched_text for word in ['thousand', 'k', 'हजार']):
                        amount = int(amount_str) * 1000
                        unit = 'thousand'
                    else:
                        amount = int(amount_str)
                        unit = 'rupees'
                    
                    formatted_amount = f"₹{amount:,}"
                    results.append(formatted_amount)
                    
                    # Confidence based on context
                    if any(phrase in matched_text for phrase in ['per person', 'pp', 'each', 'प्रति व्यक्ति']):
                        confidence_scores.append(0.95)
                        extraction_details.append(f"Per person budget: {formatted_amount}")
                    elif 'budget' in matched_text:
                        confidence_scores.append(0.9)
                        extraction_details.append(f"Total budget: {formatted_amount}")
                    else:
                        confidence_scores.append(0.8)
                        extraction_details.append(f"Amount found: {formatted_amount}")
                        
                except (ValueError, IndexError) as e:
                    logger.debug(f"Budget parsing error: {e}")
                    continue
        
        if results:
            best_idx = confidence_scores.index(max(confidence_scores))
            return {
                'value': results[best_idx],
                'confidence': confidence_scores[best_idx],
                'method': 'rule_based',
                'alternatives': list(set(results)),
                'extraction_details': extraction_details[best_idx]
            }
        
        return {
            'value': None,
            'confidence': 0.0,
            'method': 'rule_based',
            'alternatives': [],
            'extraction_details': 'No budget information found'
        }
    
    def _extract_duration(self, text: str) -> Dict[str, Any]:
        """Enhanced duration extraction with night/day logic"""
        results = []
        confidence_scores = []
        extraction_details = []
        
        for pattern in self.patterns['duration']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    groups = match.groups()
                    matched_text = match.group(0).lower()
                    
                    # Parse different duration formats
                    if 'night' in matched_text:
                        nights = int(groups[0])
                        days = int(groups[1]) if groups[1] else nights + 1
                        duration = f"{nights} nights / {days} days"
                        confidence_scores.append(0.95)
                    elif 'day' in matched_text:
                        days = int(groups[0])
                        nights = max(1, days - 1) if days > 1 else 0
                        duration = f"{nights} nights / {days} days"
                        confidence_scores.append(0.9)
                    elif re.search(r'(\d+)N.*?(\d+)D', matched_text):
                        nights = int(groups[0])
                        days = int(groups[1])
                        duration = f"{nights} nights / {days} days"
                        confidence_scores.append(0.95)
                    elif re.search(r'(\d+)D.*?(\d+)N', matched_text):
                        days = int(groups[0])
                        nights = int(groups[1])
                        duration = f"{nights} nights / {days} days"
                        confidence_scores.append(0.95)
                    else:
                        # Generic number found
                        num = int(groups[0])
                        duration = f"{num-1} nights / {num} days"
                        confidence_scores.append(0.7)
                    
                    results.append(duration)
                    extraction_details.append(f"Duration: {duration}")
                    
                except (ValueError, IndexError) as e:
                    logger.debug(f"Duration parsing error: {e}")
                    continue
        
        if results:
            best_idx = confidence_scores.index(max(confidence_scores))
            return {
                'value': results[best_idx],
                'confidence': confidence_scores[best_idx],
                'method': 'rule_based',
                'alternatives': list(set(results)),
                'extraction_details': extraction_details[best_idx]
            }
        
        return {
            'value': None,
            'confidence': 0.0,
            'method': 'rule_based',
            'alternatives': [],
            'extraction_details': 'No duration found'
        }
    
    def _extract_destinations(self, text: str) -> Dict[str, Any]:
        """Enhanced destination extraction with location grouping"""
        text_lower = text.lower()
        found_destinations = []
        confidence_scores = []
        extraction_details = []
        
        for dest in self.patterns['destinations']:
            dest_lower = dest.lower()
            if dest_lower in text_lower:
                # Word‑boundary match
                if f" {dest_lower} " in text_lower:
                    confidence = 0.95
                # Start or end of text
                elif text_lower.startswith(dest_lower) or text_lower.endswith(dest_lower):
                    confidence = 0.9
                # Punctuation boundary
                elif f"{dest_lower}," in text_lower or f"{dest_lower}." in text_lower:
                    confidence = 0.85
                else:
                    confidence = 0.7
                
                found_destinations.append(dest.title())
                confidence_scores.append(confidence)
                extraction_details.append(f"Found: {dest.title()}")
        
        # Dedupe while preserving first‑seen order and confidences
        unique, uniq_conf = [], []
        seen = set()
        for d, c in zip(found_destinations, confidence_scores):
            if d.lower() not in seen:
                unique.append(d)
                uniq_conf.append(c)
                seen.add(d.lower())
        
        if unique:
            avg_conf = sum(uniq_conf) / len(uniq_conf)
            return {
                'value': unique,
                'confidence': avg_conf,
                'method': 'rule_based',
                'alternatives': [],
                'extraction_details': '; '.join(extraction_details)
            }
        
        return {
            'value': [],
            'confidence': 0.0,
            'method': 'rule_based',
            'alternatives': [],
            'extraction_details': 'No destinations found'
        }

    def _extract_hotel_preferences(self, text: str) -> Dict[str, Any]:
            """Extract hotel preferences and requirements"""
            text_lower = text.lower()
            found_preferences = []
            confidence_scores = []
            
            for pattern in self.patterns['hotel_preferences']:
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    preference = match.group(0).strip()
                    found_preferences.append(preference)
                    confidence_scores.append(0.85)
            
            if found_preferences:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                return {
                    'value': found_preferences,
                    'confidence': avg_confidence,
                    'method': 'rule_based',
                    'alternatives': [],
                    'extraction_details': f"Found {len(found_preferences)} preferences"
                }
            
            return {
                'value': [],
                'confidence': 0.0,
                'method': 'rule_based',
                'alternatives': [],
                'extraction_details': 'No hotel preferences found'
            }
        
    def _extract_activities(self, text: str) -> Dict[str, Any]:
        """Extract activities and experiences"""
        text_lower = text.lower()
        found_activities = []
        confidence_scores = []
        
        for activity in self.patterns['activities']:
            if activity.lower() in text_lower:
                found_activities.append(activity.title())
                confidence_scores.append(0.8)
        
        if found_activities:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            return {
                'value': found_activities,
                'confidence': avg_confidence,
                'method': 'rule_based',
                'alternatives': [],
                'extraction_details': f"Found {len(found_activities)} activities"
            }
        
        return {
            'value': [],
            'confidence': 0.0,
            'method': 'rule_based',
            'alternatives': [],
            'extraction_details': 'No activities found'
        }
    
    def _extract_special_requirements(self, text: str) -> Dict[str, Any]:
        """Extract special requirements"""
        text_lower = text.lower()
        found_requirements = []
        confidence_scores = []
        
        for requirement in self.patterns['special_requirements']:
            if requirement.lower() in text_lower:
                found_requirements.append(requirement.title())
                confidence_scores.append(0.8)
        
        if found_requirements:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            return {
                'value': found_requirements,
                'confidence': avg_confidence,
                'method': 'rule_based',
                'alternatives': [],
                'extraction_details': f"Found {len(found_requirements)} requirements"
            }
        
        return {
            'value': [],
            'confidence': 0.0,
            'method': 'rule_based',
            'alternatives': [],
            'extraction_details': 'No special requirements found'
        }
    
    def _extract_phone(self, text: str) -> Dict[str, Any]:
        """Extract phone numbers"""
        phone_patterns = [
            r'\+91[\s-]?\d{10}',
            r'\d{10}',
            r'\+\d{1,3}[\s-]?\d{10,12}',
            r'\(\d{3}\)[\s-]?\d{3}[\s-]?\d{4}'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return {
                    'value': match.group(0),
                    'confidence': 0.9,
                    'method': 'rule_based',
                    'alternatives': [],
                    'extraction_details': 'Phone number extracted'
                }
        
        return {
            'value': None,
            'confidence': 0.0,
            'method': 'rule_based',
            'alternatives': [],
            'extraction_details': 'No phone number found'
        }
    
    def _extract_email(self, text: str) -> Dict[str, Any]:
        """Extract email addresses"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        
        if match:
            return {
                'value': match.group(0),
                'confidence': 0.95,
                'method': 'rule_based',
                'alternatives': [],
                'extraction_details': 'Email address extracted'
            }
        
        return {
            'value': None,
            'confidence': 0.0,
            'method': 'rule_based',
            'alternatives': [],
            'extraction_details': 'No email found'
        }
