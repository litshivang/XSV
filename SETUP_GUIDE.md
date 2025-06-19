# AI Travel Agent - Setup Guide

## Overview

This guide will help you set up the fully automated AI Travel Agent system that processes customer travel inquiries via email, generates Excel quotations, and sends automated replies.

## System Requirements

- Python 3.11+
- Gmail and/or Outlook email account with API access
- Replit environment (recommended) or local development setup

## Installation Steps

### 1. Environment Setup

```bash
# Install required packages
pip install pydantic pandas openpyxl chardet python-dotenv
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install O365 exchangelib APScheduler openai email-validator
```

### 2. Email API Configuration

#### Gmail Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create credentials (OAuth 2.0 Client ID)
5. Download credentials JSON file and save as `credentials/gmail_credentials.json`

#### Outlook Setup (Optional)

1. Go to [Azure Portal](https://portal.azure.com/)
2. Register a new application
3. Add Microsoft Graph permissions for Mail.ReadWrite
4. Note down Client ID and Client Secret

### 3. Environment Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Target Email Configuration
TARGET_EMAIL=shivangnvyas@gmail.com
MAX_EMAILS_PER_RUN=50
ENABLE_GMAIL=true
ENABLE_OUTLOOK=false
AUTO_REPLY=true

# Gmail API Credentials
GMAIL_CLIENT_ID=your_gmail_client_id_here
GMAIL_CLIENT_SECRET=your_gmail_client_secret_here

# Outlook API Credentials (if using)
OUTLOOK_CLIENT_ID=your_outlook_client_id_here
OUTLOOK_CLIENT_SECRET=your_outlook_client_secret_here
```

### 4. Directory Structure

The system will create these directories automatically:

```
├── data/                    # Processing data and tracking
├── output/quotes/          # Generated Excel quotations
├── logs/                   # System logs
├── credentials/            # API credentials
└── backup/                 # Backup files
```

## Usage

### Manual Processing

Run a single processing cycle:

```bash
python automated_main.py
```

### Scheduled Processing

Run with automatic scheduling:

```bash
# Every 30 minutes (default)
python scheduler.py --mode schedule

# Every 10 minutes (for testing)
python scheduler.py --mode schedule --schedule-type frequent --minutes 10

# Daily at 9 AM
python scheduler.py --mode schedule --schedule-type daily --hour 9

# Custom cron schedule
python scheduler.py --mode schedule --schedule-type custom_cron --cron "0 */2 * * *"
```

### Testing

Run the comprehensive test suite:

```bash
python test_system.py
```

## How It Works

### 1. Email Processing Flow

1. **Email Fetching**: System connects to Gmail/Outlook and fetches unread emails to `shivangnvyas@gmail.com`
2. **Content Analysis**: Extracts customer information and trip requirements using rule-based parsing
3. **Inquiry Classification**: Determines if it's a single-leg, multi-leg, or modification request
4. **Data Extraction**: Extracts destinations, dates, travelers, budget, and special requirements

### 2. Excel Generation

1. **Individual Quotes**: Generates separate Excel file for each inquiry
2. **Multi-sheet Format**: 
   - Travel Quote Summary
   - Detailed Itinerary (single-leg) or Segment Details (multi-leg)
   - Terms & Conditions
3. **Professional Formatting**: Styled headers, borders, and conditional layouts

### 3. Automated Replies

1. **Email Response**: Sends personalized reply with Excel attachment
2. **Tracking**: Records all processing activities in SQLite database
3. **Idempotency**: Prevents reprocessing of same emails

## Supported Inquiry Types

### Single-leg Trips
- Simple destination trips (e.g., "Goa vacation for 5 days")
- Extracts: destination, duration, travelers, budget, dates

### Multi-leg Trips
- Complex itineraries (e.g., "Delhi-Agra-Jaipur Golden Triangle")
- Creates separate segments for each destination
- Generates multi-sheet Excel with segment details

### Modification Requests
- Updates to existing bookings
- Detects reference to original inquiry ID
- Updates existing Excel files with modification notices

## Monitoring and Logs

### Log Files
- `logs/main.log` - Main application logs
- `logs/email_fetcher.log` - Email processing logs
- `logs/enhanced_inquiry_processor.log` - Inquiry processing logs
- `logs/enhanced_excel_generator.log` - Excel generation logs

### Processing Statistics
- Stored in `data/processing_stats.json`
- Tracks success rates, processing times, and errors
- Accessible via API or direct file inspection

## Troubleshooting

### Common Issues

1. **Gmail Authentication Errors**
   - Verify credentials file path and content
   - Check OAuth scopes and permissions
   - Ensure Gmail API is enabled

2. **No Emails Found**
   - Verify target email address
   - Check email filters and labels
   - Ensure emails are unread

3. **Excel Generation Fails**
   - Check write permissions in `output/quotes/` directory
   - Verify pandas and openpyxl installation
   - Review logs for specific errors

4. **Scheduler Issues**
   - Verify APScheduler installation
   - Check system permissions for background processes
   - Review scheduler logs for timing conflicts

### Debug Mode

Enable debug logging:

```env
LOG_LEVEL=DEBUG
DEBUG_MODE=true
```

### Manual Testing

Test individual components:

```python
# Test email fetching
from email_fetcher import EmailFetcher
from enhanced_schema import ProcessingConfig

config = ProcessingConfig()
fetcher = EmailFetcher(config)
emails = fetcher.fetch_new_emails()

# Test inquiry processing
from enhanced_inquiry_processor import EnhancedInquiryProcessor

processor = EnhancedInquiryProcessor()
inquiry = processor.process_email_inquiry(email_data)

# Test Excel generation
from enhanced_excel_generator import EnhancedExcelGenerator

generator = EnhancedExcelGenerator()
excel_path = generator.generate_individual_quote(inquiry)
```

## Security Considerations

### Credentials Management
- Store API credentials in environment variables
- Use Replit Secrets for production deployment
- Never commit credentials to version control

### Email Security
- Validate sender addresses
- Sanitize email content before processing
- Implement rate limiting for API calls

### File Security
- Secure generated Excel files
- Implement proper access controls
- Regular cleanup of temporary files

## Performance Optimization

### Recommended Settings
- `MAX_EMAILS_PER_RUN=50` for balanced processing
- `DEFAULT_SCHEDULE_MINUTES=30` for regular processing
- Enable concurrent processing for multiple emails

### Resource Management
- Monitor memory usage with large email volumes
- Implement cleanup routines for old files
- Use batch processing for efficiency

## Deployment

### Replit Deployment
1. Upload all files to Replit project
2. Configure environment variables in Secrets tab
3. Set up scheduled runs using Replit's cron functionality
4. Monitor logs through Replit console

### Production Considerations
- Use proper logging and monitoring
- Implement backup strategies
- Set up alerting for processing failures
- Regular maintenance and updates

## Support

For issues and questions:
1. Check logs for error details
2. Review this setup guide
3. Run the test suite to identify problems
4. Verify API credentials and permissions

## Updates and Maintenance

### Regular Tasks
- Monitor processing statistics
- Clean up old Excel files
- Update API credentials before expiry
- Review and optimize extraction rules

### Version Updates
- Test new versions in staging environment
- Backup data before updates
- Monitor for breaking changes in dependencies
- Update documentation as needed