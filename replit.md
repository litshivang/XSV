# AI Travel Agent - Email-based Quotation System

## Overview

This is an automated AI travel agent system that processes customer travel inquiries from emails, extracts relevant information, and generates Excel quotations. The system supports multiple languages (English, Hindi, Hinglish) and can classify different types of travel inquiries (single-leg, multi-leg, modifications).

## System Architecture

### Core Architecture
- **Modular Design**: Clean separation of concerns with dedicated modules for each processing step
- **Hybrid Processing**: Combines rule-based pattern matching with ML capabilities for optimal accuracy
- **Email Integration**: Gmail API integration for fetching and sending emails
- **Excel Generation**: Automated creation of professional travel quotations

### Processing Pipeline
1. **Email Fetching**: Live email retrieval from Gmail inbox
2. **Language Detection**: Multi-language support (English, Hindi, Hinglish)
3. **Entity Extraction**: NER for travelers, dates, budget, destinations, preferences
4. **Inquiry Classification**: Categorizes as single-leg, multi-leg, or modification requests
5. **Excel Generation**: Creates detailed quotation spreadsheets
6. **Email Response**: Automated reply with quotation attachment

## Key Components

### Language Detection (`modules/language_detector.py`)
- **HybridLanguageDetector**: Handles English, Hindi (Devanagari), Romanized Hindi, and Hinglish
- Uses pattern matching for reliable language identification
- Supports mixed-language content common in Indian travel industry

### Entity Extraction (`modules/extractor.py`)
- **EnhancedNERExtractor**: Extracts key travel information
- Patterns for: travelers count, budget (Indian currency), destinations, dates, preferences
- Handles various formats and Indian-specific terminology

### Inquiry Classification (`modules/inquiry_classifier.py`)
- **InquiryClassifier**: Categorizes inquiry types
- **Single-leg**: Basic trips to one destination
- **Multi-leg**: Complex itineraries with multiple locations
- **Modification**: Changes to existing quotations

### Excel Generation (`modules/excel_generator.py`)
- **ExcelGenerator**: Creates professional quotation documents
- Structured format with all extracted information
- Uses xlsxwriter for formatting and styling

### Data Schema (`modules/schema.py`)
- Pydantic models for structured data validation
- Separate schemas for different inquiry types
- Ensures data consistency and type safety

## Data Flow

1. **Email Ingestion**: System fetches unread emails from specified Gmail account
2. **Text Processing**: Email content is cleaned and prepared for analysis
3. **Language Analysis**: Primary language is detected and confidence scored
4. **Information Extraction**: Key travel details are extracted using hybrid patterns
5. **Classification**: Inquiry type is determined with confidence scoring
6. **Data Validation**: Extracted data is validated against Pydantic schemas
7. **Excel Generation**: Structured quotation is created with all details
8. **Response Automation**: Reply email is sent with quotation attachment

## External Dependencies

### Google APIs
- **Gmail API**: Email fetching and sending capabilities
- **OAuth2 Authentication**: Secure access to Gmail account
- Requires `credentials.json` and generates `token.pickle`

### Python Libraries
- **xlsxwriter**: Excel file generation with formatting
- **pandas**: Data manipulation and analysis
- **pydantic**: Data validation and settings management
- **google-api-python-client**: Google API integration
- **google-auth-oauthlib**: OAuth authentication flow

### Optional ML Libraries
- **spacy**: Advanced NLP processing (if available)
- **langdetect**: Language detection enhancement
- **transformers**: Additional NER capabilities

## Deployment Strategy

### Development Mode
- **Demo Mode**: Uses sample emails for testing without Gmail API
- **Local Testing**: Processes sample data from DATA directory
- **File-based Output**: Generates Excel files in output directory

### Production Mode
- **Live Email Processing**: Continuous monitoring of Gmail inbox
- **Batch Processing**: Handles multiple emails efficiently
- **Error Handling**: Robust error recovery and logging
- **Automated Scheduling**: Configurable processing intervals

### Configuration
- **Environment Variables**: Secure credential management
- **Config Files**: Centralized settings in `utils/config.py`
- **Logging**: Comprehensive logging to files and console

## Changelog

- June 20, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.