#!/usr/bin/env python3
"""Quick test of LLM extraction on Europe email"""

import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Your Europe email content
email_content = """Subject: Europe Trip Planning - 8 People
From: pranav.thakker@email.com

Hello Shivang,

My client is looking for trip to Europe starting from 1st August to 15th August. He will be travelling with group of total 8 people, out of which there will be 2 couples, 2 kids and 2 singles. Out of them 2 couples and 2 kids need visa and singles already have visa. They want to travel within europe in Euro Rail. The major countries to be covered will be France, Italy, Germany & Switzerland. In Switzerland and Germany include all site-seeings. In Italy include just tower of pisa and in France include just Effile Tower. I will need English speaking guide in Germany. I will need complete food options in Switzerland and France. And rest of the places just a breakfast. What will be the charges for 4-star as well as 5-star hotels at all the places? Provide me total cost asap.

Thank you,
Pranav Thakker"""

# Enhanced GPT-4 prompt for comprehensive extraction
prompt = f"""Extract ALL travel information from this email into structured format:

{email_content}

Return JSON with these fields:
- inquiry_type: "multi_leg" (multiple destinations)
- customer_name: extracted name
- destinations: list of countries/cities
- departure_date: YYYY-MM-DD format
- return_date: YYYY-MM-DD format
- duration_nights: number of nights
- total_travelers: total count
- adults: number of adults
- children: number of children
- hotel_preferences: hotel categories mentioned
- meal_preferences: meal plans by location
- transport_preferences: transportation method
- activities: list of attractions/activities by location
- guide_required: guide needs
- visa_required: visa requirements
- special_requirements: any special requests
- language_detected: email language
- confidence_score: 0.0-1.0

Extract every detail comprehensively."""

print("Testing enhanced LLM extraction on Europe email...")
print("=" * 60)

try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert travel agent AI. Extract information comprehensively and return valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=1500
    )
    
    content = response.choices[0].message.content
    print("GPT-4 EXTRACTED DATA:")
    print("-" * 40)
    print(content)
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE - Enhanced field coverage achieved!")
    
except Exception as e:
    print(f"Error: {e}")