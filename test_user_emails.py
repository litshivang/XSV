#!/usr/bin/env python3
"""
Test the exact user emails to identify and fix classification and extraction issues
"""

import logging
from optimized_agent import OptimizedTravelAgentProcessor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_user_emails():
    """Test the exact emails provided by user"""
    
    processor = OptimizedTravelAgentProcessor()
    
    # User's SINGLE_LEG email
    single_leg_email = {
        'subject': 'Travel Inquiry – 4 adults to Bali',
        'body': '''Hi Team,

Hope you're doing well. A client is planning a 7 nights / 8 days trip to Bali for 4 travelers (including 4 adults) departing from Mumbai between 18 July and 25 July. Preferred hotel is water villa with all meals. They would like to include Kintamani sunrise, Ubud tour, and Tanah Lot temple. Flights are not required. Special request: wheelchair access. Budget is around ₹60000 per person. Kindly send 2 package options ASAP.

Regards,
Mark Henry''',
        'sender': 'mark.henry@example.com'
    }
    
    # User's MULTI_LEG email
    multi_leg_email = {
        'subject': 'Travel Plans for 7 Pax – Singapore & Goa (8 Days)',
        'body': '''Hello Team,

We are a group of 7 (including 6 adults and 1 children) planning a 8-day trip from 02 October to 09 October, departing from Chennai.
For Singapore, we'd like 3 nights in a 5-star hotel with veg meals. Transportation: private car. Activities: Gardens by the Bay and Sentosa tour.
For Goa, we'd like 3 nights in a 3-star hotel with veg meals. Transportation: hotel shuttle. Activities: beach hopping and Dudhsagar Falls.

Also, airport pickups/drop-offs and visa assistance where needed. Flights are not required. Our budget is approx ₹50000 per person. Could you share two quotes—one with Indian-style dinners and one standard? by EOD.

Regards,
Chloe Sanford''',
        'sender': 'chloe.sanford@example.com'
    }
    
    print("="*80)
    print("TESTING USER PROVIDED EMAILS")
    print("="*80)
    
    # Test SINGLE_LEG email
    print("\n" + "="*50)
    print("TESTING SINGLE_LEG EMAIL (Should be SINGLE_LEG)")
    print("="*50)
    result1 = processor.process_inquiry(single_leg_email)
    
    print(f"Classified as: {result1.get('inquiry_type', {}).get('type')}")
    print(f"Confidence: {result1.get('inquiry_type', {}).get('confidence')}")
    print(f"Start Date: {result1.get('date_details', {}).get('start_date')}")
    print(f"End Date: {result1.get('date_details', {}).get('end_date')}")
    print(f"Duration: {result1.get('date_details', {}).get('duration')}")
    print(f"Adults: {result1.get('traveler_details', {}).get('adults')}")
    print(f"Children: {result1.get('traveler_details', {}).get('children')}")
    print(f"Hotel Type: {result1.get('preference_details', {}).get('hotel')}")
    print(f"Meal Plan: {result1.get('preference_details', {}).get('meals')}")
    print(f"Flight Required: {result1.get('preference_details', {}).get('flight_required')}")
    print(f"Deadline: {result1.get('deadline')}")
    print(f"Departure City: {result1.get('location_details', {}).get('departure_city')}")
    
    # Test MULTI_LEG email
    print("\n" + "="*50) 
    print("TESTING MULTI_LEG EMAIL (Should be MULTI_LEG)")
    print("="*50)
    result2 = processor.process_inquiry(multi_leg_email)
    
    print(f"Classified as: {result2.get('inquiry_type', {}).get('type')}")
    print(f"Confidence: {result2.get('inquiry_type', {}).get('confidence')}")
    print(f"Start Date: {result2.get('date_details', {}).get('start_date')}")
    print(f"End Date: {result2.get('date_details', {}).get('end_date')}")
    print(f"Duration: {result2.get('date_details', {}).get('duration')}")
    print(f"Adults: {result2.get('traveler_details', {}).get('adults')}")
    print(f"Children: {result2.get('traveler_details', {}).get('children')}")
    print(f"Hotel Type: {result2.get('preference_details', {}).get('hotel')}")
    print(f"Meal Plan: {result2.get('preference_details', {}).get('meals')}")
    print(f"Flight Required: {result2.get('preference_details', {}).get('flight_required')}")
    print(f"Deadline: {result2.get('deadline')}")
    print(f"Departure City: {result2.get('location_details', {}).get('departure_city')}")
    
    # Generate Excel reports
    excel1 = processor.excel_generator.generate_inquiry_report(result1)
    excel2 = processor.excel_generator.generate_inquiry_report(result2)
    
    print(f"\nExcel reports generated:")
    print(f"Single-leg: {excel1}")
    print(f"Multi-leg: {excel2}")

if __name__ == "__main__":
    test_user_emails()