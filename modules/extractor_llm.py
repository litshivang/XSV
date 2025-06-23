"""
LLM-based Travel Inquiry Extractor using OpenAI GPT-4
Replaces rule-based extraction with dynamic structured extraction
"""

import json
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, ValidationError, Field
from datetime import datetime
import openai
import os

# Setup logging
logger = logging.getLogger(__name__)

class TripInquiry(BaseModel):
    """Pydantic model for structured trip inquiry validation"""
    destination: Optional[str] = Field(None, description="Primary destination or list of destinations")
    departure_city: Optional[str] = Field(None, description="City of departure")
    departure_date: Optional[str] = Field(None, description="Departure date in ISO format YYYY-MM-DD")
    return_date: Optional[str] = Field(None, description="Return date in ISO format YYYY-MM-DD")
    adults: Optional[int] = Field(None, description="Number of adult travelers", ge=0)
    children: Optional[int] = Field(None, description="Number of child travelers", ge=0)
    infants: Optional[int] = Field(None, description="Number of infant travelers", ge=0)
    budget: Optional[Dict[str, Any]] = Field(None, description="Budget with amount and currency")
    travel_class: Optional[str] = Field(None, description="Preferred flight class")
    hotel_preferences: Optional[str] = Field(None, description="Hotel or accommodation preferences")
    preferred_airlines: Optional[list] = Field(None, description="List of preferred airlines")
    special_requests: Optional[str] = Field(None, description="Special requests or requirements")
    notes: Optional[str] = Field(None, description="Additional notes or context")
    duration_nights: Optional[int] = Field(None, description="Trip duration in nights")
    meal_preferences: Optional[str] = Field(None, description="Meal plan preferences")
    activities: Optional[list] = Field(None, description="Desired activities or tours")

class LLMTravelExtractor:
    """LLM-based travel inquiry extractor using OpenAI GPT-4"""
    
    def __init__(self):
        """Initialize the LLM extractor"""
        self.client = None
        self.setup_openai_client()
        logger.info("LLM Travel Extractor initialized")
    
    def setup_openai_client(self):
        """Setup OpenAI client with API key"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
        else:
            logger.warning("OPENAI_API_KEY not found - LLM extraction disabled")
    
    def extract_trip_inquiry(self, email_text: str, email_subject: str = "") -> Dict[str, Any]:
        """
        Extract structured trip inquiry data from email text using GPT-4
        
        Args:
            email_text: Raw email content
            email_subject: Email subject line
            
        Returns:
            Dict containing extracted and validated trip inquiry data
        """
        if not self.client:
            logger.error("OpenAI client not available - falling back to empty extraction")
            return self._create_empty_extraction()
        
        try:
            # Prepare the extraction prompt
            prompt = self._prepare_extraction_prompt(email_text, email_subject)
            
            # Call GPT-4 with function calling
            response = self._call_gpt4_extraction(prompt)
            
            # Validate and structure the response
            validated_data = self._validate_extraction(response)
            
            logger.info("LLM extraction completed successfully")
            return validated_data
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return self._create_error_extraction(str(e))
    
    def _prepare_extraction_prompt(self, email_text: str, email_subject: str = "") -> str:
        """Prepare the prompt for GPT-4 extraction"""
        prompt = f"""
Extract structured travel inquiry information from the following customer email.

Email Subject: {email_subject}
Email Content:
{email_text}

Instructions:
1. Extract all travel-related information accurately
2. Convert dates to ISO format (YYYY-MM-DD)
3. Normalize numeric values (adults, children, infants)
4. Parse budget information with amount and currency
5. If information is missing or unclear, set to null
6. Handle multiple languages (English, Hindi, Hinglish)
7. Extract destinations as comma-separated string if multiple

Key fields to extract:
- destination: Primary travel destination(s)
- departure_city: City of departure
- departure_date: Trip start date (YYYY-MM-DD)
- return_date: Trip end date (YYYY-MM-DD)
- adults: Number of adult travelers
- children: Number of child travelers
- infants: Number of infant travelers
- budget: {{amount: number, currency: "INR/USD/etc"}}
- travel_class: Flight class preference
- hotel_preferences: Accommodation preferences
- special_requests: Any special requirements
- duration_nights: Trip duration in nights
- meal_preferences: Meal plan preferences
- activities: List of desired activities

Return valid JSON matching the expected schema.
"""
        return prompt
    
    def _call_gpt4_extraction(self, prompt: str) -> Dict[str, Any]:
        """Call GPT-4 with function calling for structured extraction"""
        
        function_schema = {
            "name": "extract_trip_inquiry",
            "description": "Extract structured travel inquiry data from customer email",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string", "description": "Primary destination or destinations"},
                    "departure_city": {"type": "string", "description": "City of departure"},
                    "departure_date": {"type": "string", "description": "Departure date in YYYY-MM-DD format"},
                    "return_date": {"type": "string", "description": "Return date in YYYY-MM-DD format"},
                    "adults": {"type": "integer", "description": "Number of adult travelers"},
                    "children": {"type": "integer", "description": "Number of child travelers"},
                    "infants": {"type": "integer", "description": "Number of infant travelers"},
                    "budget": {
                        "type": "object",
                        "properties": {
                            "amount": {"type": "number"},
                            "currency": {"type": "string"}
                        },
                        "description": "Budget information"
                    },
                    "travel_class": {"type": "string", "description": "Flight class preference"},
                    "hotel_preferences": {"type": "string", "description": "Hotel preferences"},
                    "preferred_airlines": {"type": "array", "items": {"type": "string"}},
                    "special_requests": {"type": "string", "description": "Special requests"},
                    "notes": {"type": "string", "description": "Additional notes"},
                    "duration_nights": {"type": "integer", "description": "Trip duration in nights"},
                    "meal_preferences": {"type": "string", "description": "Meal preferences"},
                    "activities": {"type": "array", "items": {"type": "string"}, "description": "Desired activities"}
                },
                "required": ["destination"]
            }
        }
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a travel industry expert extracting structured data from customer inquiries."},
                {"role": "user", "content": prompt}
            ],
            functions=[function_schema],
            function_call={"name": "extract_trip_inquiry"},
            temperature=0.1,
            max_tokens=1500
        )
        
        # Extract function call result
        function_call = response.choices[0].message.function_call
        if function_call and function_call.arguments:
            return json.loads(function_call.arguments)
        else:
            raise Exception("No function call result received from GPT-4")
    
    def _validate_extraction(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted data using Pydantic model"""
        try:
            # Validate with Pydantic
            inquiry = TripInquiry(**raw_data)
            validated_data = inquiry.model_dump(exclude_none=True)
            
            # Add confidence score based on completeness
            confidence = self._calculate_confidence(validated_data)
            validated_data['extraction_confidence'] = confidence
            validated_data['extraction_method'] = 'llm'
            validated_data['extracted_at'] = datetime.now().isoformat()
            
            return validated_data
            
        except ValidationError as e:
            logger.error(f"Validation failed: {e}")
            # Return partial data with errors logged
            return {
                'extraction_method': 'llm',
                'extraction_confidence': 0.3,
                'validation_errors': str(e),
                'partial_data': raw_data,
                'extracted_at': datetime.now().isoformat()
            }
    
    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate extraction confidence based on completeness"""
        required_fields = ['destination', 'departure_city', 'departure_date', 'adults']
        important_fields = ['return_date', 'budget', 'hotel_preferences']
        
        required_score = sum(1 for field in required_fields if data.get(field)) / len(required_fields)
        important_score = sum(1 for field in important_fields if data.get(field)) / len(important_fields)
        
        return (required_score * 0.7) + (important_score * 0.3)
    
    def _create_empty_extraction(self) -> Dict[str, Any]:
        """Create empty extraction result when LLM is unavailable"""
        return {
            'extraction_method': 'llm_unavailable',
            'extraction_confidence': 0.0,
            'error': 'OpenAI API not available',
            'extracted_at': datetime.now().isoformat()
        }
    
    def _create_error_extraction(self, error_msg: str) -> Dict[str, Any]:
        """Create error extraction result"""
        return {
            'extraction_method': 'llm_error',
            'extraction_confidence': 0.0,
            'error': error_msg,
            'extracted_at': datetime.now().isoformat()
        }

def translate_to_english(text: str, source_language: str = None) -> str:
    """
    Translate text to English if needed
    Placeholder for existing translation functionality
    """
    # This would integrate with existing translation utilities
    # For now, return as-is assuming translation happens elsewhere
    return text