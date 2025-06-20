#!/usr/bin/env python3
"""
Enhanced AI Travel Agent - Production Ready System
Hybrid ML + Rule-Based Approach for Travel Inquiry Processing
Author: Enhanced Travel Processing System
Version: 2.0
"""

import os
import json
import csv
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from collections import defaultdict
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('travel_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ML Libraries for enhanced processing (Optional - Free/Open Source)
try:
    import spacy
    import langdetect
    from transformers import pipeline, AutoTokenizer, AutoModel
    ML_AVAILABLE = True
    logger.info("ML libraries loaded successfully")
except ImportError:
    ML_AVAILABLE = False
    logger.warning("ML libraries not available. Using rule-based approach only.")

# Import utility modules
try:
    from utils.email_fetcher import fetch_live_emails
    from utils.email_sender import GmailEmailSender
    from utils.excel_utils import ExcelGenerator
except ImportError as e:
    logger.warning(f"Some utility modules not found: {e}")


class HybridLanguageDetector:
    """
    Enhanced language detection with ML support
    Handles: Hindi (Devanagari), Hindi (Romanized), English, Hinglish
    """
    
    def __init__(self):
        """Initialize language detector with patterns and ML models"""
        self.setup_patterns()
        if ML_AVAILABLE:
            self._setup_ml_detector()
    
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
    
    def _setup_ml_detector(self):
        """Setup ML-based language detection (if available)"""
        try:
            # Initialize langdetect for broader language coverage
            self.use_ml = True
            logger.info("ML language detection initialized")
        except Exception as e:
            self.use_ml = False
            logger.warning(f"ML setup failed: {e}")
    
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
            
            # ML enhancement (if available)
            if ML_AVAILABLE and self.use_ml and len(text.strip()) > 10:
                try:
                    ml_lang = langdetect.detect(text)
                    confidence = langdetect.detect_langs(text)[0].prob
                    
                    if ml_lang in ['hi', 'ur']:  # Hindi/Urdu
                        scores['hindi'] += 8.0 * confidence
                    elif ml_lang == 'en':
                        scores['english'] += 5.0 * confidence
                    
                    result['detection_method'] = 'hybrid'
                    logger.debug(f"ML detected: {ml_lang} with confidence: {confidence}")
                except Exception as e:
                    logger.debug(f"ML detection failed: {e}")
            
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


class EnhancedNERExtractor:
    """
    Named Entity Recognition with ML support
    Extracts: travelers, budget, duration, destinations, preferences
    """
    
    def __init__(self):
        """Initialize NER extractor with patterns and ML models"""
        self.setup_patterns()
        if ML_AVAILABLE:
            self._setup_ml_models()
    
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
    
    def _setup_ml_models(self):
        """Setup ML models for enhanced extraction (if available)"""
        try:
            if ML_AVAILABLE:
                # Load multilingual NER pipeline
                self.ner_pipeline = pipeline(
                    "ner", 
                    model="xlm-roberta-base",
                    aggregation_strategy="simple"
                )
                self.ml_ready = True
                logger.info("ML NER models loaded successfully")
        except Exception as e:
            self.ml_ready = False
            logger.warning(f"ML NER setup failed: {e}")
    
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
        
        # ML enhancement for number detection (if available)
        if ML_AVAILABLE and self.ml_ready:
            try:
                entities = self.ner_pipeline(text)
                for entity in entities:
                    if 'MISC' in entity.get('entity_group', '') and re.search(r'\d+', entity['word']):
                        num_match = re.search(r'\d+', entity['word'])
                        if num_match:
                            num = int(num_match.group())
                            if 1 <= num <= 50:  # Reasonable traveler range
                                results.append(num)
                                confidence_scores.append(0.6)
                                extraction_details.append(f"ML detected: {num}")
            except Exception as e:
                logger.debug(f"ML traveler extraction failed: {e}")
        
        if results:
            # Return highest confidence result
            best_idx = confidence_scores.index(max(confidence_scores))
            return {
                'value': results[best_idx],
                'confidence': confidence_scores[best_idx],
                'method': 'hybrid' if ML_AVAILABLE else 'rule_based',
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


class TravelAgentProcessor:
    """
    Main processor for travel inquiries with hybrid ML + rule-based approach
    """
    
    def __init__(self):
        """Initialize the travel agent processor"""
        self.language_detector = HybridLanguageDetector()
        self.ner_extractor = EnhancedNERExtractor()
        self.inquiry_classifier = InquiryClassifier()
        logger.info("Travel Agent Processor initialized")
    
    def process_inquiry(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a travel inquiry email
        
        Args:
            email_data (Dict): Email data with subject, body, sender, etc.
            
        Returns:
            Dict with processed inquiry data
        """
        try:
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            sender = email_data.get('sender', '')
            
            logger.info(f"Processing inquiry from: {sender}")
            
            # Step 1: Language Detection
            language_info = self.language_detector.detect_language(body)
            
            # Step 2: Inquiry Classification
            inquiry_type = self.inquiry_classifier.classify_inquiry(body, subject)
            
            # Step 3: Extract basic information
            basic_info = self._extract_basic_info(body, sender)
            
            # Step 4: Extract location-specific details based on inquiry type
            if inquiry_type['type'] == 'MULTI_LEG':
                location_details = self._extract_multi_leg_details(body)
            else:
                location_details = self._extract_single_leg_details(body)
            
            # Compile results
            result = {
                'inquiry_id': f"INQ_{int(time.time())}",
                'timestamp': datetime.now().isoformat(),
                'language_info': language_info,
                'inquiry_type': inquiry_type,
                'basic_info': basic_info,
                'location_details': location_details,
                'raw_data': {
                    'subject': subject,
                    'body': body,
                    'sender': sender
                }
            }
            
            logger.info(f"Successfully processed inquiry: {result['inquiry_id']}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing inquiry: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'raw_data': email_data
            }
    
    def _extract_basic_info(self, text: str, sender: str) -> Dict[str, Any]:
        """Extract basic information common to all inquiry types"""
        basic_info = {}
        
        # Extract key fields
        fields = ['travelers', 'budget', 'duration', 'destinations', 
                 'hotel_preferences', 'activities', 'special_requirements', 'phone', 'email']
        
        for field in fields:
            extraction_result = self.ner_extractor.extract_with_confidence(text, field)
            basic_info[field] = extraction_result
        
        # Add sender information
        basic_info['sender'] = sender
        basic_info['contact_email'] = self.ner_extractor.extract_with_confidence(text, 'email')
        if not basic_info['contact_email']['value']:
            basic_info['contact_email']['value'] = sender
            basic_info['contact_email']['confidence'] = 0.9
        
        return basic_info
    
    def _extract_single_leg_details(self, text: str) -> Dict[str, Any]:
        """Extract details for single destination inquiries"""
        destinations = self.ner_extractor.extract_with_confidence(text, 'destinations')
        
        if destinations['value']:
            primary_destination = destinations['value'][0]
            return {
                'type': 'SINGLE_LEG',
                'primary_destination': primary_destination,
                'all_destinations': destinations['value'],
                'location_specific': {
                    primary_destination: {
                        'travelers': self.ner_extractor.extract_with_confidence(text, 'travelers'),
                        'duration': self.ner_extractor.extract_with_confidence(text, 'duration'),
                        'hotel_preferences': self.ner_extractor.extract_with_confidence(text, 'hotel_preferences'),
                        'activities': self.ner_extractor.extract_with_confidence(text, 'activities'),
                        'special_requirements': self.ner_extractor.extract_with_confidence(text, 'special_requirements')
                    }
                }
            }
        
        return {
            'type': 'SINGLE_LEG',
            'primary_destination': 'Not specified',
            'all_destinations': [],
            'location_specific': {}
        }
    
    def _extract_multi_leg_details(self, text: str) -> Dict[str, Any]:
        """Extract details for multi-destination inquiries"""
        # Split text by location patterns
        location_splits = self._split_text_by_locations(text)
        
        all_destinations = []
        location_specific = {}
        
        for location_text in location_splits:
            # Extract destination for this segment
            dest_result = self.ner_extractor.extract_with_confidence(location_text, 'destinations')
            
            if dest_result['value']:
                destination = dest_result['value'][0]
                all_destinations.extend(dest_result['value'])
                
                # Extract location-specific details
                location_specific[destination] = {
                    'travelers': self.ner_extractor.extract_with_confidence(location_text, 'travelers'),
                    'duration': self.ner_extractor.extract_with_confidence(location_text, 'duration'),
                    'hotel_preferences': self.ner_extractor.extract_with_confidence(location_text, 'hotel_preferences'),
                    'activities': self.ner_extractor.extract_with_confidence(location_text, 'activities'),
                    'special_requirements': self.ner_extractor.extract_with_confidence(location_text, 'special_requirements'),
                    'text_segment': location_text[:200] + "..." if len(location_text) > 200 else location_text
                }
        
        # Determine primary destination (first mentioned or most detailed)
        primary_destination = all_destinations[0] if all_destinations else 'Not specified'
        
        return {
            'type': 'MULTI_LEG',
            'primary_destination': primary_destination,
            'all_destinations': list(set(all_destinations)),  # Remove duplicates
            'location_specific': location_specific
        }
    
    def _split_text_by_locations(self, text: str) -> List[str]:
        """Split text into location-specific segments"""
        # Pattern to identify location transitions
        location_transition_patterns = [
            r'for\s+(\w+).*?(?=for\s+\w+|$)',
            r'in\s+(\w+).*?(?=in\s+\w+|$)',
            r'(\w+).*?(?=\w+.*?night|$)'
        ]
        
        segments = []
        
        # Try to split by sentences first
        sentences = re.split(r'[.!?]\s+', text)
        
        current_segment = ""
        for sentence in sentences:
            # Check if this sentence mentions a new location
            destinations = self.ner_extractor.extract_with_confidence(sentence, 'destinations')
            
            if destinations['value'] and current_segment:
                # New location found, save current segment
                segments.append(current_segment.strip())
                current_segment = sentence
            else:
                current_segment += " " + sentence
        
        # Add the final segment
        if current_segment.strip():
            segments.append(current_segment.strip())
        
        # If no clear splits found, return the whole text
        if not segments:
            segments = [text]
        
        return segments


class ExcelGenerator:
    """
    Generate user-friendly Excel reports for travel inquiries
    """
    
    def __init__(self):
        """Initialize Excel generator"""
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_inquiry_report(self, processed_data: Dict[str, Any]) -> str:
        """
        Generate Excel report for processed inquiry
        
        Args:
            processed_data (Dict): Processed inquiry data
            
        Returns:
            str: Path to generated Excel file
        """
        try:
            inquiry_id = processed_data.get('inquiry_id', 'UNKNOWN')
            filename = f"Travel_Inquiry_{inquiry_id}.xlsx"
            filepath = self.output_dir / filename
            
            # Create workbook and worksheet
            import xlsxwriter
            workbook = xlsxwriter.Workbook(str(filepath))
            worksheet = workbook.add_worksheet('Travel Inquiry Details')
            
            # Define formats
            bold_format = workbook.add_format({'bold': True, 'font_size': 12})
            header_format = workbook.add_format({
                'bold': True, 
                'font_size': 14, 
                'bg_color': '#4F81BD',
                'font_color': 'white'
            })
            location_format = workbook.add_format({
                'bold': True, 
                'font_size': 13, 
                'bg_color': '#B8CCE4'
            })
            
            row = 0
            
            # Header
            worksheet.write(row, 0, 'TRAVEL INQUIRY DETAILS', header_format)
            worksheet.merge_range(row, 0, row, 3, 'TRAVEL INQUIRY DETAILS', header_format)
            row += 2
            
            # Basic Information
            basic_info = processed_data.get('basic_info', {})
            
            worksheet.write(row, 0, 'INQUIRY ID:', bold_format)
            worksheet.write(row, 1, inquiry_id)
            row += 1
            
            worksheet.write(row, 0, 'INQUIRY TYPE:', bold_format)
            worksheet.write(row, 1, processed_data.get('inquiry_type', {}).get('type', 'Unknown'))
            row += 1
            
            worksheet.write(row, 0, 'LANGUAGE:', bold_format)
            worksheet.write(row, 1, processed_data.get('language_info', {}).get('primary_language', 'Unknown'))
            row += 1
            
            worksheet.write(row, 0, 'SENDER:', bold_format)
            worksheet.write(row, 1, basic_info.get('sender', 'Unknown'))
            row += 1
            
            worksheet.write(row, 0, 'CONTACT EMAIL:', bold_format)
            worksheet.write(row, 1, basic_info.get('contact_email', {}).get('value', 'Not provided'))
            row += 1
            
            worksheet.write(row, 0, 'PHONE:', bold_format)
            worksheet.write(row, 1, basic_info.get('phone', {}).get('value', 'Not provided'))
            row += 2
            
            # General Details
            worksheet.write(row, 0, 'TOTAL TRAVELERS:', bold_format)
            travelers_info = basic_info.get('travelers', {})
            worksheet.write(row, 1, travelers_info.get('value', 'Not specified'))
            row += 1
            
            worksheet.write(row, 0, 'TOTAL BUDGET:', bold_format)
            budget_info = basic_info.get('budget', {})
            worksheet.write(row, 1, budget_info.get('value', 'Not specified'))
            row += 1
            
            worksheet.write(row, 0, 'TOTAL DURATION:', bold_format)
            duration_info = basic_info.get('duration', {})
            worksheet.write(row, 1, duration_info.get('value', 'Not specified'))
            row += 1
            
            worksheet.write(row, 0, 'DESTINATIONS:', bold_format)
            dest_info = basic_info.get('destinations', {})
            destinations = ', '.join(dest_info.get('value', [])) if dest_info.get('value') else 'Not specified'
            worksheet.write(row, 1, destinations)
            row += 2
            
            # Location-specific details
            location_details = processed_data.get('location_details', {})
            
            if location_details.get('type') == 'MULTI_LEG':
                worksheet.write(row, 0, 'LOCATION-SPECIFIC DETAILS:', location_format)
                worksheet.merge_range(row, 0, row, 3, 'LOCATION-SPECIFIC DETAILS:', location_format)
                row += 2
                
                location_specific = location_details.get('location_specific', {})
                
                for location, details in location_specific.items():
                    # Location header
                    worksheet.write(row, 0, f'LOCATION: {location.upper()}', location_format)
                    worksheet.merge_range(row, 0, row, 3, f'LOCATION: {location.upper()}', location_format)
                    row += 1
                    
                    # Location details
                    worksheet.write(row, 1, 'Number of Travellers:', bold_format)
                    worksheet.write(row, 2, details.get('travelers', {}).get('value', 'Not specified'))
                    row += 1
                    
                    worksheet.write(row, 1, 'Duration:', bold_format)
                    worksheet.write(row, 2, details.get('duration', {}).get('value', 'Not specified'))
                    row += 1
                    
                    worksheet.write(row, 1, 'Hotel Preferences:', bold_format)
                    hotel_prefs = details.get('hotel_preferences', {}).get('value', [])
                    worksheet.write(row, 2, ', '.join(hotel_prefs) if hotel_prefs else 'Not specified')
                    row += 1
                    
                    worksheet.write(row, 1, 'Activities:', bold_format)
                    activities = details.get('activities', {}).get('value', [])
                    worksheet.write(row, 2, ', '.join(activities) if activities else 'Not specified')
                    row += 1
                    
                    worksheet.write(row, 1, 'Special Requirements:', bold_format)
                    special_reqs = details.get('special_requirements', {}).get('value', [])
                    worksheet.write(row, 2, ', '.join(special_reqs) if special_reqs else 'Not specified')
                    row += 2
            
            else:
                # Single leg details
                worksheet.write(row, 0, 'GENERAL PREFERENCES:', bold_format)
                row += 1
                
                worksheet.write(row, 0, 'Hotel Preferences:', bold_format)
                hotel_prefs = basic_info.get('hotel_preferences', {}).get('value', [])
                worksheet.write(row, 1, ', '.join(hotel_prefs) if hotel_prefs else 'Not specified')
                row += 1
                
                worksheet.write(row, 0, 'Activities:', bold_format)
                activities = basic_info.get('activities', {}).get('value', [])
                worksheet.write(row, 1, ', '.join(activities) if activities else 'Not specified')
                row += 1
                
                worksheet.write(row, 0, 'Special Requirements:', bold_format)
                special_reqs = basic_info.get('special_requirements', {}).get('value', [])
                worksheet.write(row, 1, ', '.join(special_reqs) if special_reqs else 'Not specified')
                row += 2
            
            # Raw email data
            worksheet.write(row, 0, 'RAW EMAIL DATA:', header_format)
            worksheet.merge_range(row, 0, row, 3, 'RAW EMAIL DATA:', header_format)
            row += 1
            
            raw_data = processed_data.get('raw_data', {})
            
            worksheet.write(row, 0, 'Subject:', bold_format)
            worksheet.write(row, 1, raw_data.get('subject', ''))
            row += 1
            
            worksheet.write(row, 0, 'Body:', bold_format)
            body_text = raw_data.get('body', '')[:500] + "..." if len(raw_data.get('body', '')) > 500 else raw_data.get('body', '')
            worksheet.write(row, 1, body_text)
            
            # Adjust column widths
            worksheet.set_column(0, 0, 25)
            worksheet.set_column(1, 1, 40)
            worksheet.set_column(2, 2, 30)
            worksheet.set_column(3, 3, 20)
            
            workbook.close()
            
            logger.info(f"Excel report generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating Excel report: {e}")
            return None


def main():
    """
    Main function to run the travel agent system on live emails only
    """
    processor = TravelAgentProcessor()
    excel_generator = ExcelGenerator()

    try:
        live_emails = fetch_live_emails()
        
        if not live_emails:
            logger.warning("No live emails fetched. Exiting.")
            return

        logger.info(f"{len(live_emails)} live emails fetched. Starting processing...")

        for inquiry in live_emails:
            result = processor.process_inquiry(inquiry)
            excel_path = excel_generator.generate_inquiry_report(result)

            logger.info(f"Processed Inquiry ID: {result.get('inquiry_id')}")
            logger.info(f"Language Detected: {result.get('language_info', {}).get('primary_language')}")
            logger.info(f"Inquiry Type: {result.get('inquiry_type', {}).get('type')}")
            logger.info(f"Destinations: {result.get('location_details', {}).get('all_destinations')}")
            logger.info(f"Excel Generated At: {excel_path}")

    except Exception as e:
        logger.error(f"Critical failure during processing: {e}")


if __name__ == "__main__":
    main()