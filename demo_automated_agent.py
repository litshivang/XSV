#!/usr/bin/env python3
"""
Demo Automated AI Travel Agent - Email-based Quotation System
Demonstrates the complete automated workflow with mock email processing
"""

import os
import json
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import re


class MockEmailData:
    """Mock email data for demonstration"""
    
    def __init__(self):
        self.sample_emails = [
            {
                'message_id': 'demo_001',
                'thread_id': 'thread_001',
                'from': 'John Doe <john.doe@example.com>',
                'to': 'shivangnvyas@gmail.com',
                'subject': 'Goa Family Trip Inquiry',
                'date': '2024-12-19 10:30:00',
                'body': '''Dear Travel Agent,

I am planning a family trip to Goa for 6 days and 5 nights with my family of 4 people (2 adults and 2 children aged 8 and 12).

Travel dates: 25th December 2024 to 30th December 2024
Budget: Around Rs. 80,000 for the entire family
Departure city: Mumbai

We would like:
- 4-star hotel accommodation with swimming pool
- Airport transfers included
- Half board meal plan (breakfast and dinner)
- Local sightseeing tours
- Beach activities for children

Special requirements:
- One room should be adjoining/connecting rooms for family
- Vegetarian meal options
- Early check-in if possible (arriving early morning)

Please send detailed quotation with day-wise itinerary.

Best regards,
John Doe
Phone: +91 9876543210'''
            },
            {
                'message_id': 'demo_002',
                'thread_id': 'thread_002', 
                'from': 'Priya Sharma <priya.sharma@gmail.com>',
                'to': 'shivangnvyas@gmail.com',
                'subject': 'Kerala Honeymoon Package - Multi-destination',
                'date': '2024-12-19 14:15:00',
                'body': '''Hello,

We are planning our honeymoon trip to Kerala for 8 days and 7 nights. We want to visit multiple destinations:

First 3 nights in Munnar (hill station)
Then 2 nights in Thekkady (wildlife)
Finally 2 nights in Alleppey (backwaters)

Travel dates: 5th February 2025 to 12th February 2025
Number of travelers: 2 people (couple)
Budget: Rs. 1,20,000 total

Requirements:
- Luxury/5-star accommodation
- Private car with driver for entire trip
- Candlelight dinner arrangements
- Couple spa sessions
- Houseboat stay in Alleppey
- Photography sessions at scenic locations

We need flight bookings from Delhi to Kochi and return.

Please prepare detailed quotation for this multi-destination honeymoon package.

Thanks & Regards,
Priya Sharma
Email: priya.sharma@gmail.com
Phone: +91 9988776655'''
            },
            {
                'message_id': 'demo_003',
                'thread_id': 'thread_003',
                'from': 'Corporate Travel <corporate@techcompany.com>',
                'to': 'shivangnvyas@gmail.com',
                'subject': 'Golden Triangle Corporate Tour - Modification Request',
                'date': '2024-12-19 16:45:00',
                'body': '''Hi,

This is regarding our previous inquiry for Golden Triangle tour (Inquiry ID: INQ_20241215_001).

We need to modify the following:
- Change travel dates from 20th January to 10th February 2025
- Increase group size from 15 to 18 people
- Add one extra day in Jaipur (total 4 days instead of 3)
- Upgrade to 5-star hotels throughout
- Include team building activities in Jaipur

Original itinerary was:
- Delhi: 2 days
- Agra: 2 days  
- Jaipur: 3 days (now 4 days)

Budget can be increased to Rs. 8,00,000 total for 18 people.

Please send updated quotation with these modifications.

Best regards,
Travel Coordinator
TechCompany Ltd.
Email: corporate@techcompany.com'''
            }
        ]


class DemoInquiryProcessor:
    """Demo inquiry processor with rule-based extraction"""
    
    def __init__(self):
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(?:\+91[-\s]?)?[6-9]\d{9}',
            'currency': r'(?:Rs\.?|INR|₹)\s*[\d,]+(?:\.\d{2})?',
            'date': r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',
            'travelers': r'\b(\d+)\s*(?:people|persons?|travelers?|pax|adults?)\b',
            'duration': r'\b(\d+)\s*(?:days?|nights?)\b'
        }
    
    def process_email_inquiry(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process email inquiry and extract structured data"""
        start_time = time.time()
        
        try:
            body = email_data.get('body', '')
            subject = email_data.get('subject', '')
            full_text = f"{subject}\n\n{body}"
            
            # Generate inquiry ID
            inquiry_id = f"INQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{email_data.get('message_id', 'unknown')[:8]}"
            
            # Determine inquiry type
            inquiry_type = self._determine_inquiry_type(full_text)
            
            # Extract customer information
            customer_name = self._extract_customer_name(body, email_data.get('from', ''))
            customer_email = self._extract_email_address(email_data.get('from', ''))
            phone = self._extract_phone(body)
            
            # Extract trip details
            destinations = self._extract_destinations(full_text)
            travelers = self._extract_travelers(body)
            duration = self._extract_duration(body)
            budget = self._extract_budget(body)
            dates = self._extract_dates(body)
            requirements = self._extract_requirements(body)
            
            # Create inquiry result
            inquiry = {
                'inquiry_id': inquiry_id,
                'inquiry_type': inquiry_type,
                'email_message_id': email_data.get('message_id'),
                'email_subject': subject,
                'customer_name': customer_name,
                'customer_email': customer_email,
                'contact_phone': phone,
                'destinations': destinations,
                'num_travelers': travelers,
                'duration_nights': duration,
                'total_budget': budget,
                'travel_dates': dates,
                'special_requirements': requirements,
                'processing_status': 'success',
                'processing_time': round(time.time() - start_time, 3),
                'extraction_method': 'demo_rule_based'
            }
            
            return inquiry
            
        except Exception as e:
            return {
                'inquiry_id': f"ERROR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'processing_status': f'error: {str(e)}',
                'processing_time': round(time.time() - start_time, 3)
            }
    
    def _determine_inquiry_type(self, text: str) -> str:
        """Determine inquiry type"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['modify', 'change', 'update', 'revise']):
            return 'modification'
        elif any(word in text_lower for word in ['then', 'next', 'followed by', 'first', 'multiple destination']):
            return 'multi_leg'
        else:
            return 'single_leg'
    
    def _extract_customer_name(self, body: str, from_field: str) -> str:
        """Extract customer name"""
        # Try from signature
        lines = body.strip().split('\n')
        for line in reversed(lines):
            line = line.strip()
            if line and not '@' in line and len(line.split()) <= 3:
                line = re.sub(r'^(Best regards,|Thanks,|Regards,)\s*', '', line, flags=re.IGNORECASE)
                if line and line.lower() not in ['thanks', 'regards', 'best']:
                    return line
        
        # Try from email field
        if '<' in from_field:
            return from_field.split('<')[0].strip()
        
        return 'Valued Customer'
    
    def _extract_email_address(self, from_field: str) -> str:
        """Extract email address"""
        match = re.search(self.patterns['email'], from_field)
        return match.group(0) if match else ''
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        match = re.search(self.patterns['phone'], text)
        return match.group(0) if match else ''
    
    def _extract_destinations(self, text: str) -> List[str]:
        """Extract destinations"""
        destinations = []
        common_destinations = [
            'goa', 'kerala', 'munnar', 'alleppey', 'thekkady', 'delhi', 'agra', 'jaipur',
            'mumbai', 'bangalore', 'chennai', 'kochi', 'trivandrum'
        ]
        
        text_lower = text.lower()
        for dest in common_destinations:
            if dest in text_lower:
                destinations.append(dest.title())
        
        return list(set(destinations))
    
    def _extract_travelers(self, text: str) -> Optional[int]:
        """Extract number of travelers"""
        match = re.search(self.patterns['travelers'], text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Check for family mentions
        if 'family' in text.lower():
            family_match = re.search(r'family of (\d+)', text, re.IGNORECASE)
            if family_match:
                return int(family_match.group(1))
        
        return None
    
    def _extract_duration(self, text: str) -> Optional[int]:
        """Extract duration in nights"""
        night_match = re.search(r'(\d+)\s*nights?', text, re.IGNORECASE)
        if night_match:
            return int(night_match.group(1))
        
        day_match = re.search(r'(\d+)\s*days?', text, re.IGNORECASE)
        if day_match:
            return max(1, int(day_match.group(1)) - 1)
        
        return None
    
    def _extract_budget(self, text: str) -> str:
        """Extract budget"""
        match = re.search(self.patterns['currency'], text)
        return match.group(0) if match else ''
    
    def _extract_dates(self, text: str) -> str:
        """Extract travel dates"""
        dates = re.findall(self.patterns['date'], text, re.IGNORECASE)
        return ', '.join(dates[:2]) if dates else ''
    
    def _extract_requirements(self, text: str) -> str:
        """Extract special requirements"""
        requirements = []
        
        if re.search(r'vegetarian|veg', text, re.IGNORECASE):
            requirements.append('Vegetarian meals')
        if re.search(r'spa|massage', text, re.IGNORECASE):
            requirements.append('Spa services')
        if re.search(r'honeymoon|romantic', text, re.IGNORECASE):
            requirements.append('Honeymoon arrangements')
        if re.search(r'children|kids', text, re.IGNORECASE):
            requirements.append('Child-friendly arrangements')
        if re.search(r'corporate|team', text, re.IGNORECASE):
            requirements.append('Corporate arrangements')
        
        return ', '.join(requirements)


class DemoExcelGenerator:
    """Demo Excel generator using CSV format"""
    
    def __init__(self):
        self.output_dir = Path("output/quotes")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_individual_quote(self, inquiry: Dict[str, Any]) -> str:
        """Generate individual quote file"""
        try:
            # Generate filename
            customer_name = inquiry.get('customer_name', 'Customer').replace(' ', '_')
            filename = f"Quote_{customer_name}_{inquiry['inquiry_id']}.csv"
            filepath = self.output_dir / filename
            
            # Create quote data
            quote_data = [
                ['TRAVEL QUOTATION', ''],
                ['', ''],
                ['Inquiry ID', inquiry['inquiry_id']],
                ['Date', datetime.now().strftime('%B %d, %Y')],
                ['Customer Name', inquiry.get('customer_name', '')],
                ['Email', inquiry.get('customer_email', '')],
                ['Phone', inquiry.get('contact_phone', '')],
                ['', ''],
                ['TRIP DETAILS', ''],
                ['Destinations', ', '.join(inquiry.get('destinations', []))],
                ['Number of Travelers', inquiry.get('num_travelers', 'TBD')],
                ['Duration', f"{inquiry.get('duration_nights', 'TBD')} nights" if inquiry.get('duration_nights') else 'TBD'],
                ['Travel Dates', inquiry.get('travel_dates', 'TBD')],
                ['Total Budget', inquiry.get('total_budget', 'To be quoted')],
                ['', ''],
                ['SPECIAL REQUIREMENTS', ''],
                ['Requirements', inquiry.get('special_requirements', 'None specified')],
                ['', ''],
                ['SERVICES INCLUDED', ''],
                ['Services', 'Accommodation, Meals as specified, Transportation, Sightseeing, Guide services'],
                ['', ''],
                ['STATUS', ''],
                ['Inquiry Type', inquiry.get('inquiry_type', 'standard')],
                ['Processing Status', inquiry.get('processing_status', 'processed')],
                ['Generated At', datetime.now().isoformat()]
            ]
            
            # Write CSV file
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(quote_data)
            
            print(f"Quote generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"Error generating quote: {e}")
            return ""


class DemoEmailSender:
    """Demo email sender that simulates sending replies"""
    
    def send_reply_with_quote(self, email_data: Dict[str, Any], 
                             quote_path: str, inquiry_id: str) -> bool:
        """Simulate sending reply email with quote"""
        try:
            customer_email = self._extract_email_address(email_data.get('from', ''))
            subject = email_data.get('subject', 'Travel Inquiry')
            
            # Create reply message
            reply_content = f"""Dear Valued Customer,

Thank you for your travel inquiry. We have carefully reviewed your requirements and prepared a customized quotation for your trip.

Inquiry Details:
- Inquiry ID: {inquiry_id}
- Quote File: {Path(quote_path).name}
- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Our team has prepared a detailed quotation based on your requirements. The quote includes accommodation, transportation, meals, and sightseeing as discussed.

We would be happy to discuss any modifications or answer any questions you may have about the proposed itinerary.

Please feel free to contact us for any clarifications.

Best regards,
AI Travel Agent Team
Email: shivangnvyas@gmail.com

---
This is an automated response generated by AI Travel Agent System.
Your inquiry has been processed and a detailed quotation has been prepared.
"""
            
            # Log the reply (in real system, this would send actual email)
            reply_log = {
                'timestamp': datetime.now().isoformat(),
                'to': customer_email,
                'subject': f"Re: {subject}",
                'inquiry_id': inquiry_id,
                'quote_attached': quote_path,
                'status': 'sent_simulation'
            }
            
            # Save reply log
            reply_log_file = Path("logs/email_replies.json")
            reply_log_file.parent.mkdir(exist_ok=True)
            
            replies = []
            if reply_log_file.exists():
                try:
                    with open(reply_log_file, 'r') as f:
                        replies = json.load(f)
                except:
                    replies = []
            
            replies.append(reply_log)
            
            with open(reply_log_file, 'w') as f:
                json.dump(replies, f, indent=2)
            
            print(f"Reply sent (simulated) to: {customer_email}")
            print(f"Subject: Re: {subject}")
            return True
            
        except Exception as e:
            print(f"Error sending reply: {e}")
            return False
    
    def _extract_email_address(self, from_field: str) -> str:
        """Extract email address from 'From' field"""
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', from_field)
        return match.group(0) if match else from_field


class DemoAutomatedTravelAgent:
    """Demo automated travel agent orchestrator"""
    
    def __init__(self):
        self.mock_emails = MockEmailData()
        self.processor = DemoInquiryProcessor()
        self.excel_generator = DemoExcelGenerator()
        self.email_sender = DemoEmailSender()
        
        # Setup directories
        for directory in ["data", "logs", "output/quotes"]:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def run_demo_cycle(self) -> Dict[str, Any]:
        """Run a complete demo processing cycle"""
        print("=== AI Travel Agent - Automated Email Processing Demo ===")
        print(f"Starting demo at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        cycle_start = datetime.now()
        
        stats = {
            'cycle_start': cycle_start.isoformat(),
            'emails_fetched': 0,
            'emails_processed': 0,
            'quotes_generated': 0,
            'replies_sent': 0,
            'errors': 0,
            'processing_details': []
        }
        
        # Get demo emails
        demo_emails = self.mock_emails.sample_emails
        stats['emails_fetched'] = len(demo_emails)
        
        print(f"\nFetched {len(demo_emails)} demo emails for processing...")
        
        # Process each email
        for i, email_data in enumerate(demo_emails, 1):
            print(f"\n--- Processing Email {i}/{len(demo_emails)} ---")
            print(f"From: {email_data['from']}")
            print(f"Subject: {email_data['subject']}")
            
            email_stats = self.process_single_email(email_data)
            stats['processing_details'].append(email_stats)
            
            # Update overall stats
            if email_stats['status'] == 'success':
                stats['emails_processed'] += 1
                if email_stats['quote_generated']:
                    stats['quotes_generated'] += 1
                if email_stats['reply_sent']:
                    stats['replies_sent'] += 1
            else:
                stats['errors'] += 1
        
        # Calculate final stats
        cycle_end = datetime.now()
        cycle_duration = (cycle_end - cycle_start).total_seconds()
        
        stats['cycle_end'] = cycle_end.isoformat()
        stats['cycle_duration_seconds'] = cycle_duration
        
        # Print results
        print(f"\n=== Demo Processing Results ===")
        print(f"Emails processed: {stats['emails_processed']}/{stats['emails_fetched']}")
        print(f"Quotes generated: {stats['quotes_generated']}")
        print(f"Reply emails sent: {stats['replies_sent']}")
        print(f"Errors: {stats['errors']}")
        print(f"Total time: {cycle_duration:.2f} seconds")
        
        # Save stats
        self.save_demo_stats(stats)
        
        return stats
    
    def process_single_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single email through the complete pipeline"""
        email_stats = {
            'message_id': email_data.get('message_id'),
            'customer_email': self._extract_customer_email(email_data.get('from', '')),
            'subject': email_data.get('subject', ''),
            'status': 'processing',
            'quote_generated': False,
            'reply_sent': False,
            'inquiry_id': None,
            'quote_path': None
        }
        
        try:
            # Step 1: Process inquiry
            print("  • Processing inquiry...")
            inquiry = self.processor.process_email_inquiry(email_data)
            email_stats['inquiry_id'] = inquiry['inquiry_id']
            
            if inquiry['processing_status'] != 'success':
                raise Exception(f"Inquiry processing failed: {inquiry['processing_status']}")
            
            print(f"    ✓ Inquiry processed: {inquiry['inquiry_id']}")
            print(f"    ✓ Type: {inquiry['inquiry_type']}")
            print(f"    ✓ Destinations: {', '.join(inquiry.get('destinations', []))}")
            print(f"    ✓ Travelers: {inquiry.get('num_travelers', 'TBD')}")
            print(f"    ✓ Budget: {inquiry.get('total_budget', 'TBD')}")
            
            # Step 2: Generate quote
            print("  • Generating quote...")
            quote_path = self.excel_generator.generate_individual_quote(inquiry)
            
            if quote_path:
                email_stats['quote_generated'] = True
                email_stats['quote_path'] = quote_path
                print(f"    ✓ Quote generated: {Path(quote_path).name}")
            else:
                raise Exception("Failed to generate quote")
            
            # Step 3: Send reply
            print("  • Sending reply...")
            reply_sent = self.email_sender.send_reply_with_quote(
                email_data, quote_path, inquiry['inquiry_id']
            )
            
            if reply_sent:
                email_stats['reply_sent'] = True
                print(f"    ✓ Reply sent successfully")
            
            email_stats['status'] = 'success'
            print(f"  ✓ Email processing completed successfully")
            
        except Exception as e:
            email_stats['status'] = 'error'
            email_stats['error'] = str(e)
            print(f"  ✗ Error: {e}")
        
        return email_stats
    
    def _extract_customer_email(self, from_field: str) -> str:
        """Extract customer email from 'From' field"""
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', from_field)
        return match.group(0) if match else from_field
    
    def save_demo_stats(self, stats: Dict[str, Any]):
        """Save demo statistics"""
        stats_file = Path("data/demo_stats.json")
        
        try:
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
            print(f"\nDemo statistics saved to: {stats_file}")
        except Exception as e:
            print(f"Error saving stats: {e}")


def main():
    """Main demo entry point"""
    try:
        # Run the demo
        agent = DemoAutomatedTravelAgent()
        results = agent.run_demo_cycle()
        
        # Show final summary
        print(f"\n{'='*60}")
        print("DEMO COMPLETION SUMMARY")
        print(f"{'='*60}")
        print(f"✓ Successfully demonstrated automated email-based travel quotation system")
        print(f"✓ Processed {results['emails_processed']} travel inquiries")
        print(f"✓ Generated {results['quotes_generated']} individual Excel quotes")
        print(f"✓ Sent {results['replies_sent']} automated reply emails")
        print(f"✓ Complete processing time: {results['cycle_duration_seconds']:.2f} seconds")
        
        print(f"\nGenerated files:")
        quote_files = list(Path("output/quotes").glob("*.csv"))
        for quote_file in quote_files:
            print(f"  • {quote_file}")
        
        if Path("logs/email_replies.json").exists():
            print(f"  • logs/email_replies.json (reply log)")
        
        print(f"\n✓ AI Travel Agent automation demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()