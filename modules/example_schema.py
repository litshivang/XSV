from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class InquiryType(str, Enum):
    SINGLE_LEG   = "single_leg"
    MULTI_LEG    = "multi_leg"
    MODIFICATION = "modification"


class TripInquiry(BaseModel):
    """Shared fields for ANY trip inquiry"""
    inquiry_type: InquiryType
    total_travellers: Optional[int]     = Field(None, description="Total number of travelers")
    num_adults: Optional[int]         = Field(None, description="Number of adult travelers")
    num_children: Optional[int]       = Field(None, description="Number of child travelers")
    destinations: List[str]           = Field(default_factory=list, description="List of travel destinations")
    start_date: Optional[str]         = Field(None, description="Trip start date")
    end_date: Optional[str]           = Field(None, description="Trip end date")
    total_duration: Optional[int]    = Field(None, description="Number of nights for the trip")
    hotel_preferences: Optional[str]  = Field(None, description="Hotel category preferences")
    meal_preferences: Optional[str]   = Field(None, description="Meal plan preferences")
    activities: List[str]             = Field(default_factory=list, description="List of desired activities")
    needs_flight: Optional[bool]      = Field(None, description="Whether flights are required")
    total_budget: Optional[str]             = Field(None, description="total_budget information")
    special_requirements: Optional[str]   = Field(None, description="Special requests or requirements")
    deadline: Optional[str]           = Field(None, description="Customer response deadline")


class LegDetail(BaseModel):
    """Per-location details for a multi-leg itinerary"""
    location: str                                   = Field(..., description="City or region name")
    total_duration: Optional[int]    = Field(None, description="Nights in this leg")
    hotel_preferences: Optional[str]  = Field(None, description="Hotel category for this leg")
    meal_preferences: Optional[str]   = Field(None, description="Meal plan for this leg")
    activities: List[str]             = Field(default_factory=list, description="Activities in this leg")
    special_requirements: Optional[str]   = Field(None, description="Special requests for this leg")


class SingleLegInquiry(TripInquiry):
    inquiry_type: InquiryType = Field(InquiryType.SINGLE_LEG, const=True)
    # all data lives in the base fields (destinations will contain one entry)


class MultiLegInquiry(TripInquiry):
    inquiry_type: InquiryType         = Field(InquiryType.MULTI_LEG, const=True)
    legs: List[LegDetail]             = Field(..., description="Detailed per-location legs")
    # You may leave the base TripInquiry.destinations empty or duplicate from legs


class ModificationDetail(BaseModel):
    """Describes a single change in a modification request"""
    field_changed: str                 = Field(..., description="Which field or leg was modified")
    new_value: str                     = Field(..., description="The updated value or instruction")


class ModificationInquiry(BaseModel):
    inquiry_type: InquiryType          = Field(InquiryType.MODIFICATION, const=True)
    original_inquiry_id: str           = Field(..., description="Reference to the original inquiry")
    changes: List[ModificationDetail]  = Field(..., description="List of requested changes")
    deadline: Optional[str]            = Field(None, description="By when to resend the updated quote")
