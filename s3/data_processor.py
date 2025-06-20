#!/usr/bin/env python3
"""
Optimized Data Processor for AI Travel Agent
Processes sample data across all inquiry types and languages for accuracy testing
"""

import os
import json
import csv
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict


class OptimizedInquiryProcessor:
    """Optimized processor for multilingual travel inquiries"""
    
    def __init__(self):
        self.setup_enhanced_patterns()
        self.setup_language_patterns()
        self.output_dir = Path("output/optimized_quotes")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics tracking
        self.processing_stats = {
            'total_processed': 0,
            'successful': 0,
            'errors': 0,
            'by_type': defaultdict(int),
            'by_language': defaultdict(int),
            'extraction_accuracy': defaultdict(list)
        }
    
    def setup_enhanced_patterns(self):
        """Setup enhanced regex patterns for better extraction"""
        self.patterns = {
            # Enhanced email patterns
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            
            # Enhanced phone patterns
            'phone': r'(?:\+91[-\s]?)?[6-9]\d{9}',
            
            # Enhanced currency patterns (multiple formats)
            'currency_inr': r'(?:Rs\.?|INR|₹)\s*[\d,]+(?:\.\d{2})?',
            'currency_per_person': r'(?:Rs\.?|INR|₹)\s*[\d,]+(?:\.\d{2})?\s*(?:per person|प्रति व्यक्ति|per pax)',
            
            # Enhanced date patterns
            'date_patterns': [
                r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',
                r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?\b'
            ],
            
            # Enhanced traveler patterns
            'travelers': [
                r'(\d+)\s*(?:people|persons?|travelers?|pax|adults?|log|यात्री)',
                r'family of\s*(\d+)',
                r'group of\s*(\d+)',
                r'(\d+)\s*adults?\s*\+\s*(\d+)\s*(?:kids?|children?)',
                r'total\s*(?:of\s*)?(\d+)\s*(?:people|persons?|log)'
            ],
            
            # Enhanced duration patterns
            'duration': [
                r'(\d+)\s*nights?\s*/?(?:\s*(\d+)\s*days?)?',
                r'(\d+)\s*days?\s*/?(?:\s*(\d+)\s*nights?)?'
            ],
            
            # Hotel and accommodation patterns
            'hotel_category': r'(\d+)\s*[-]?star\s*hotel',
            'accommodation_type': r'(water villa|resort|hotel|houseboat|homestay)',
            'meal_plan': r'(breakfast|lunch|dinner|all meals|veg meals|Indian-style)',
            
            # Transportation patterns
            'transportation': r'(flights?|taxi|public transport|private car|driver)',
            
            # Activity patterns
            'activities': r'(?:include|activities?|want to do|hoping to do)[:\s]*([^.]+)',
            
            # Special requirements patterns
            'special_requests': r'(?:special request|विशेष अनुरोध)[:\s]*([^.]+)'
        }
    
    def setup_language_patterns(self):
        """Setup language-specific patterns and destination lists"""
        # Comprehensive destination lists
        self.destinations = {
            'international': [
                'maldives', 'thailand', 'bali', 'europe', 'venice', 'paris', 'swiss alps',
                'kashmir', 'singapore', 'dubai', 'malaysia', 'sri lanka', 'bhutan',
                'nepal', 'vietnam', 'cambodia', 'japan', 'south korea'
            ],
            'indian': [
                'kerala', 'goa', 'rajasthan', 'himachal', 'kashmir', 'delhi', 'mumbai',
                'bangalore', 'hyderabad', 'chennai', 'kolkata', 'pune', 'ahmedabad',
                'jaipur', 'udaipur', 'jodhpur', 'manali', 'shimla', 'darjeeling',
                'ooty', 'kodaikanal', 'munnar', 'alleppey', 'kochi', 'trivandrum',
                'pondicherry', 'mahabalipuram', 'hampi', 'mysore', 'coorg', 'agra',
                'varanasi', 'rishikesh', 'haridwar', 'amritsar', 'chandigarh',
                'cochin', 'periyar', 'pahalgam', 'gulmarg', 'kufri', 'solang valley',
                'mall road', 'phi phi island', 'james bond island', 'ubud', 'kintamani'
            ]
        }
        
        # Language detection patterns
        self.language_indicators = {
            'hindi': ['नमस्ते', 'विषय', 'यात्रा', 'के लिए', 'चाहिए', 'शुभकामनाएं', 'कृपया'],
            'hindi_english': ['namaste', 'yatra', 'ke liye', 'chahiye', 'bhej do', 'hai'],
            'hinglish': ['hamare', 'hona chahiye', 'include honi chahiye', 'jaldi', 'finalize karna']
        }
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the inquiry"""
        text_lower = text.lower()
        
        # Check for Hindi script
        if any(ord(char) >= 0x900 and ord(char) <= 0x97F for char in text):
            return 'hindi'
        
        # Check for Hindi-English indicators
        hindi_english_count = sum(1 for phrase in self.language_indicators['hindi_english'] 
                                 if phrase in text_lower)
        
        # Check for Hinglish indicators
        hinglish_count = sum(1 for phrase in self.language_indicators['hinglish'] 
                            if phrase in text_lower)
        
        if hinglish_count > 2:
            return 'hinglish'
        elif hindi_english_count > 1:
            return 'hindi_english'
        else:
            return 'english'
    
    def determine_inquiry_type(self, text: str) -> str:
        """Determine inquiry type with enhanced patterns"""
        text_lower = text.lower()
        
        # Modification indicators
        modification_indicators = [
            'modify', 'change', 'update', 'revise', 'made some changes',
            'skip one destination', 'upgraded hotels', 'update the quote',
            're:', 'again', 'resend'
        ]
        
        if any(indicator in text_lower for indicator in modification_indicators):
            return 'MODIFICATION'
        
        # Multi-leg indicators
        multi_leg_indicators = [
            'then', 'next', 'followed by', 'first', 'multiple destination',
            'for kashmir', 'for bali', 'stay 5 nights', 'stay 2 nights',
            'each locale', 'at each'
        ]
        
        # Count destinations mentioned
        all_destinations = self.destinations['international'] + self.destinations['indian']
        dest_count = sum(1 for dest in all_destinations if dest in text_lower)
        
        if any(indicator in text_lower for indicator in multi_leg_indicators) or dest_count > 2:
            return 'MULTI_LEG'
        
        return 'SINGLE_LEG'
    
    def extract_customer_name(self, text: str) -> str:
        """Extract customer name with language-aware patterns"""
        lines = text.strip().split('\n')
        
        # Check signature area (last few lines)
        for line in reversed(lines[-5:]):
            line = line.strip()
            if not line or '@' in line:
                continue
                
            # Remove common salutations
            line = re.sub(r'^(regards,|thanks,|शुभकामनाएं,|best,|sincerely,)\s*', '', line, flags=re.IGNORECASE)
            
            # Check if it looks like a name (2-4 words, no numbers, not too long)
            if line and len(line.split()) <= 4 and not any(char.isdigit() for char in line):
                if len(line) < 50:  # Reasonable name length
                    return line
        
        return 'Valued Customer'
    
    def extract_destinations(self, text: str) -> List[str]:
        """Extract destinations with enhanced multilingual support"""
        text_lower = text.lower()
        destinations = []
        
        # Check all destination lists
        for dest_list in [self.destinations['international'], self.destinations['indian']]:
            for dest in dest_list:
                if dest in text_lower:
                    destinations.append(dest.title())
        
        return list(set(destinations))
    
    def extract_travelers_enhanced(self, text: str) -> Optional[int]:
        """Enhanced traveler extraction with multiple patterns"""
        for pattern in self.patterns['travelers']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:  # Adults + children pattern
                    adults = int(match.group(1))
                    children = int(match.group(2))
                    return adults + children
                else:
                    return int(match.group(1))
        
        return None
    
    def extract_duration_enhanced(self, text: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract duration with nights and days separation"""
        for pattern in self.patterns['duration']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'night' in match.group(0).lower():
                    nights = int(match.group(1))
                    days = int(match.group(2)) if match.group(2) else nights + 1
                else:
                    days = int(match.group(1))
                    nights = int(match.group(2)) if match.group(2) else days - 1
                
                return nights, days
        
        return None, None
    
    def extract_budget_enhanced(self, text: str) -> Dict[str, Any]:
        """Enhanced budget extraction with per-person detection"""
        budget_info = {
            'total_budget': None,
            'per_person_budget': None,
            'currency': 'INR'
        }
        
        # Check for per-person budget first
        per_person_match = re.search(self.patterns['currency_per_person'], text, re.IGNORECASE)
        if per_person_match:
            amount = re.sub(r'[^\d]', '', per_person_match.group(0))
            budget_info['per_person_budget'] = f"₹{amount}"
        
        # Check for general budget
        currency_match = re.search(self.patterns['currency_inr'], text)
        if currency_match and not per_person_match:
            amount = re.sub(r'[^\d]', '', currency_match.group(0))
            budget_info['total_budget'] = f"₹{amount}"
        
        return budget_info
    
    def extract_accommodation_details(self, text: str) -> Dict[str, Any]:
        """Extract accommodation details"""
        details = {
            'hotel_category': None,
            'accommodation_type': None,
            'meal_plan': None
        }
        
        # Hotel category
        hotel_match = re.search(self.patterns['hotel_category'], text, re.IGNORECASE)
        if hotel_match:
            details['hotel_category'] = f"{hotel_match.group(1)}-star"
        
        # Accommodation type
        acc_match = re.search(self.patterns['accommodation_type'], text, re.IGNORECASE)
        if acc_match:
            details['accommodation_type'] = acc_match.group(1)
        
        # Meal plan
        meal_matches = re.findall(self.patterns['meal_plan'], text, re.IGNORECASE)
        if meal_matches:
            details['meal_plan'] = ', '.join(meal_matches)
        
        return details
    
    def extract_special_requirements(self, text: str) -> List[str]:
        """Extract special requirements and activities"""
        requirements = []
        
        # Special requests
        special_match = re.search(self.patterns['special_requests'], text, re.IGNORECASE)
        if special_match:
            requirements.append(f"Special: {special_match.group(1).strip()}")
        
        # Activities
        activity_match = re.search(self.patterns['activities'], text, re.IGNORECASE)
        if activity_match:
            requirements.append(f"Activities: {activity_match.group(1).strip()}")
        
        # Transportation
        transport_matches = re.findall(self.patterns['transportation'], text, re.IGNORECASE)
        if transport_matches:
            requirements.append(f"Transport: {', '.join(transport_matches)}")
        
        # Common special requirements
        if re.search(r'vegetarian|veg', text, re.IGNORECASE):
            requirements.append('Vegetarian meals')
        if re.search(r'wheelchair|accessibility', text, re.IGNORECASE):
            requirements.append('Wheelchair accessibility')
        if re.search(r'birthday|anniversary', text, re.IGNORECASE):
            requirements.append('Special occasion arrangements')
        if re.search(r'late checkout|early checkin', text, re.IGNORECASE):
            requirements.append('Flexible check-in/out')
        
        return requirements
    
    def process_file(self, file_path: Path, inquiry_type: str, language: str) -> Dict[str, Any]:
        """Process a single inquiry file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract subject and body
            lines = content.strip().split('\n')
            subject = lines[0].replace('Subject:', '').strip() if lines[0].startswith('Subject:') else ''
            body = '\n'.join(lines[1:]).strip()
            full_text = f"{subject}\n{body}"
            
            # Generate inquiry ID
            inquiry_id = f"OPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_path.stem}"
            
            # Extract information
            detected_language = self.detect_language(full_text)
            detected_type = self.determine_inquiry_type(full_text)
            customer_name = self.extract_customer_name(body)
            destinations = self.extract_destinations(full_text)
            travelers = self.extract_travelers_enhanced(full_text)
            nights, days = self.extract_duration_enhanced(full_text)
            budget_info = self.extract_budget_enhanced(full_text)
            accommodation = self.extract_accommodation_details(full_text)
            requirements = self.extract_special_requirements(full_text)
            
            # Create result
            result = {
                'file_path': str(file_path),
                'inquiry_id': inquiry_id,
                'expected_type': inquiry_type,
                'detected_type': detected_type,
                'expected_language': language,
                'detected_language': detected_language,
                'subject': subject,
                'customer_name': customer_name,
                'destinations': destinations,
                'num_travelers': travelers,
                'duration_nights': nights,
                'duration_days': days,
                'budget_info': budget_info,
                'accommodation': accommodation,
                'special_requirements': requirements,
                'processing_status': 'success',
                'type_accuracy': detected_type == inquiry_type.upper(),
                'language_accuracy': detected_language == language.replace('_', '_'),
                'extraction_completeness': self.calculate_completeness(result)
            }
            
            return result
            
        except Exception as e:
            return {
                'file_path': str(file_path),
                'processing_status': f'error: {str(e)}',
                'type_accuracy': False,
                'language_accuracy': False,
                'extraction_completeness': 0.0
            }
    
    def calculate_completeness(self, result: Dict[str, Any]) -> float:
        """Calculate extraction completeness score"""
        required_fields = [
            'customer_name', 'destinations', 'num_travelers', 
            'duration_nights', 'budget_info'
        ]
        
        score = 0.0
        for field in required_fields:
            if field == 'customer_name' and result.get(field) != 'Valued Customer':
                score += 0.2
            elif field == 'destinations' and result.get(field):
                score += 0.2
            elif field == 'num_travelers' and result.get(field):
                score += 0.2
            elif field == 'duration_nights' and result.get(field):
                score += 0.2
            elif field == 'budget_info' and (result.get(field, {}).get('total_budget') or 
                                           result.get(field, {}).get('per_person_budget')):
                score += 0.2
        
        return score
    
    def generate_optimization_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        total_files = len(results)
        successful = sum(1 for r in results if r['processing_status'] == 'success')
        
        type_accuracy = sum(1 for r in results if r.get('type_accuracy', False)) / total_files
        language_accuracy = sum(1 for r in results if r.get('language_accuracy', False)) / total_files
        avg_completeness = sum(r.get('extraction_completeness', 0) for r in results) / total_files
        
        # Breakdown by type and language
        by_type = defaultdict(lambda: {'total': 0, 'accurate': 0, 'completeness': []})
        by_language = defaultdict(lambda: {'total': 0, 'accurate': 0, 'completeness': []})
        
        for result in results:
            if result['processing_status'] == 'success':
                exp_type = result['expected_type']
                exp_lang = result['expected_language']
                
                by_type[exp_type]['total'] += 1
                by_language[exp_lang]['total'] += 1
                
                if result.get('type_accuracy', False):
                    by_type[exp_type]['accurate'] += 1
                if result.get('language_accuracy', False):
                    by_language[exp_lang]['accurate'] += 1
                
                by_type[exp_type]['completeness'].append(result.get('extraction_completeness', 0))
                by_language[exp_lang]['completeness'].append(result.get('extraction_completeness', 0))
        
        # Calculate averages
        for category in by_type:
            by_type[category]['accuracy_rate'] = by_type[category]['accurate'] / by_type[category]['total']
            by_type[category]['avg_completeness'] = sum(by_type[category]['completeness']) / len(by_type[category]['completeness'])
        
        for category in by_language:
            by_language[category]['accuracy_rate'] = by_language[category]['accurate'] / by_language[category]['total']
            by_language[category]['avg_completeness'] = sum(by_language[category]['completeness']) / len(by_language[category]['completeness'])
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_files_processed': total_files,
            'successful_processing': successful,
            'success_rate': successful / total_files,
            'overall_type_accuracy': type_accuracy,
            'overall_language_accuracy': language_accuracy,
            'overall_completeness': avg_completeness,
            'by_inquiry_type': dict(by_type),
            'by_language': dict(by_language),
            'recommendations': self.generate_recommendations(by_type, by_language)
        }
    
    def generate_recommendations(self, by_type: dict, by_language: dict) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Type accuracy recommendations
        for inquiry_type, stats in by_type.items():
            if stats['accuracy_rate'] < 0.8:
                recommendations.append(f"Improve {inquiry_type} detection patterns - current accuracy: {stats['accuracy_rate']:.2%}")
        
        # Language accuracy recommendations
        for language, stats in by_language.items():
            if stats['accuracy_rate'] < 0.8:
                recommendations.append(f"Enhance {language} language detection - current accuracy: {stats['accuracy_rate']:.2%}")
        
        # Completeness recommendations
        for inquiry_type, stats in by_type.items():
            if stats['avg_completeness'] < 0.7:
                recommendations.append(f"Improve field extraction for {inquiry_type} - current completeness: {stats['avg_completeness']:.2%}")
        
        return recommendations


def process_sample_data():
    """Process all sample data and generate optimization report"""
    processor = OptimizedInquiryProcessor()
    data_dir = Path("DATA")
    all_results = []
    
    print("=== AI Travel Agent - Sample Data Processing & Optimization ===")
    print(f"Starting optimization analysis at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Process each inquiry type and language combination
    inquiry_types = ['SINGLE_LEG', 'MULTI_LEG', 'MODIFICATION']
    
    for inquiry_type in inquiry_types:
        type_dir = data_dir / inquiry_type
        if not type_dir.exists():
            continue
            
        print(f"\nProcessing {inquiry_type} inquiries...")
        
        # Get language directories
        lang_dirs = [d for d in type_dir.iterdir() if d.is_dir()]
        
        for lang_dir in lang_dirs:
            language = lang_dir.name
            print(f"  Processing {language} samples...")
            
            # Process files in this language directory
            text_files = list(lang_dir.glob("*.txt"))
            processed_count = 0
            
            for file_path in text_files[:20]:  # Process first 20 files for quick analysis
                result = processor.process_file(file_path, inquiry_type, language)
                all_results.append(result)
                processed_count += 1
                
                if processed_count % 5 == 0:
                    print(f"    Processed {processed_count}/{len(text_files[:20])} files")
    
    # Generate optimization report
    print(f"\nGenerating optimization report...")
    report = processor.generate_optimization_report(all_results)
    
    # Save detailed results
    results_file = Path("data/optimization_results.json")
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'report': report,
            'detailed_results': all_results
        }, f, indent=2, ensure_ascii=False, default=str)
    
    # Print summary
    print(f"\n=== Optimization Analysis Results ===")
    print(f"Total files processed: {report['total_files_processed']}")
    print(f"Success rate: {report['success_rate']:.2%}")
    print(f"Type detection accuracy: {report['overall_type_accuracy']:.2%}")
    print(f"Language detection accuracy: {report['overall_language_accuracy']:.2%}")
    print(f"Overall extraction completeness: {report['overall_completeness']:.2%}")
    
    print(f"\n=== By Inquiry Type ===")
    for inquiry_type, stats in report['by_inquiry_type'].items():
        print(f"{inquiry_type}: {stats['accuracy_rate']:.2%} accuracy, {stats['avg_completeness']:.2%} completeness")
    
    print(f"\n=== By Language ===")
    for language, stats in report['by_language'].items():
        print(f"{language}: {stats['accuracy_rate']:.2%} accuracy, {stats['avg_completeness']:.2%} completeness")
    
    if report['recommendations']:
        print(f"\n=== Recommendations ===")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
    
    print(f"\nOptimization analysis saved to: {results_file}")
    return report, all_results


if __name__ == "__main__":
    process_sample_data()