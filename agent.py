import time
import re
from datetime import datetime
from typing import Dict, Any, List
import logging
from modules.optimized_language_detector import OptimizedLanguageDetector
from modules.optimized_extractor import OptimizedTravelExtractor
from modules.optimized_classifier import OptimizedInquiryClassifier
from modules.optimized_excel_generator import OptimizedExcelGenerator
from utils.email_fetcher import fetch_live_emails
from utils.email_sender import GmailEmailSender


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




def main():
    processor = TravelAgentProcessor()
    excel_generator = ExcelGenerator()
    mailer = GmailEmailSender()

    try:
        live_emails = fetch_live_emails()
        if not live_emails:
            logger.warning("No live emails fetched. Exiting.")
            return

        logger.info(f"{len(live_emails)} live emails fetched. Starting processing...")

        for idx, inquiry in enumerate(live_emails, start=1):
            # 1) Process
            result = processor.process_inquiry(inquiry)
            # 2) Make ID unique
            result['inquiry_id'] = f"{result['inquiry_id']}_{idx}"
            # 3) Generate Excel
            excel_path = excel_generator.generate_inquiry_report(result)
            logger.info(f"Excel generated: {excel_path}")

            # 4) Send back the quote
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