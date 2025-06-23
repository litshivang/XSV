"""
Clean LLM-Only Travel Agent - Production System
Processes any travel inquiry using only OpenAI GPT-4 with optimized prompts
"""

import time
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Import LLM-only modules
from modules.llm_travel_agent import LLMTravelAgent
from modules.optimized_excel_generator import OptimizedExcelGenerator
from config.demo_config import get_demo_emails, is_demo_mode

# Import email utilities (only when not in demo mode)
try:
    from utils.email_fetcher import fetch_live_emails
    from utils.email_sender import GmailEmailSender
    EMAIL_UTILS_AVAILABLE = True
except ImportError:
    EMAIL_UTILS_AVAILABLE = False

def setup_logging():
    """Setup production-grade logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(
        log_dir / f"llm_travel_agent_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

class CleanLLMTravelAgent:
    """Clean LLM-only travel agent system"""
    
    def __init__(self):
        """Initialize the LLM-only travel agent system"""
        self.logger = setup_logging()
        self.processor = LLMTravelAgent()
        self.excel_generator = OptimizedExcelGenerator()
        
        # Initialize email sender only if not in demo mode
        self.demo_mode = is_demo_mode()
        if not self.demo_mode and EMAIL_UTILS_AVAILABLE:
            try:
                self.email_sender = GmailEmailSender()
                self.logger.info("Gmail integration initialized successfully")
            except Exception as e:
                self.logger.warning(f"Gmail initialization failed: {e}. Running in demo mode.")
                self.demo_mode = True
                self.email_sender = None
        else:
            self.email_sender = None
            self.logger.info("Running in demo mode - no Gmail integration")
        
        # Setup output directories
        self.setup_directories()
        
        mode_status = "demo mode" if self.demo_mode else "production mode"
        self.logger.info(f"Clean LLM Travel Agent initialized successfully in {mode_status}")
    
    def setup_directories(self):
        """Setup required directories"""
        directories = ["output", "logs", "config"]
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def run_continuous_processing(self):
        """Run continuous email processing loop"""
        self.logger.info("Starting continuous email processing...")
        
        while True:
            try:
                self.process_email_batch()
                self.logger.info("Completed processing cycle. Waiting 5 minutes for next cycle...")
                time.sleep(300)  # Wait 5 minutes
                
            except KeyboardInterrupt:
                self.logger.info("Received shutdown signal. Stopping gracefully...")
                break
            except Exception as e:
                self.logger.error(f"Error in processing cycle: {e}")
                self.logger.info("Waiting 1 minute before retry...")
                time.sleep(60)
    
    def process_email_batch(self):
        """Process a batch of emails"""
        try:
            # Fetch emails based on mode
            if self.demo_mode:
                emails = get_demo_emails()
                self.logger.info("Processing demo emails for demonstration")
            else:
                if 'fetch_live_emails' in globals():
                    emails = fetch_live_emails(max_results=10)
                else:
                    self.logger.error("Email fetching not available")
                    return
            
            if not emails:
                self.logger.info("No new emails found")
                return
            
            self.logger.info(f"Processing {len(emails)} new emails...")
            
            for i, email_data in enumerate(emails, 1):
                self.logger.info(f"Processing email {i}/{len(emails)}")
                result = self.process_single_email(email_data)
                if result:
                    self.logger.info(f"Successfully processed inquiry {result.get('inquiry_id')}")
            
            self.logger.info(f"Completed batch processing of {len(emails)} emails")
            
        except Exception as e:
            self.logger.error(f"Error in batch processing: {e}")
    
    def process_single_email(self, email_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single email through the LLM pipeline"""
        try:
            subject = email_data.get('subject', '')
            sender = email_data.get('sender', '')
            
            self.logger.info(f"Processing email from {sender} with subject: {subject[:50]}...")
            
            # Process the inquiry using LLM only
            result = self.processor.process_inquiry(email_data)
            
            if not result or result.get('error'):
                self.logger.warning("Failed to process inquiry - LLM processing failed")
                return None
            
            # Generate Excel report
            excel_path = self.excel_generator.generate_inquiry_report(result)
            result['excel_path'] = excel_path
            
            # Send email only in production mode
            if not self.demo_mode and self.email_sender:
                to_email = email_data.get('sender')
                if to_email:
                    subject = "Travel Quotation - LLM Processed"
                    body_text = f"""Dear {result.get('customer_name', 'Customer')},

Thank you for your travel inquiry. Please find attached the detailed quotation based on your requirements.

Trip Summary:
- Destinations: {', '.join(result.get('destinations', []))}
- Travel Dates: {result.get('departure_date', 'TBD')} to {result.get('return_date', 'TBD')}
- Travelers: {result.get('total_travelers', 'TBD')}
- Processing Confidence: {result.get('confidence_score', 0):.1%}

We look forward to serving you.

Best regards,
AI Travel Agent (LLM-Powered)"""

                    success = self.email_sender.send_email_with_attachment(
                        to_email=to_email,
                        subject=subject,
                        body_text=body_text,
                        attachment_path=excel_path
                    )
                    
                    if not success:
                        self.logger.warning(f"Failed to send quote to {to_email}")
                    else:
                        self.logger.info(f"Quote sent to {to_email}")
                else:
                    self.logger.warning("No sender email found")
            else:
                self.logger.info(f"Demo mode: Excel quotation generated at {excel_path}")
            
            # Log processing summary
            self.log_processing_summary(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing single email: {e}")
            return None
    
    def log_processing_summary(self, result: Dict[str, Any]):
        """Log a summary of the LLM processing results"""
        inquiry_id = result.get('inquiry_id', 'UNKNOWN')
        inquiry_type = result.get('inquiry_type', 'UNKNOWN')
        destinations = result.get('destinations', [])
        travelers = result.get('total_travelers', 'UNKNOWN')
        confidence = result.get('confidence_score', 0)
        
        self.logger.info(f"LLM PROCESSING SUMMARY:")
        self.logger.info(f"  Inquiry ID: {inquiry_id}")
        self.logger.info(f"  Type: {inquiry_type}")
        self.logger.info(f"  Destinations: {', '.join(destinations) if destinations else 'None'}")
        self.logger.info(f"  Travelers: {travelers}")
        self.logger.info(f"  Confidence: {confidence:.1%}")
        self.logger.info(f"  Excel: {result.get('excel_path', 'Not generated')}")
    
    def run_demo_mode(self):
        """Run a single demo processing cycle"""
        self.logger.info("Running demo mode - processing sample emails with LLM")
        print("Processing demo emails with LLM extraction...")
        
        # Process demo emails once
        self.process_email_batch()
        
        print("\nLLM demo processing completed!")
        print("Check the 'output' directory for generated Excel quotations.")

def main():
    """Main entry point for the Clean LLM Travel Agent"""
    print("="*60)
    print("   Clean LLM-Only AI Travel Agent - Production System")
    print("="*60)
    print()
    
    # Initialize the system
    agent = CleanLLMTravelAgent()
    
    # Check if we should run in demo mode
    demo_mode = os.getenv('DEMO_MODE', 'true').lower() != 'false'
    
    if demo_mode:
        print("Running in LLM DEMO MODE...")
        agent.run_demo_mode()
    else:
        print("Running in LLM PRODUCTION MODE...")
        print("Starting continuous email processing...")
        print("Press Ctrl+C to stop")
        agent.run_continuous_processing()

if __name__ == "__main__":
    exit(main())