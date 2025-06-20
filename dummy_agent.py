#!/usr/bin/env python3
"""
Dummy Agent for Testing Optimized Travel Agent System
Tests with dummy email data across all inquiry types and languages
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any, List
from optimized_agent import OptimizedTravelAgentProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dummy_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DummyTravelAgent:
    """
    Dummy agent for testing the optimized travel agent with sample inquiries
    """
    
    def __init__(self):
        """Initialize dummy agent"""
        self.processor = OptimizedTravelAgentProcessor()
        self.test_results = []
        logger.info("Dummy Travel Agent initialized for testing")
    
    def create_dummy_inquiries(self) -> List[Dict[str, Any]]:
        """Create comprehensive dummy inquiries for testing"""
        
        return [
            # SINGLE_LEG - English
            {
                'subject': 'Travel Inquiry – 2 adults + 1 child to Thailand',
                'body': '''Hi Team,

Hope you're doing well. A client is planning a 6 nights / 7 days trip to Thailand for 3 travelers (including 2 adults and 1 child) departing from Mumbai between 15 March and 21 March. Preferred hotel is 4-star with breakfast and dinner. They would like to include Bangkok city tour, Pattaya beach, and floating market. Flights are required. Special request: child-friendly activities. Budget is around ₹45000 per person. Kindly send 2 package options by tomorrow.

Regards,
Sarah Johnson''',
                'sender': 'sarah.johnson@example.com'
            },
            
            # SINGLE_LEG - Hindi
            {
                'subject': 'यात्रा पूछताछ – Rajasthan के लिए 4 वयस्क',
                'body': '''नमस्ते,

एक क्लाइंट 5 nights / 6 days के लिए Rajasthan जाना चाहता है, कुल यात्री 4 (जिसमें 4 वयस्क) प्रस्थान शहर: Delhi, समय: 10 December से 15 December. होटल: heritage hotel जिसमें all meals शामिल। गतिविधियाँ: Jaipur city tour, Udaipur lake tour, camel safari. फ्लाइट्स आवश्यक नहीं हैं। विशेष अनुरोध: cultural programs. बजट: ₹35000/व्यक्ति. कृपया 2 पैकेज विकल्प ASAP भेजें।

धन्यवाद,
Priya Sharma''',
                'sender': 'priya.sharma@example.com'
            },
            
            # SINGLE_LEG - Hindi-English
            {
                'subject': 'Kashmir ke liye yatra enquiry – 3 adults + 2 children',
                'body': '''Namaste,

Ek client 4 nights / 5 days ke liye Kashmir jana chahta hai for 5 travellers (jisme 3 adults and 2 children) departing from Bangalore between 20 May and 24 May. Hotel preference: houseboat with Kashmiri meals. Activities: Shikara ride, Gulmarg gondola, Dal Lake tour. Flights required hai. Special request: warm clothing arrangement. Budget ~₹40000/person. Please send 2 options within 3 days.

Thanks,
Rajesh Kumar''',
                'sender': 'rajesh.kumar@example.com'
            },
            
            # SINGLE_LEG - Hinglish
            {
                'subject': 'Himachal trip enquiry – 6 adults',
                'body': '''Hi Team,

Hamare client ko 7 nights / 8 days ka trip chahiye to Himachal for 6 travellers (jisme 6 adults) departing from Delhi between 25 June and 02 July. Hotel preference: mountain resort with breakfast only. Activities include trekking, river rafting, and temple visits. Flights not required. Special request: adventure sports equipment. Budget approx ₹30000/person. Send 2 options by EOD.

Regards,
Amit Patel''',
                'sender': 'amit.patel@example.com'
            },
            
            # MULTI_LEG - English
            {
                'subject': 'Travel Plans for 8 Pax – Dubai & Singapore (10 Days)',
                'body': '''Hello Team,

We are a group of 8 (including 5 adults and 3 children) planning a 10-day trip from 05 January to 14 January, departing from Chennai.
For Dubai, we'd like 4 nights in a 5-star hotel with breakfast and dinner. Transportation: private car. Activities: Desert Safari, Burj Khalifa, and Dubai Mall.
For Singapore, we'd like 4 nights in a 4-star hotel with breakfast only. Transportation: MRT pass. Activities: Universal Studios, Gardens by the Bay, and Sentosa.

Also, airport pickups/drop-offs and visa assistance where needed. Flights are required. Our budget is approx ₹80000 per person. Could you share two quotes—one with Indian meals and one international? by tomorrow.

Regards,
David Wilson''',
                'sender': 'david.wilson@example.com'
            },
            
            # MULTI_LEG - Hinglish
            {
                'subject': 'Travel Plans for 4 Pax – Kerala & Tamil Nadu (9 Days)',
                'body': '''Hi Team,

Hamare client 9-day trip ke liye 4 log (jisme 3 adults & 1 child) 12 October se 20 October tak jaana chahte hain. Departure: Mumbai.
Kerala: 4 nights at backwater resort with all meals. Transfer via boat. Activities: houseboat stay & spice plantation tour.
Tamil Nadu: 3 nights at hill station hotel with breakfast and dinner. Transfer via cab. Activities: temple tour & tea garden visit.

Also airport pickup/drop aur train bookings. Flights not required. Budget ~₹55000/person. Please send 2 options—South Indian meals & continental. by day after tomorrow.

Regards,
Neha Gupta''',
                'sender': 'neha.gupta@example.com'
            },
            
            # MODIFICATION - English
            {
                'subject': 'Re: Trip – Group Query for 18 August–25 August',
                'body': '''Hi again,

Client has made some changes to their booking. They would like to add 2 more travelers to the group, making it 7 people total. Also, they want to upgrade hotel category from 3-star to 4-star throughout the trip. Additionally, they prefer to add Indian-style dinners for all days. Kindly update the quote and itinerary Excel and resend by tomorrow evening.

Thanks,
Lisa Martinez''',
                'sender': 'lisa.martinez@example.com'
            },
            
            # MODIFICATION - Hindi-English
            {
                'subject': 'Re: Trip – Group Query for 22 November–28 November',
                'body': '''Hi dobara,

Client ne kuch important changes kiye hain. They would like to change travel dates from 22 November to 25 December to 02 January (New Year trip). Also duration increase karna hai from 6 days to 8 days. Hotel preference change - 5-star luxury resorts only. Kindly update the complete quote with new pricing and resend by ASAP.

Shukriya,
Vikash Singh''',
                'sender': 'vikash.singh@example.com'
            }
        ]
    
    def run_dummy_tests(self):
        """Run comprehensive dummy tests"""
        
        logger.info("="*60)
        logger.info("   DUMMY TRAVEL AGENT - COMPREHENSIVE TESTING")
        logger.info("="*60)
        
        dummy_inquiries = self.create_dummy_inquiries()
        
        logger.info(f"Processing {len(dummy_inquiries)} dummy inquiries...")
        
        for i, inquiry in enumerate(dummy_inquiries, 1):
            logger.info(f"\n{'='*50}")
            logger.info(f"Processing Dummy Inquiry {i}/{len(dummy_inquiries)}")
            logger.info(f"Subject: {inquiry['subject'][:50]}...")
            logger.info(f"{'='*50}")
            
            # Process inquiry
            start_time = time.time()
            result = self.processor.process_inquiry(inquiry)
            processing_time = time.time() - start_time
            
            # Generate Excel report
            excel_path = self.processor.excel_generator.generate_inquiry_report(result)
            
            # Analyze and log results
            analysis = self.analyze_results(result, inquiry, processing_time)
            self.test_results.append(analysis)
            
            # Log summary
            self.log_inquiry_summary(i, result, excel_path, analysis)
        
        # Generate final report
        self.generate_final_report()
    
    def analyze_results(self, result: Dict[str, Any], inquiry: Dict[str, Any], 
                       processing_time: float) -> Dict[str, Any]:
        """Analyze processing results"""
        
        analysis = {
            'inquiry_id': result.get('inquiry_id'),
            'processing_time': processing_time,
            'success': not result.get('error', False),
            'completeness_score': result.get('completeness_score', 0),
            'extracted_fields': {}
        }
        
        if analysis['success']:
            # Analyze extracted fields
            analysis['extracted_fields'] = {
                'inquiry_type': result.get('inquiry_type', {}).get('type'),
                'language': result.get('language_info', {}).get('primary_language'),
                'destinations': result.get('location_details', {}).get('all_destinations', []),
                'travelers': result.get('traveler_details', {}).get('total_travelers'),
                'adults': result.get('traveler_details', {}).get('adults'),
                'children': result.get('traveler_details', {}).get('children'),
                'duration': result.get('date_details', {}).get('duration'),
                'start_date': result.get('date_details', {}).get('start_date'),
                'end_date': result.get('date_details', {}).get('end_date'),
                'hotel': result.get('preference_details', {}).get('hotel'),
                'meals': result.get('preference_details', {}).get('meals'),
                'activities': result.get('preference_details', {}).get('activities', []),
                'budget': result.get('budget_details', {}).get('amount'),
                'flight_required': result.get('preference_details', {}).get('flight_required'),
                'special_requirements': result.get('preference_details', {}).get('special_requirements'),
                'deadline': result.get('deadline')
            }
            
            # Count non-null fields
            non_null_fields = sum(1 for v in analysis['extracted_fields'].values() 
                                if v is not None and (not isinstance(v, list) or len(v) > 0))
            analysis['fields_extracted'] = non_null_fields
            analysis['total_fields'] = len(analysis['extracted_fields'])
            analysis['field_extraction_rate'] = (non_null_fields / analysis['total_fields']) * 100
        
        return analysis
    
    def log_inquiry_summary(self, inquiry_num: int, result: Dict[str, Any], 
                          excel_path: str, analysis: Dict[str, Any]):
        """Log summary for single inquiry"""
        
        logger.info(f"✓ INQUIRY {inquiry_num} RESULTS:")
        logger.info(f"  ID: {analysis['inquiry_id']}")
        logger.info(f"  Success: {'Yes' if analysis['success'] else 'No'}")
        logger.info(f"  Processing Time: {analysis['processing_time']:.2f}s")
        logger.info(f"  Completeness: {analysis['completeness_score']:.1f}%")
        
        if analysis['success']:
            fields = analysis['extracted_fields']
            logger.info(f"  Type: {fields['inquiry_type']}")
            logger.info(f"  Language: {fields['language']}")
            logger.info(f"  Destinations: {', '.join(fields['destinations']) if fields['destinations'] else 'None'}")
            logger.info(f"  Travelers: {fields['travelers']} ({fields['adults']} adults, {fields['children']} children)")
            logger.info(f"  Duration: {fields['duration'] or 'Not specified'}")
            logger.info(f"  Budget: {fields['budget'] or 'Not specified'}")
            logger.info(f"  Fields Extracted: {analysis['fields_extracted']}/{analysis['total_fields']} ({analysis['field_extraction_rate']:.1f}%)")
        
        logger.info(f"  Excel Generated: {excel_path}")
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        
        logger.info("\n" + "="*80)
        logger.info("DUMMY AGENT - FINAL COMPREHENSIVE REPORT")
        logger.info("="*80)
        
        total_inquiries = len(self.test_results)
        successful_inquiries = sum(1 for r in self.test_results if r['success'])
        avg_processing_time = sum(r['processing_time'] for r in self.test_results) / total_inquiries
        avg_completeness = sum(r['completeness_score'] for r in self.test_results) / total_inquiries
        avg_field_extraction = sum(r.get('field_extraction_rate', 0) for r in self.test_results) / total_inquiries
        
        logger.info(f"\n📊 OVERALL STATISTICS:")
        logger.info(f"Total Inquiries Processed: {total_inquiries}")
        logger.info(f"Successful Extractions: {successful_inquiries}/{total_inquiries} ({(successful_inquiries/total_inquiries)*100:.1f}%)")
        logger.info(f"Average Processing Time: {avg_processing_time:.2f} seconds")
        logger.info(f"Average Completeness Score: {avg_completeness:.1f}%")
        logger.info(f"Average Field Extraction Rate: {avg_field_extraction:.1f}%")
        
        # Analyze by inquiry type
        type_stats = {}
        for result in self.test_results:
            if result['success']:
                inquiry_type = result['extracted_fields']['inquiry_type']
                if inquiry_type not in type_stats:
                    type_stats[inquiry_type] = []
                type_stats[inquiry_type].append(result)
        
        logger.info(f"\n📈 ACCURACY BY INQUIRY TYPE:")
        for inquiry_type, results in type_stats.items():
            avg_score = sum(r['completeness_score'] for r in results) / len(results)
            logger.info(f"{inquiry_type}: {len(results)} samples, {avg_score:.1f}% avg completeness")
        
        # Analyze by language
        lang_stats = {}
        for result in self.test_results:
            if result['success']:
                language = result['extracted_fields']['language']
                if language not in lang_stats:
                    lang_stats[language] = []
                lang_stats[language].append(result)
        
        logger.info(f"\n🌐 ACCURACY BY LANGUAGE:")
        for language, results in lang_stats.items():
            avg_score = sum(r['completeness_score'] for r in results) / len(results)
            logger.info(f"{language}: {len(results)} samples, {avg_score:.1f}% avg completeness")
        
        # Performance assessment
        logger.info(f"\n🎯 PERFORMANCE ASSESSMENT:")
        if avg_completeness >= 95:
            logger.info("✅ EXCELLENT: 95%+ completeness achieved!")
        elif avg_completeness >= 90:
            logger.info("✅ VERY GOOD: 90%+ completeness achieved!")
        elif avg_completeness >= 80:
            logger.info("⚠️  GOOD: 80%+ completeness - minor optimizations may help")
        else:
            logger.info("❌ NEEDS IMPROVEMENT: <80% completeness - review extraction patterns")
        
        logger.info(f"\n💾 All Excel reports generated in 'output/' directory")
        logger.info(f"📝 Detailed logs saved to 'dummy_agent.log'")
        logger.info("\n" + "="*80)
        logger.info("DUMMY AGENT TESTING COMPLETED SUCCESSFULLY")
        logger.info("="*80)

def main():
    """Main dummy agent execution"""
    print("🤖 Starting Dummy Travel Agent Testing...")
    
    dummy_agent = DummyTravelAgent()
    dummy_agent.run_dummy_tests()
    
    print("\n✅ Dummy agent testing completed!")
    print("📁 Check 'output/' directory for generated Excel reports")
    print("📋 Check 'dummy_agent.log' for detailed processing logs")

if __name__ == "__main__":
    main()