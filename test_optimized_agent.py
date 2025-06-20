#!/usr/bin/env python3
"""
Comprehensive Test Suite for Optimized Travel Agent
Tests extraction accuracy across all inquiry types and languages using real data samples
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List
import json
from optimized_agent import OptimizedTravelAgentProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OptimizedAgentTester:
    """
    Comprehensive tester for optimized travel agent
    Tests accuracy across all inquiry types and languages
    """
    
    def __init__(self):
        """Initialize tester"""
        self.processor = OptimizedTravelAgentProcessor()
        self.results = {
            'total_tested': 0,
            'successful_extractions': 0,
            'by_type': {},
            'by_language': {},
            'field_accuracy': {},
            'detailed_results': []
        }
        logger.info("Optimized Agent Tester initialized")
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive tests across all data samples"""
        
        # Test categories
        test_categories = [
            ('SINGLE_LEN', ['english_single_len', 'hindi_single_len', 'hindi_english_single_len', 'hinglish_single_len']),
            ('MULTI_LEN', ['english_multi_len', 'hindi_multi_len', 'hindi_english_multi_len', 'hinglish_multi_len']),
            ('MODIFICATION', ['english_modification', 'hindi_modification', 'hindi_english_modification', 'hinglish_modification'])
        ]
        
        logger.info("Starting comprehensive testing...")
        
        for inquiry_type, language_dirs in test_categories:
            logger.info(f"\nTesting {inquiry_type} inquiries...")
            
            for lang_dir in language_dirs:
                self.test_language_category(inquiry_type, lang_dir)
        
        # Generate final report
        self.generate_test_report()
        return self.results
    
    def test_language_category(self, inquiry_type: str, lang_dir: str):
        """Test specific language category"""
        
        base_path = Path(f"DATA/{inquiry_type}/{lang_dir}")
        if not base_path.exists():
            logger.warning(f"Directory not found: {base_path}")
            return
        
        # Test first 10 samples from each category for comprehensive analysis
        sample_files = sorted(list(base_path.glob("*.txt")))[:10]
        
        logger.info(f"Testing {len(sample_files)} samples from {lang_dir}...")
        
        category_results = {
            'total': len(sample_files),
            'successful': 0,
            'failed': 0,
            'accuracy_scores': []
        }
        
        for sample_file in sample_files:
            try:
                # Read sample file
                with open(sample_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                # Parse content (assuming subject and body format)
                lines = content.split('\n')
                subject = lines[0].replace('Subject: ', '') if lines else ''
                body = '\n'.join(lines[1:]) if len(lines) > 1 else content
                
                # Create email data
                email_data = {
                    'subject': subject,
                    'body': body,
                    'sender': 'test@example.com'
                }
                
                # Process inquiry
                result = self.processor.process_inquiry(email_data)
                
                # Analyze results
                analysis = self.analyze_extraction_result(result, inquiry_type, lang_dir, sample_file.name)
                
                if analysis['success']:
                    category_results['successful'] += 1
                else:
                    category_results['failed'] += 1
                
                category_results['accuracy_scores'].append(analysis['accuracy_score'])
                self.results['detailed_results'].append(analysis)
                
                logger.info(f"✓ {sample_file.name}: {analysis['accuracy_score']:.1f}% accuracy")
                
            except Exception as e:
                logger.error(f"✗ Error processing {sample_file.name}: {e}")
                category_results['failed'] += 1
        
        # Update overall results
        self.update_results(inquiry_type, lang_dir, category_results)
    
    def analyze_extraction_result(self, result: Dict[str, Any], expected_type: str, 
                                lang_dir: str, filename: str) -> Dict[str, Any]:
        """Analyze extraction accuracy"""
        
        analysis = {
            'filename': filename,
            'expected_type': expected_type,
            'language_category': lang_dir,
            'success': False,
            'accuracy_score': 0.0,
            'field_scores': {},
            'issues': []
        }
        
        if result.get('error'):
            analysis['issues'].append(f"Processing error: {result.get('error_message')}")
            return analysis
        
        # Check inquiry type accuracy
        detected_type = result.get('inquiry_type', {}).get('type', '').upper()
        if detected_type == expected_type:
            analysis['field_scores']['inquiry_type'] = 100.0
        else:
            analysis['field_scores']['inquiry_type'] = 0.0
            analysis['issues'].append(f"Type mismatch: expected {expected_type}, got {detected_type}")
        
        # Check language detection
        detected_lang = result.get('language_info', {}).get('primary_language', '')
        expected_lang = self.get_expected_language(lang_dir)
        if detected_lang == expected_lang:
            analysis['field_scores']['language'] = 100.0
        else:
            analysis['field_scores']['language'] = 0.0
            analysis['issues'].append(f"Language mismatch: expected {expected_lang}, got {detected_lang}")
        
        # Check field extraction completeness
        field_scores = self.check_field_completeness(result, expected_type)
        analysis['field_scores'].update(field_scores)
        
        # Calculate overall accuracy
        all_scores = list(analysis['field_scores'].values())
        analysis['accuracy_score'] = sum(all_scores) / len(all_scores) if all_scores else 0.0
        analysis['success'] = analysis['accuracy_score'] >= 80.0  # 80% threshold for success
        
        return analysis
    
    def get_expected_language(self, lang_dir: str) -> str:
        """Get expected language from directory name"""
        if 'english' in lang_dir and 'hindi' not in lang_dir:
            return 'english'
        elif 'hindi_english' in lang_dir:
            return 'hindi_english'
        elif 'hinglish' in lang_dir:
            return 'hinglish'
        elif 'hindi' in lang_dir:
            return 'hindi'
        else:
            return 'english'  # default
    
    def check_field_completeness(self, result: Dict[str, Any], inquiry_type: str) -> Dict[str, float]:
        """Check completeness of extracted fields"""
        
        field_scores = {}
        
        # Core fields (required for all types)
        core_fields = {
            'destinations': result.get('location_details', {}).get('all_destinations', []),
            'travelers': result.get('traveler_details', {}).get('total_travelers'),
            'customer_email': result.get('customer_details', {}).get('email')
        }
        
        for field, value in core_fields.items():
            if value and (not isinstance(value, list) or len(value) > 0):
                field_scores[field] = 100.0
            else:
                field_scores[field] = 0.0
        
        # Optional but important fields
        optional_fields = {
            'duration': result.get('date_details', {}).get('duration'),
            'start_date': result.get('date_details', {}).get('start_date'),
            'end_date': result.get('date_details', {}).get('end_date'),
            'adults': result.get('traveler_details', {}).get('adults'),
            'children': result.get('traveler_details', {}).get('children'),
            'hotel_preferences': result.get('preference_details', {}).get('hotel'),
            'meal_preferences': result.get('preference_details', {}).get('meals'),
            'activities': result.get('preference_details', {}).get('activities', []),
            'budget': result.get('budget_details', {}).get('amount'),
            'flight_required': result.get('preference_details', {}).get('flight_required'),
            'special_requirements': result.get('preference_details', {}).get('special_requirements'),
            'deadline': result.get('deadline')
        }
        
        for field, value in optional_fields.items():
            if value is not None and (not isinstance(value, list) or len(value) > 0):
                field_scores[field] = 100.0
            else:
                field_scores[field] = 50.0  # Partial credit for optional fields
        
        return field_scores
    
    def update_results(self, inquiry_type: str, lang_dir: str, category_results: Dict[str, Any]):
        """Update overall test results"""
        
        self.results['total_tested'] += category_results['total']
        self.results['successful_extractions'] += category_results['successful']
        
        # By type
        if inquiry_type not in self.results['by_type']:
            self.results['by_type'][inquiry_type] = {'total': 0, 'successful': 0, 'accuracy': 0.0}
        
        self.results['by_type'][inquiry_type]['total'] += category_results['total']
        self.results['by_type'][inquiry_type]['successful'] += category_results['successful']
        
        # By language
        language = self.get_expected_language(lang_dir)
        if language not in self.results['by_language']:
            self.results['by_language'][language] = {'total': 0, 'successful': 0, 'accuracy': 0.0}
        
        self.results['by_language'][language]['total'] += category_results['total']
        self.results['by_language'][language]['successful'] += category_results['successful']
        
        # Calculate accuracy percentages
        for category in [self.results['by_type'][inquiry_type], self.results['by_language'][language]]:
            if category['total'] > 0:
                category['accuracy'] = (category['successful'] / category['total']) * 100.0
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        
        logger.info("\n" + "="*80)
        logger.info("OPTIMIZED TRAVEL AGENT - COMPREHENSIVE TEST RESULTS")
        logger.info("="*80)
        
        # Overall summary
        overall_accuracy = (self.results['successful_extractions'] / self.results['total_tested']) * 100.0 if self.results['total_tested'] > 0 else 0.0
        
        logger.info(f"\nOVERALL RESULTS:")
        logger.info(f"Total Tested: {self.results['total_tested']}")
        logger.info(f"Successful: {self.results['successful_extractions']}")
        logger.info(f"Overall Accuracy: {overall_accuracy:.1f}%")
        
        # By inquiry type
        logger.info(f"\nACCURACY BY INQUIRY TYPE:")
        for inquiry_type, stats in self.results['by_type'].items():
            logger.info(f"{inquiry_type}: {stats['successful']}/{stats['total']} ({stats['accuracy']:.1f}%)")
        
        # By language
        logger.info(f"\nACCURACY BY LANGUAGE:")
        for language, stats in self.results['by_language'].items():
            logger.info(f"{language}: {stats['successful']}/{stats['total']} ({stats['accuracy']:.1f}%)")
        
        # Field-wise accuracy
        self.calculate_field_accuracy()
        logger.info(f"\nFIELD EXTRACTION ACCURACY:")
        for field, accuracy in sorted(self.results['field_accuracy'].items()):
            logger.info(f"{field}: {accuracy:.1f}%")
        
        # Save detailed results
        self.save_detailed_results()
        
        logger.info("\n" + "="*80)
        logger.info("TEST COMPLETED - Check test_results.json for detailed analysis")
        logger.info("="*80)
    
    def calculate_field_accuracy(self):
        """Calculate field-wise extraction accuracy"""
        
        field_totals = {}
        field_counts = {}
        
        for result in self.results['detailed_results']:
            for field, score in result['field_scores'].items():
                if field not in field_totals:
                    field_totals[field] = 0.0
                    field_counts[field] = 0
                
                field_totals[field] += score
                field_counts[field] += 1
        
        # Calculate averages
        for field in field_totals:
            if field_counts[field] > 0:
                self.results['field_accuracy'][field] = field_totals[field] / field_counts[field]
    
    def save_detailed_results(self):
        """Save detailed test results to JSON"""
        
        output_file = "test_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Detailed results saved to {output_file}")

def main():
    """Main test function"""
    logger.info("Starting Optimized Travel Agent Comprehensive Testing...")
    
    tester = OptimizedAgentTester()
    results = tester.run_comprehensive_tests()
    
    # Quick summary
    overall_accuracy = (results['successful_extractions'] / results['total_tested']) * 100.0 if results['total_tested'] > 0 else 0.0
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"Overall Accuracy: {overall_accuracy:.1f}%")
    print(f"Total Samples Tested: {results['total_tested']}")
    print(f"Successful Extractions: {results['successful_extractions']}")
    
    if overall_accuracy >= 95.0:
        print("✅ EXCELLENT: 95%+ accuracy achieved!")
    elif overall_accuracy >= 90.0:
        print("✅ VERY GOOD: 90%+ accuracy achieved!")
    elif overall_accuracy >= 80.0:
        print("⚠️  GOOD: 80%+ accuracy achieved - some optimization needed")
    else:
        print("❌ NEEDS IMPROVEMENT: <80% accuracy - significant optimization required")

if __name__ == "__main__":
    main()