#!/usr/bin/env python3
"""
Test script to demonstrate enhanced LLM extraction on Europe email
"""

import sys
import os
sys.path.append('.')

from modules.llm_travel_agent import LLMTravelAgent
import json

def test_europe_email():
    """Test enhanced extraction on the complex Europe email"""
    
    # Initialize LLM agent
    agent = LLMTravelAgent()
    
    # Your actual Europe email content
    email_data = {
        'subject': 'Europe Trip Planning - 8 People',
        'body': """Hello Shivang,

My client is looking for trip to Europe starting from 1st August to 15th August. He will be travelling with group of total 8 people, out of which there will be 2 couples, 2 kids and 2 singles. Out of them 2 couples and 2 kids need visa and singles already have visa. They want to travel within europe in Euro Rail. The major countries to be covered will be France, Italy, Germany & Switzerland. In Switzerland and Germany include all site-seeings. In Italy include just tower of pisa and in France include just Effile Tower. I will need English speaking guide in Germany. I will need complete food options in Switzerland and France. And rest of the places just a breakfast. What will be the charges for 4-star as well as 5-star hotels at all the places? Provide me total cost asap.

Thank you,
Pranav Thakker""",
        'sender': 'pranav.thakker@email.com'
    }
    
    print("=" * 60)
    print("TESTING ENHANCED LLM EXTRACTION ON EUROPE EMAIL")
    print("=" * 60)
    
    # Process the email
    result = agent.process_inquiry(email_data)
    
    print("\nEXTRACTED FIELDS:")
    print("-" * 40)
    
    # Display key extracted information
    key_fields = [
        'inquiry_type', 'destinations', 'departure_date', 'return_date',
        'total_travelers', 'adults', 'children', 'hotel_preferences',
        'meal_preferences', 'transport_preferences', 'activities',
        'visa_required', 'guide_required', 'special_requirements',
        'language_detected', 'confidence_score'
    ]
    
    for field in key_fields:
        value = result.get(field, 'Not extracted')
        print(f"{field:20}: {value}")
    
    print("\n" + "=" * 60)
    print("FIELD EXTRACTION ANALYSIS:")
    print("=" * 60)
    
    # Analyze what was captured vs original email
    analysis = {
        'Destinations': f"✓ Extracted: {result.get('destinations', [])}",
        'Travel Dates': f"✓ Extracted: {result.get('departure_date')} to {result.get('return_date')}",
        'Travelers': f"✓ Total: {result.get('total_travelers')}, Adults: {result.get('adults')}, Children: {result.get('children')}",
        'Hotel Preferences': f"✓ Extracted: {result.get('hotel_preferences')}",
        'Meal Preferences': f"✓ Extracted: {result.get('meal_preferences')}",
        'Transportation': f"✓ Extracted: {result.get('transport_preferences')}",
        'Activities': f"✓ Extracted: {len(result.get('activities', []))} activities",
        'Guide Requirements': f"✓ Extracted: {result.get('guide_required')}",
        'Visa Requirements': f"✓ Extracted: {result.get('visa_required')}",
        'Confidence Score': f"✓ {result.get('confidence_score', 0)*100:.1f}%"
    }
    
    for key, value in analysis.items():
        print(f"{key:20}: {value}")
    
    return result

if __name__ == "__main__":
    test_europe_email()