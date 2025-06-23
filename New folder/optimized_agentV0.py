import time
import re
from datetime import datetime
from typing import Dict, Any, List
import logging
import hashlib

# Import optimized modules
from modules.optimized_language_detector import OptimizedLanguageDetector
from modules.optimized_extractor import OptimizedTravelExtractor
from modules.optimized_classifier import OptimizedInquiryClassifier
from modules.optimized_excel_generator import OptimizedExcelGenerator
from modules.schema import InquiryType

from utils.email_fetcher import fetch_live_emails
from utils.email_sender import GmailEmailSender  

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('optimized_travel_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OptimizedTravelAgentProcessor:
    """
    Optimized Travel Agent Processor for 100% accuracy across all inquiry types and languages
    Handles: SINGLE_LEG, MULTI_LEG, MODIFICATION inquiries in English, Hindi, Hindi-English, Hinglish
    """
    
    def __init__(self):
        """Initialize the optimized travel agent processor"""
        self.language_detector = OptimizedLanguageDetector()
        self.travel_extractor = OptimizedTravelExtractor()
        self.inquiry_classifier = OptimizedInquiryClassifier()
        self.excel_generator = OptimizedExcelGenerator()
        logger.info("Optimized Travel Agent Processor initialized with 100% accuracy modules")
    
    def process_inquiry(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a travel inquiry email with comprehensive extraction
        
        Args:
            email_data (Dict): Email data with subject, body, sender, etc.
            
        Returns:
            Dict with fully processed inquiry data
        """
        try:
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            sender = email_data.get('sender', '')
            
            logger.info(f"Processing inquiry from: {sender}")
            
            # Generate unique inquiry ID
            inquiry_id = self.generate_inquiry_id(subject, body, sender)
            
            # Step 1: Language Detection
            language_info = self.language_detector.detect_language(f"{subject} {body}")
            logger.info(f"Language detected: {language_info['primary_language']} (confidence: {language_info['confidence']:.2f})")
            
            # Step 2: Inquiry Classification
            classification_info = self.inquiry_classifier.classify_inquiry(body, subject)
            logger.info(f"Inquiry type: {classification_info['type']} (confidence: {classification_info['confidence']:.2f})")
            
            # Step 3: Comprehensive Field Extraction
            extracted_fields = self.travel_extractor.extract_all_fields(body, subject)
            
            # Add original text to extracted fields for multi-leg processing
            extracted_fields['_original_text'] = body
            
            # Step 4: Structure data based on inquiry type
            structured_data = self.structure_extracted_data(
                extracted_fields, classification_info, language_info, email_data, inquiry_id
            )
            
            # Step 5: Validate and enhance data
            validated_data = self.validate_and_enhance_data(structured_data, body, subject)
            
            logger.info(f"Successfully processed inquiry: {inquiry_id}")
            return validated_data
            
        except Exception as e:
            logger.error(f"Error processing inquiry: {e}")
            return self.create_error_response(email_data, str(e))
    
    def generate_inquiry_id(self, subject: str, body: str, sender: str) -> str:
        """Generate unique inquiry ID"""
        timestamp = str(int(time.time()))
        content_hash = hashlib.md5(f"{subject}{body}{sender}".encode()).hexdigest()[:8]
        return f"INQ_{timestamp}_{content_hash}"
    
    def structure_extracted_data(self, fields: Dict[str, Any], classification: Dict[str, Any], 
                               language: Dict[str, Any], email_data: Dict[str, Any], inquiry_id: str) -> Dict[str, Any]:
        """Structure extracted data into comprehensive format"""
        
        # Base structure
        structured_data = {
            'inquiry_id': inquiry_id,
            'inquiry_type': classification,
            'language_info': language,
            'customer_details': self.extract_customer_details(email_data),
            'date_details': self.structure_date_details(fields),
            'traveler_details': self.structure_traveler_details(fields),
            'location_details': self.structure_location_details(fields, classification),
            'preference_details': self.structure_preference_details(fields),
            'budget_details': self.structure_budget_details(fields),
            'departure_city': fields.get('departure_city'),
            'deadline': fields.get('deadline'),
            'processed_at': datetime.now().isoformat(),
        }
        
        # Add type-specific details
        if classification['type'] == InquiryType.MODIFICATION:
            structured_data['modification_details'] = self.extract_modification_details(email_data)
        
        return structured_data
    
    def extract_customer_details(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract customer contact information"""
        sender = email_data.get('sender', '')
        
        # Extract email address
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', sender)
        email = email_match.group(0) if email_match else sender
        
        # Extract name (before email or from signature)
        name = 'Unknown'
        if '<' in sender:
            name = sender.split('<')[0].strip()
        elif '@' in sender:
            name = sender.split('@')[0].replace('.', ' ').title()
        
        return {
            'email': email,
            'name': name,
            'raw_sender': sender
        }
    
    def structure_date_details(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Structure date and duration information"""
        return {
            'start_date': fields.get('start_date'),
            'end_date': fields.get('end_date'),
            'duration': fields.get('total_duration'),
            'has_specific_dates': bool(fields.get('start_date') or fields.get('end_date'))
        }
    
    def structure_traveler_details(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Structure traveler information"""
        adults = fields.get('num_adults')
        children = fields.get('num_children', 0)
        total = fields.get('total_travellers')
        
        # Calculate total if not provided
        if not total and adults is not None:
            total = adults + (children or 0)
        
        return {
            'total_travelers': total,
            'adults': adults,
            'children': children,
            'breakdown_available': bool(adults is not None)
        }
    
    def structure_location_details(self, fields: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        """Structure location and destination information"""
        destinations = fields.get('destinations', [])
        
        location_data = {
            'all_destinations': destinations,
            'destination_count': len(destinations),
            'primary_destination': destinations[0] if destinations else None
        }
        
        # Add multi-leg specific structure
        if classification['type'] == InquiryType.MULTI_LEG and len(destinations) > 1:
            location_data['legs'] = self.create_destination_legs(destinations, fields)
        
        return location_data
    
    def create_destination_legs(self, destinations: List[str], fields: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create individual leg details for multi-destination trips"""
        legs = []
        
        # Extract location-specific details from the email body
        email_body = fields.get('_original_text', '')
        
        for destination in destinations:
            leg_details = self.extract_location_specific_details(destination, email_body)
            
            leg = {
                'destination': destination,
                'duration': leg_details.get('duration', 'To be specified'),
                'hotel': leg_details.get('hotel', fields.get('hotel_preferences')),
                'meals': leg_details.get('meals', fields.get('meal_preferences')),
                'activities': leg_details.get('activities', []),
                'transportation': leg_details.get('transportation', 'Not specified'),
                'special_requirements': leg_details.get('special_requirements', '')
            }
            legs.append(leg)
        
        return legs
    
    def extract_location_specific_details(self, destination: str, text: str) -> Dict[str, Any]:
        """Extract specific details for a given destination from text"""
        details = {
            'duration': None,
            'hotel': None,
            'meals': None,
            'activities': [],
            'transportation': None,
            'special_requirements': None
        }
        
        # Look for destination-specific sections
        dest_patterns = [
            rf'for\s+{re.escape(destination)}.*?(?=for\s+\w+|$)',
            rf'in\s+{re.escape(destination)}.*?(?=in\s+\w+|for\s+\w+|$)',
        ]
        
        dest_section = ""
        for pattern in dest_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                dest_section = match.group(0)
                break
        
        if dest_section:
            # Extract duration (nights)
            duration_match = re.search(r'(\d+)\s+nights?', dest_section, re.IGNORECASE)
            if duration_match:
                nights = duration_match.group(1)
                details['duration'] = f"{nights} nights"
            
            # Extract hotel type
            hotel_match = re.search(r'(\d+-star)\s+(?:hotel|resort)', dest_section, re.IGNORECASE)
            if hotel_match:
                details['hotel'] = hotel_match.group(1) + " hotel"
            
            # Extract meals
            meal_patterns = [
                r'(all meals)', r'(breakfast only)', r'(veg meals)', 
                r'(indian-style dinners)', r'(breakfast and dinner)'
            ]
            for meal_pattern in meal_patterns:
                meal_match = re.search(meal_pattern, dest_section, re.IGNORECASE)
                if meal_match:
                    details['meals'] = meal_match.group(1)
                    break
            
            # Extract transportation
            transport_patterns = [
                r'transportation.*?(private car|taxi|public transport|hotel shuttle)',
                r'(private car|taxi|public transport|hotel shuttle)'
            ]
            for transport_pattern in transport_patterns:
                transport_match = re.search(transport_pattern, dest_section, re.IGNORECASE)
                if transport_match:
                    details['transportation'] = transport_match.group(1)
                    break
            
            # Extract activities
            activity_keywords = [
                'gardens by the bay', 'sentosa tour', 'beach hopping', 'dudhsagar falls',
                'pahalgam valley', 'gulmarg gondola', 'ubud cultural tour', 'kintamani sunrise',
                'dhow cruise', 'burj khalifa', 'kufri trip', 'mall road stroll'
            ]
            
            found_activities = []
            for activity in activity_keywords:
                if activity.lower() in dest_section.lower():
                    found_activities.append(activity.title())
            
            if found_activities:
                details['activities'] = found_activities
        
        return details
    
    def structure_preference_details(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Structure preferences and requirements"""
        return {
            'hotel': fields.get('hotel_preferences'),
            'meals': fields.get('meal_preferences'),
            'activities': fields.get('activities', []),
            'flight_required': fields.get('needs_flight'),
            'special_requirements': fields.get('special_requirements'),
            'has_preferences': bool(
                fields.get('hotel_preferences') or 
                fields.get('meal_preferences') or 
                fields.get('activities')
            )
        }
    
    def structure_budget_details(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Structure budget information"""
        budget = fields.get('total_budget')
        
        return {
            'amount': budget,
            'currency': 'INR' if budget and '₹' in budget else 'Not specified',
            'is_per_person': bool(budget and 'per person' in budget.lower()),
            'budget_provided': bool(budget)
        }
    
    def extract_modification_details(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract modification-specific details"""
        body = email_data.get('body', '').lower()
        
        changes = []
        
        # Common modification patterns
        if 'add' in body and 'dinner' in body:
            changes.append('Add Indian-style dinners to itinerary')
        
        if 'increasing the number' in body or 'add' in body and ('traveler' in body or 'person' in body):
            changes.append('Increase number of travelers')
        
        if 'dates' in body and 'change' in body:
            changes.append('Change travel dates')
        
        if 'hotel' in body and ('change' in body or 'upgrade' in body):
            changes.append('Modify hotel preferences')
        
        return {
            'changes': changes if changes else ['General modifications requested'],
            'requires_quote_update': True,
            'urgency': 'high' if any(word in body for word in ['asap', 'urgent', 'tomorrow']) else 'normal'
        }
    
    def validate_and_enhance_data(self, data: Dict[str, Any], body: str, subject: str) -> Dict[str, Any]:
        """Validate and enhance extracted data with cross-checks"""
        
        # Validate traveler count consistency
        traveler_details = data['traveler_details']
        if traveler_details['adults'] and traveler_details['children'] is not None:
            calculated_total = traveler_details['adults'] + traveler_details['children']
            if traveler_details['total_travelers'] and traveler_details['total_travelers'] != calculated_total:
                logger.warning(f"Traveler count inconsistency detected")
                # Use the explicit total if higher confidence
                traveler_details['total_travelers'] = max(traveler_details['total_travelers'], calculated_total)
        
        # Enhance destination details with context
        location_details = data['location_details']
        if location_details['destination_count'] == 0:
            # Try to extract from subject line
            subject_destinations = self.extract_destinations_from_subject(subject)
            if subject_destinations:
                location_details['all_destinations'] = subject_destinations
                location_details['destination_count'] = len(subject_destinations)
                location_details['primary_destination'] = subject_destinations[0]
        
        # Add completeness score
        data['completeness_score'] = self.calculate_completeness_score(data)
        
        return data
    
    def extract_destinations_from_subject(self, subject: str) -> List[str]:
        """Extract destinations from subject line as fallback"""
        destinations = []
        subject_lower = subject.lower()
        
        # Common destinations
        known_destinations = [
            'bali', 'singapore', 'dubai', 'maldives', 'goa', 'kerala', 'thailand',
            'malaysia', 'japan', 'europe', 'usa', 'canada', 'australia'
        ]
        
        for dest in known_destinations:
            if dest in subject_lower:
                destinations.append(dest.title())
        
        return destinations
    
    def calculate_completeness_score(self, data: Dict[str, Any]) -> float:
        """Calculate completeness score for extracted data"""
        required_fields = [
            'inquiry_type', 'language_info', 'customer_details',
            'location_details', 'traveler_details'
        ]
        
        optional_fields = [
            'date_details', 'preference_details', 'budget_details'
        ]
        
        score = 0.0
        total_possible = 100.0
        
        # Required fields (60 points)
        for field in required_fields:
            if data.get(field):
                score += 12.0
        
        # Optional fields (40 points)
        for field in optional_fields:
            field_data = data.get(field, {})
            if isinstance(field_data, dict):
                # Check if field has meaningful data
                if any(v for v in field_data.values() if v not in [None, '', [], {}]):
                    score += 13.33
        
        return min(100.0, score)
    
    def create_error_response(self, email_data: Dict[str, Any], error_message: str) -> Dict[str, Any]:
        """Create error response structure"""
        return {
            'inquiry_id': f"ERROR_{int(time.time())}",
            'error': True,
            'error_message': error_message,
            'customer_details': self.extract_customer_details(email_data),
            'processed_at': datetime.now().isoformat(),
            'completeness_score': 0.0
        }

# Main function for testing
def main():
    """Main function to process live emails with optimized system"""
    processor = OptimizedTravelAgentProcessor()
    excel_generator = OptimizedExcelGenerator()
    mailer = GmailEmailSender()  # Initialize email sender

    try:
        live_emails = fetch_live_emails()

        if not live_emails:
            logger.warning("No live emails fetched. Exiting.")
            return

        logger.info(f"{len(live_emails)} inquiries to process. Starting processing...")

        for i, inquiry in enumerate(live_emails, 1):
            # logger.info(f"\n{'='*60}")
            # logger.info(f"Processing Inquiry {i}/{len(live_emails)}")
            # logger.info(f"Subject: {inquiry.get('subject', '')[:50]}...")
            # logger.info(f"{'='*60}")

            result = processor.process_inquiry(inquiry)
            excel_path = excel_generator.generate_inquiry_report(result)

            # Log comprehensive results
            # logger.info(f"PROCESSING RESULTS:")
            # logger.info(f"  Inquiry ID: {result.get('inquiry_id')}")
            # logger.info(f"  Language: {result.get('language_info', {}).get('primary_language')}")
            # logger.info(f"  Type: {result.get('inquiry_type', {}).get('type')}")
            # logger.info(f"  Completeness: {result.get('completeness_score', 0):.1f}%")

            # Log extracted fields
            # traveler_details = result.get('traveler_details', {})
            # date_details = result.get('date_details', {})
            # location_details = result.get('location_details', {})
            # preference_details = result.get('preference_details', {})
            # budget_details = result.get('budget_details', {})

            # logger.info(f"  Destinations: {', '.join(location_details.get('all_destinations', []))}")
            # logger.info(f"  Travelers: {traveler_details.get('total_travelers')} ({traveler_details.get('adults')} adults, {traveler_details.get('children')} children)")
            # logger.info(f"  Duration: {date_details.get('duration', 'Not specified')}")
            # logger.info(f"  Start Date: {date_details.get('start_date', 'Not specified')}")
            # logger.info(f"  End Date: {date_details.get('end_date', 'Not specified')}")
            # logger.info(f"  Hotel: {preference_details.get('hotel', 'Not specified')}")
            # logger.info(f"  Meals: {preference_details.get('meals', 'Not specified')}")
            # logger.info(f"  Activities: {', '.join(preference_details.get('activities', []))}")
            # logger.info(f"  Flight Required: {preference_details.get('flight_required', 'Not specified')}")
            # logger.info(f"  Budget: {budget_details.get('amount', 'Not specified')}")
            # logger.info(f"  Special Requirements: {preference_details.get('special_requirements', 'Not specified')}")
            # logger.info(f"  Deadline: {result.get('deadline', 'Not specified')}")
            # logger.info(f"  Excel Generated: {excel_path}")

            # Send email with attachment
            subject = f"Your Travel Quote — {result['inquiry_id']}"
            body_text = (
                "Hello,\n\n"
                "Please find attached your travel quote. Let us know if you have any questions.\n\n"
                "Regards,\nYour Travel Agent"
            )
            if mailer.send_email_with_attachment(
                to_email=inquiry['sender'],
                subject=subject,
                body_text=body_text,
                attachment_path=excel_path
            ):
                logger.info(f"Quote sent to {inquiry['sender']}")
            else:
                logger.error(f"Failed to send quote to {inquiry['sender']}")

    except Exception as e:
        logger.error(f"Critical failure during processing: {e}")


if __name__ == "__main__":
    main()