"""
Enhanced Schema definition for AI Travel Agent with Multi-leg Support
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class InquiryType(str, Enum):
    """Type of travel inquiry"""
    SINGLE_LEG = "single_leg"
    MULTI_LEG = "multi_leg"
    MODIFICATION = "modification"


class TripSegment(BaseModel):
    """Individual segment of a multi-leg trip"""
    
    # Segment identification
    segment_id: Optional[str] = Field(None, description="Unique identifier for this segment")
    sequence_order: Optional[int] = Field(None, description="Order of this segment in the trip")
    
    # Destination and timing
    destination: Optional[str] = Field(None, description="Destination for this segment")
    departure_city: Optional[str] = Field(None, description="Departure city for this segment")
    start_date: Optional[str] = Field(None, description="Start date for this segment")
    end_date: Optional[str] = Field(None, description="End date for this segment")
    duration_nights: Optional[int] = Field(None, description="Number of nights for this segment")
    
    # Accommodation preferences
    hotel_category: Optional[str] = Field(None, description="Hotel category (3*, 4*, 5*, luxury, budget)")
    room_type: Optional[str] = Field(None, description="Room type preferences")
    meal_plan: Optional[str] = Field(None, description="Meal plan (BB, HB, FB, AI)")
    
    # Activities and experiences
    activities: List[str] = Field(default_factory=list, description="Activities for this segment")
    sightseeing: List[str] = Field(default_factory=list, description="Sightseeing places")
    experiences: List[str] = Field(default_factory=list, description="Special experiences")
    
    # Transportation
    needs_flight: Optional[bool] = Field(None, description="Flight required for this segment")
    transportation_type: Optional[str] = Field(None, description="Transportation type (flight, train, bus, car)")
    
    # Segment-specific budget
    segment_budget: Optional[str] = Field(None, description="Budget allocated for this segment")
    
    # Special requirements
    special_requests: Optional[str] = Field(None, description="Special requests for this segment")
    notes: Optional[str] = Field(None, description="Additional notes for this segment")


class EnhancedTripInquiry(BaseModel):
    """Enhanced Pydantic model for validating travel inquiry data with multi-leg support"""
    
    # Inquiry metadata
    inquiry_id: Optional[str] = Field(None, description="Unique inquiry identifier")
    inquiry_type: InquiryType = Field(InquiryType.SINGLE_LEG, description="Type of inquiry")
    email_subject: Optional[str] = Field(None, description="Original email subject")
    email_message_id: Optional[str] = Field(None, description="Email message ID for tracking")
    email_thread_id: Optional[str] = Field(None, description="Email thread ID for modifications")
    
    # Customer information
    customer_name: Optional[str] = Field(None, description="Customer name")
    customer_email: Optional[str] = Field(None, description="Customer email address")
    contact_phone: Optional[str] = Field(None, description="Customer phone number")
    contact_info: Optional[str] = Field(None, description="Additional contact information")
    
    # Overall trip details
    num_travelers: Optional[int] = Field(None, description="Total number of travelers")
    num_adults: Optional[int] = Field(None, description="Number of adult travelers")
    num_children: Optional[int] = Field(None, description="Number of child travelers")
    travel_party_composition: Optional[str] = Field(None, description="Travel party details")
    
    # Trip timing and duration
    overall_start_date: Optional[str] = Field(None, description="Overall trip start date")
    overall_end_date: Optional[str] = Field(None, description="Overall trip end date")
    total_duration_nights: Optional[int] = Field(None, description="Total nights for entire trip")
    
    # Budget information
    total_budget: Optional[str] = Field(None, description="Total budget for entire trip")
    budget_per_person: Optional[str] = Field(None, description="Budget per person")
    budget_currency: Optional[str] = Field(None, description="Currency (INR, USD, EUR, etc.)")
    
    # Trip segments (for multi-leg trips)
    segments: List[TripSegment] = Field(default_factory=list, description="List of trip segments")
    
    # Single-leg trip details (fallback for simple inquiries)
    destinations: List[str] = Field(default_factory=list, description="List of destinations (single-leg)")
    start_date: Optional[str] = Field(None, description="Trip start date (single-leg)")
    end_date: Optional[str] = Field(None, description="Trip end date (single-leg)")
    duration_nights: Optional[int] = Field(None, description="Number of nights (single-leg)")
    hotel_preferences: Optional[str] = Field(None, description="Hotel preferences (single-leg)")
    meal_preferences: Optional[str] = Field(None, description="Meal preferences (single-leg)")
    activities: List[str] = Field(default_factory=list, description="Activities (single-leg)")
    
    # Travel requirements
    needs_flight: Optional[bool] = Field(None, description="Whether flights are required")
    needs_visa: Optional[bool] = Field(None, description="Whether visa assistance is needed")
    needs_insurance: Optional[bool] = Field(None, description="Whether travel insurance is needed")
    departure_city: Optional[str] = Field(None, description="Primary departure city")
    
    # Special requirements and preferences
    special_requests: Optional[str] = Field(None, description="Special requests or requirements")
    dietary_requirements: Optional[str] = Field(None, description="Dietary restrictions")
    accessibility_needs: Optional[str] = Field(None, description="Accessibility requirements")
    guide_language: Optional[str] = Field(None, description="Preferred guide language")
    travel_style: Optional[str] = Field(None, description="Travel style (luxury, budget, adventure, etc.)")
    
    # Deadline and urgency
    response_deadline: Optional[str] = Field(None, description="Response deadline")
    urgency_level: Optional[str] = Field(None, description="Urgency level (urgent, normal, flexible)")
    
    # Modification tracking (for quote updates)
    is_modification: bool = Field(False, description="Whether this is a modification request")
    original_inquiry_id: Optional[str] = Field(None, description="Original inquiry ID for modifications")
    modification_requests: List[str] = Field(default_factory=list, description="List of modification requests")
    
    # Processing metadata
    source_file: Optional[str] = Field(None, description="Source file or email")
    processing_status: Optional[str] = Field(None, description="Processing status")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    extraction_method: Optional[str] = Field(None, description="Primary extraction method used")
    confidence_score: Optional[float] = Field(None, description="Overall extraction confidence")
    
    # Generated outputs
    excel_file_path: Optional[str] = Field(None, description="Path to generated Excel quote")
    email_sent: bool = Field(False, description="Whether reply email was sent")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    
    @validator('inquiry_id', pre=True, always=True)
    def generate_inquiry_id(cls, v):
        """Generate inquiry ID if not provided"""
        if not v:
            from datetime import datetime
            return f"INQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return v
    
    @validator('inquiry_type', pre=True, always=True)
    def determine_inquiry_type(cls, v, values):
        """Auto-determine inquiry type based on segments"""
        if 'segments' in values and len(values['segments']) > 1:
            return InquiryType.MULTI_LEG
        elif values.get('is_modification', False):
            return InquiryType.MODIFICATION
        return InquiryType.SINGLE_LEG
    
    class Config:
        """Pydantic configuration"""
        extra = "forbid"
        validate_assignment = True
        use_enum_values = True


class EmailProcessingRecord(BaseModel):
    """Record for tracking processed emails"""
    
    message_id: str = Field(..., description="Email message ID")
    thread_id: Optional[str] = Field(None, description="Email thread ID")
    inquiry_id: str = Field(..., description="Generated inquiry ID")
    customer_email: str = Field(..., description="Customer email address")
    subject: str = Field(..., description="Email subject")
    processed_at: str = Field(..., description="Processing timestamp")
    excel_generated: bool = Field(False, description="Whether Excel was generated")
    reply_sent: bool = Field(False, description="Whether reply was sent")
    status: str = Field("processed", description="Processing status")
    error_message: Optional[str] = Field(None, description="Error message if any")
    file_path: Optional[str] = Field(None, description="Path to generated Excel")
    
    class Config:
        extra = "forbid"


class ProcessingConfig(BaseModel):
    """Configuration for email processing"""
    
    target_email: str = Field("shivangnvyas@gmail.com", description="Target email address")
    max_emails_per_run: int = Field(50, description="Maximum emails to process per run")
    enable_gmail: bool = Field(True, description="Enable Gmail integration")
    enable_outlook: bool = Field(True, description="Enable Outlook integration")
    auto_reply: bool = Field(True, description="Automatically send reply emails")
    backup_to_drive: bool = Field(False, description="Backup to Google Drive")
    
    class Config:
        extra = "forbid"
