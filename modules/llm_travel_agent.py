"""
Complete LLM-based Travel Agent using OpenAI GPT-4
Processes any travel inquiry with dynamic extraction and classification
"""

import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, ValidationError, Field
import openai
import os

# Setup logging
logger = logging.getLogger(__name__)

class TravelInquiry(BaseModel):
    """Complete travel inquiry model for any type of travel request"""
    # Basic inquiry info
    inquiry_id: str = Field(..., description="Unique inquiry identifier")
    inquiry_type: str = Field(..., description="Type: single_leg, multi_leg, or modification")
    
    # Customer details
    customer_name: Optional[str] = Field(None, description="Customer name")
    customer_email: str = Field(..., description="Customer email address")
    
    # Trip basics
    destinations: List[str] = Field(default_factory=list, description="All destinations to visit")
    departure_city: Optional[str] = Field(None, description="City of departure")
    departure_date: Optional[str] = Field(None, description="Departure date (YYYY-MM-DD)")
    return_date: Optional[str] = Field(None, description="Return date (YYYY-MM-DD)")
    duration_nights: Optional[int] = Field(None, description="Trip duration in nights")
    
    # Travelers
    total_travelers: Optional[int] = Field(None, description="Total number of travelers")
    adults: Optional[int] = Field(None, description="Number of adult travelers")
    children: Optional[int] = Field(None, description="Number of child travelers")
    infants: Optional[int] = Field(None, description="Number of infant travelers")
    
    # Preferences and requirements
    budget_amount: Optional[float] = Field(None, description="Budget amount")
    budget_currency: Optional[str] = Field(None, description="Budget currency (INR, USD, EUR)")
    hotel_preferences: Optional[str] = Field(None, description="Hotel category/preferences")
    meal_preferences: Optional[str] = Field(None, description="Meal plan preferences")
    transport_preferences: Optional[str] = Field(None, description="Transportation preferences")
    activities: List[str] = Field(default_factory=list, description="Desired activities and tours")
    special_requirements: Optional[str] = Field(None, description="Special requests or requirements")
    
    # Logistics
    visa_required: Optional[bool] = Field(None, description="Whether visa assistance is needed")
    flight_required: Optional[bool] = Field(None, description="Whether flight booking is required")
    guide_required: Optional[str] = Field(None, description="Guide requirements (language, type)")
    
    # Processing metadata
    language_detected: Optional[str] = Field(None, description="Primary language of inquiry")
    confidence_score: Optional[float] = Field(None, description="Extraction confidence (0-1)")
    processing_notes: Optional[str] = Field(None, description="Additional processing notes")

class LLMTravelAgent:
    """Complete LLM-based travel agent for processing any travel inquiry"""
    
    def __init__(self):
        """Initialize the LLM travel agent"""
        self.client = self._setup_openai_client()
        logger.info("LLM Travel Agent initialized successfully")
    
    def _setup_openai_client(self):
        """Setup OpenAI client with API key"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        return openai.OpenAI(api_key=api_key)
    
    def process_inquiry(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process any travel inquiry using GPT-4
        
        Args:
            email_data: Dict with subject, body, sender, etc.
            
        Returns:
            Dict with complete processed inquiry data
        """
        try:
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            sender = email_data.get('sender', '')
            
            # Generate unique inquiry ID
            inquiry_id = self._generate_inquiry_id(subject, body, sender)
            logger.info(f"Processing inquiry {inquiry_id} from {sender}")
            
            # Extract all information using GPT-4
            extracted_data = self._extract_with_gpt4(subject, body, sender, inquiry_id)
            
            # Validate and structure the data
            structured_data = self._validate_and_structure(extracted_data)
            
            logger.info(f"Successfully processed inquiry {inquiry_id}")
            return structured_data
            
        except Exception as e:
            logger.error(f"Error processing inquiry: {e}")
            return self._create_error_response(email_data, str(e))
    
    def _extract_with_gpt4(self, subject: str, body: str, sender: str, inquiry_id: str) -> Dict[str, Any]:
        """Extract comprehensive travel information using GPT-4"""
        
        prompt = f"""
You are an expert travel agent AI. Extract ALL travel information from this email into a structured JSON format.

Email Subject: {subject}
Email Body: {body}
From: {sender}

Return ONLY a valid JSON object with these EXACT field names:

{{
    "inquiry_type": "single_leg",
    "customer_name": null,
    "destinations": [],
    "departure_city": null,
    "departure_date": null,
    "return_date": null,
    "duration_nights": null,
    "total_travelers": null,
    "adults": null,
    "children": null,
    "infants": null,
    "budget_amount": null,
    "budget_currency": null,
    "hotel_preferences": null,
    "meal_preferences": null,
    "transport_preferences": null,
    "activities": [],
    "special_requirements": null,
    "visa_required": null,
    "flight_required": null,
    "guide_required": null,
    "language_detected": "english",
    "confidence_score": 0.8,
    "processing_notes": null
}}

EXTRACTION INSTRUCTIONS:
1. inquiry_type: "single_leg" (one destination), "multi_leg" (multiple cities), or "modification"
2. Extract customer name from signature or content
3. List ALL destinations/cities mentioned
4. Find departure city if specified
5. Extract dates in YYYY-MM-DD format
6. Count travelers: total, adults, children, infants
7. Find budget amount and currency (INR/USD/EUR)
8. Extract hotel preferences (star rating, type)
9. Extract meal preferences (breakfast/full board/etc)
10. Note transport needs (flights/trains/car)
11. List activities, tours, attractions mentioned
12. Note special requirements, dietary needs
13. Determine if visa/flight assistance needed
14. Detect language: english/hindi/hinglish
15. Set confidence 0.0-1.0 based on data completeness

Replace null values with extracted information. Keep empty arrays [] if no data found.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional travel industry expert with extensive experience in processing travel inquiries. Extract information comprehensively and accurately."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON from the response
            try:
                if content and '```json' in content:
                    json_str = content.split('```json')[1].split('```')[0].strip()
                elif content:
                    json_str = content.strip()
                else:
                    raise ValueError("Empty response from GPT-4")
                
                extracted_data = json.loads(json_str)
                extracted_data['inquiry_id'] = inquiry_id
                extracted_data['customer_email'] = sender
                
                return extracted_data
                
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON from GPT-4 response")
                return {"inquiry_id": inquiry_id, "customer_email": sender, "error": "Failed to parse GPT response"}
                
        except Exception as e:
            logger.error(f"GPT-4 extraction failed: {e}")
            return {"inquiry_id": inquiry_id, "customer_email": sender, "error": str(e)}
    
    def _validate_and_structure(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted data and create structured output"""
        try:
            # Clean and normalize the data
            cleaned_data = self._clean_extracted_data(extracted_data)
            
            # Create TravelInquiry model for validation
            inquiry = TravelInquiry(**cleaned_data)
            validated_data = inquiry.model_dump()
            
            # Calculate confidence score
            confidence = self._calculate_confidence(validated_data)
            validated_data['confidence_score'] = confidence
            
            # Add processing metadata
            validated_data['processed_at'] = datetime.now().isoformat()
            validated_data['processing_method'] = 'llm_only'
            
            return validated_data
            
        except ValidationError as e:
            logger.error(f"Validation failed: {e}")
            # Return partial data with errors noted
            return {
                **extracted_data,
                'validation_errors': str(e),
                'confidence_score': 0.3,
                'processed_at': datetime.now().isoformat(),
                'processing_method': 'llm_partial'
            }
    
    def _clean_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize extracted data"""
        cleaned = {}
        
        # Map common field variations to standard names
        field_mapping = {
            'destination': 'destinations',
            'total_travellers': 'total_travelers',
            'number_of_travelers': 'total_travelers',
            'start_date': 'departure_date',
            'end_date': 'return_date',
            'budget': 'budget_amount',
            'hotel_category': 'hotel_preferences',
            'meals': 'meal_preferences',
            'transport': 'transport_preferences',
            'special_requests': 'special_requirements',
            'inquiry_classification': 'inquiry_type',
            'trip_type': 'inquiry_type',
            'type': 'inquiry_type'
        }
        
        for key, value in data.items():
            # Map field names
            mapped_key = field_mapping.get(key, key)
            
            # Clean values
            if isinstance(value, str):
                value = value.strip()
                if value.lower() in ['null', 'none', 'n/a', '']:
                    value = None
            elif isinstance(value, list) and len(value) == 0:
                value = None
            
            # Handle specific field type requirements
            if mapped_key == 'destinations':
                if isinstance(value, str):
                    cleaned[mapped_key] = [dest.strip() for dest in value.split(',') if dest.strip()]
                elif isinstance(value, list):
                    cleaned[mapped_key] = [str(item) for item in value if item]
                elif value is None:
                    cleaned[mapped_key] = []
                else:
                    cleaned[mapped_key] = []
            elif mapped_key == 'activities':
                if isinstance(value, str):
                    cleaned[mapped_key] = [act.strip() for act in value.split(',') if act.strip()]
                elif isinstance(value, list):
                    cleaned[mapped_key] = [str(item) for item in value if item]
                elif value is None:
                    cleaned[mapped_key] = []
                else:
                    cleaned[mapped_key] = []
            elif mapped_key == 'guide_required':
                if isinstance(value, bool):
                    cleaned[mapped_key] = "Guide required" if value else None
                elif isinstance(value, str):
                    cleaned[mapped_key] = value
                else:
                    cleaned[mapped_key] = None
            elif mapped_key == 'hotel_preferences':
                if isinstance(value, list):
                    cleaned[mapped_key] = ', '.join(str(item) for item in value)
                elif isinstance(value, dict):
                    cleaned[mapped_key] = str(value)
                else:
                    cleaned[mapped_key] = value
            elif mapped_key == 'meal_preferences':
                if isinstance(value, dict):
                    cleaned[mapped_key] = str(value)
                elif isinstance(value, list):
                    cleaned[mapped_key] = ', '.join(str(item) for item in value)
                else:
                    cleaned[mapped_key] = value
            else:
                cleaned[mapped_key] = value
        
        # Handle complex activities data
        if 'activities' in cleaned and isinstance(cleaned['activities'], dict):
            # Convert location-based activities to a single list
            all_activities = []
            for location, acts in cleaned['activities'].items():
                if isinstance(acts, str):
                    all_activities.append(f"{location}: {acts}")
                elif isinstance(acts, list):
                    all_activities.extend([f"{location}: {act}" for act in acts])
            cleaned['activities'] = all_activities
        
        return cleaned
    
    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate processing confidence based on data completeness"""
        essential_fields = ['destinations', 'departure_date', 'total_travelers', 'customer_email']
        important_fields = ['return_date', 'budget_amount', 'hotel_preferences']
        optional_fields = ['activities', 'special_requirements', 'meal_preferences']
        
        essential_score = sum(1 for field in essential_fields if data.get(field)) / len(essential_fields)
        important_score = sum(1 for field in important_fields if data.get(field)) / len(important_fields)
        optional_score = sum(1 for field in optional_fields if data.get(field)) / len(optional_fields)
        
        return (essential_score * 0.6) + (important_score * 0.3) + (optional_score * 0.1)
    
    def _generate_inquiry_id(self, subject: str, body: str, sender: str) -> str:
        """Generate unique inquiry ID"""
        content = f"{subject}{body}{sender}{datetime.now().isoformat()}"
        hash_obj = hashlib.md5(content.encode())
        timestamp = int(datetime.now().timestamp())
        return f"INQ_{timestamp}_{hash_obj.hexdigest()[:8]}"
    
    def _create_error_response(self, email_data: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
        """Create error response structure"""
        return {
            'inquiry_id': f"ERROR_{int(datetime.now().timestamp())}",
            'customer_email': email_data.get('sender', 'unknown'),
            'error': error_msg,
            'confidence_score': 0.0,
            'processed_at': datetime.now().isoformat(),
            'processing_method': 'error'
        }