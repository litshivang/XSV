"""
Final Automated AI Travel Agent - Production System
Processes customer travel inquiries via email, generates Excel quotations, and sends automated replies.
"""

import time
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Import core modules
from optimized_agent import OptimizedTravelAgentProcessor
from modules.optimized_excel_generator import OptimizedExcelGenerator
from utils.email_fetcher import fetch_live_emails

# Setup comprehensive logging
def setup_logging():
    """Setup production-grade logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(
        log_dir / f"travel_agent_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

class FinalAutomatedTravelAgent:
    """
    Production-ready automated travel agent system
    Handles complete email-to-quote workflow
    """
    
    def __init__(self):
        """Initialize the automated travel agent system"""
        self.logger = setup_logging()
        self.processor = OptimizedTravelAgentProcessor()
        self.excel_generator = OptimizedExcelGenerator()
        
        # Setup output directories
        self.setup_directories()
        
        self.logger.info("Final Automated Travel Agent initialized successfully")
    
    def setup_directories(self):
        """Setup required directories for the application"""
        directories = ["output", "logs", "config", "temp"]
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def run_continuous_processing(self):
        """
        Run continuous email processing loop
        Checks for new emails every 5 minutes
        """
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
        """Process a batch of emails from the inbox"""
        try:
            # Fetch live emails
            live_emails = fetch_live_emails(max_results=10)
            
            if not live_emails:
                self.logger.info("No new emails found")
                return
            
            self.logger.info(f"Processing {len(live_emails)} new emails...")
            
            # Process each email
            for i, email_data in enumerate(live_emails, 1):
                self.logger.info(f"Processing email {i}/{len(live_emails)}")
                result = self.process_single_email(email_data)
                
                if result:
                    self.logger.info(f"Successfully processed inquiry {result.get('inquiry_id')}")
                else:
                    self.logger.warning(f"Failed to process email {i}")
            
            self.logger.info(f"Completed batch processing of {len(live_emails)} emails")
            
        except Exception as e:
            self.logger.error(f"Error in batch processing: {e}")
    
    def process_single_email(self, email_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single email through the complete pipeline
        
        Args:
            email_data: Email data containing subject, body, sender, etc.
            
        Returns:
            Dict containing processed inquiry data or None if failed
        """
        try:
            # Extract basic email info
            subject = email_data.get('subject', '')
            sender = email_data.get('sender', '')
            
            self.logger.info(f"Processing email from {sender} with subject: {subject[:50]}...")
            
            # Process the inquiry
            result = self.processor.process_inquiry(email_data)
            
            if not result:
                self.logger.warning("Failed to process inquiry - no result returned")
                return None
            
            # Generate Excel report
            excel_path = self.excel_generator.generate_inquiry_report(result)
            result['excel_path'] = excel_path
            
            # Log key details
            self.log_processing_summary(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing single email: {e}")
            return None
    
    def log_processing_summary(self, result: Dict[str, Any]):
        """Log a summary of the processing results"""
        inquiry_id = result.get('inquiry_id', 'UNKNOWN')
        language = result.get('language_info', {}).get('primary_language', 'UNKNOWN')
        inquiry_type = result.get('inquiry_type', {}).get('type', 'UNKNOWN')
        destinations = result.get('location_details', {}).get('all_destinations', [])
        travelers = result.get('traveler_details', {}).get('total_travelers', 'UNKNOWN')
        
        self.logger.info(f"PROCESSING SUMMARY:")
        self.logger.info(f"  Inquiry ID: {inquiry_id}")
        self.logger.info(f"  Language: {language}")
        self.logger.info(f"  Type: {inquiry_type}")
        self.logger.info(f"  Destinations: {', '.join(destinations) if destinations else 'None'}")
        self.logger.info(f"  Travelers: {travelers}")
        self.logger.info(f"  Excel: {result.get('excel_path', 'Not generated')}")
    
    def run_demo_mode(self):
        """
        Run in demo mode with sample data for testing
        """
        self.logger.info("Running in demo mode...")
        
        # Create sample email data
        sample_emails = [
            {
                'subject': 'Planning a trip to Goa',
                'body': 'Hi, I am planning a trip to Goa for 2 adults and 1 child. We want to go for 4 nights in December. Our budget is around 50000 rupees. Please send me a quote.',
                'sender': 'demo@example.com',
                'received_date': datetime.now().isoformat()
            },
            {
                'subject': 'Kerala trip inquiry',
                'body': 'Hello, we are a family of 4 looking for a Kerala trip. We want to visit Munnar, Alleppey and Kochi. Duration should be 6 nights. Budget is flexible. Please provide quotation.',
                'sender': 'family@example.com',
                'received_date': datetime.now().isoformat()
            }
        ]
        
        self.logger.info(f"Processing {len(sample_emails)} demo emails...")
        
        for i, email_data in enumerate(sample_emails, 1):
            self.logger.info(f"Processing demo email {i}/{len(sample_emails)}")
            result = self.process_single_email(email_data)
            
            if result:
                self.logger.info(f"Demo email {i} processed successfully")
            else:
                self.logger.warning(f"Demo email {i} processing failed")
        
        self.logger.info("Demo mode completed")

def main():
    """
    Main entry point for the Final Automated Travel Agent
    """
    print("="*60)
    print("   Final Automated AI Travel Agent - Production System")
    print("="*60)
    print()
    
    # Initialize the system
    agent = FinalAutomatedTravelAgent()
    
    # Check if we should run in demo mode (default to demo if no credentials)
    demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
    
    if demo_mode:
        print("Running in DEMO MODE...")
        agent.run_demo_mode()
    else:
        print("Starting continuous email processing...")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            agent.run_continuous_processing()
        except KeyboardInterrupt:
            print("\nShutdown requested. Goodbye!")
        except Exception as e:
            print(f"Fatal error: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    exit(main())