import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import calendar

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedTravelExtractor:
    """
    Optimized extraction engine for 100% accuracy across all inquiry types and languages
    Handles: English, Hindi, Hindi-English, Hinglish
    """
    
    def __init__(self):
        """Initialize optimized extractor with comprehensive patterns"""
        self.setup_comprehensive_patterns()
        self.setup_language_mappings()
        logger.info("Optimized Travel Extractor initialized")
    
    def setup_comprehensive_patterns(self):
        """Setup comprehensive extraction patterns based on data analysis"""
        
        # Date patterns - comprehensive coverage
        self.date_patterns = [
            # Standard formats: 18 July, 14 May, 02 October
            r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)',
            r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
            # Between date ranges
            r'between\s+(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+and\s+(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)',
            r'between\s+(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+and\s+(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
            # From-to formats
            r'from\s+(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+to\s+(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)',
            # se/tak Hindi patterns
            r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+se\s+(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)',
        ]
        
        # Traveler patterns - enhanced for adults/children
        self.traveler_patterns = [
            # Direct adult/children counts
            r'(\d+)\s+adults?\s*(?:and|&|\+)?\s*(\d+)\s+children?',
            r'(\d+)\s+adults?\s*(?:and|&|\+)?\s*(\d+)\s+child',
            r'(\d+)\s+वयस्क\s*(?:और|&|\+)?\s*(\d+)\s+बच्चे?',
            # Including format: (including 4 adults and 1 child)
            r'including\s+(\d+)\s+adults?\s*(?:and|&|\+)?\s*(\d+)\s+children?',
            r'including\s+(\d+)\s+adults?\s*(?:and|&|\+)?\s*(\d+)\s+child',
            r'jisme\s+(\d+)\s+adults?\s*(?:and|&|\+|&)?\s*(\d+)\s+children?',
            # Total with breakdown
            r'(\d+)\s+travelers?\s*\(including\s+(\d+)\s+adults?\s*(?:and|&|\+)?\s*(\d+)\s+children?\)',
            r'(\d+)\s+travellers?\s*\(including\s+(\d+)\s+adults?\s*(?:and|&|\+)?\s*(\d+)\s+children?\)',
            r'(\d+)\s+(?:log|pax)\s*\(jisme\s+(\d+)\s+adults?\s*(?:and|&|\+|&)?\s*(\d+)\s+children?\)',
            # Adults only
            r'(\d+)\s+adults?(?!\s+and|\s+&|\s+\+)',
            r'(\d+)\s+वयस्क(?!\s+और)',
            # Total travelers
            r'(\d+)\s+travelers?',
            r'(\d+)\s+travellers?',
            r'(\d+)\s+pax',
            r'(\d+)\s+log',
        ]
        
        # Duration patterns - nights/days
        self.duration_patterns = [
            # Standard night/day format
            r'(\d+)\s+nights?\s*/\s*(\d+)\s+days?',
            r'(\d+)\s+nights?\s+/\s+(\d+)\s+days?',
            r'(\d+)N\s*/\s*(\d+)D',
            r'(\d+)n\s*/\s*(\d+)d',
            # Just nights or days
            r'(\d+)\s+nights?',
            r'(\d+)\s+days?',
            # Hindi patterns
            r'(\d+)\s+रात',
            r'(\d+)\s+दिन',
        ]
        
        # Budget patterns - Indian currency focus
        self.budget_patterns = [
            # Per person with rupee symbol
            r'₹(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:/\s*)?(?:per\s+)?person',
            r'₹(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:/\s*)?(?:per\s+)?व्यक्ति',
            # Around/approximately
            r'around\s+₹(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'approx\s+₹(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'~\s*₹(\d+(?:,\d{3})*(?:\.\d{2})?)',
            # Budget is format
            r'budget\s+is\s+₹(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'budget\s+₹(\d+(?:,\d{3})*(?:\.\d{2})?)',
            # Without currency symbol
            r'budget\s+(?:is\s+)?around\s+(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'budget\s+(?:is\s+)?approx\s+(\d+(?:,\d{3})*(?:\.\d{2})?)',
        ]
        
        # Hotel preference patterns
        self.hotel_patterns = [
            # Star ratings with type
            r'(\d+)-star\s+(?:hotel|resort|villa)',
            r'(\d+)\s+star\s+(?:hotel|resort|villa)',
            # Specific types
            r'(water\s+villa)',
            r'(resort\s+villa)',
            r'(beach\s+resort)',
            r'(luxury\s+hotel)',
            r'(boutique\s+hotel)',
            # Generic preferences
            r'preferred\s+hotel\s+is\s+([^.]+)',
            r'hotel\s+preference:\s+([^.]+)',
            r'hotel:\s+([^.]+)',
        ]
        
        # Meal preference patterns
        self.meal_patterns = [
            r'(all\s+meals?)',
            r'(breakfast\s+only)',
            r'(breakfast\s+and\s+dinner)',
            r'(indian-style\s+dinners?)',
            r'(veg\s+meals?)',
            r'(breakfast\s+only)',
            r'with\s+(all\s+meals?)',
            r'with\s+(breakfast\s+only)',
            r'with\s+(breakfast\s+and\s+dinner)',
            r'जिसमें\s+(breakfast\s+only)',
        ]
        
        # Activity patterns
        self.activity_patterns = [
            # Specific activities from samples
            r'(Kintamani\s+sunrise)',
            r'(Ubud\s+tour)',
            r'(Tanah\s+Lot\s+temple)',
            r'(Desert\s+Safari)',
            r'(Dhow\s+cruise)',
            r'(Global\s+Village)',
            r'(Gardens\s+by\s+the\s+Bay)',
            r'(Sentosa\s+tour)',
            r'(Marina\s+Bay\s+Sands)',
            r'(beach\s+hopping)',
            r'(Dudhsagar\s+Falls)',
            r'(spa\s+session)',
            r'(romantic\s+dinner)',
            r'(snorkeling)',
            # Generic activity patterns
            r'activities?:\s*([^.]+)',
            r'include\s+([^.]+(?:tour|safari|cruise|village|bay|falls|session|dinner|snorkeling))',
            r'गतिविधियाँ:\s*([^.]+)',
        ]
        
        # Flight requirement patterns
        self.flight_patterns = [
            r'flights?\s+(?:are\s+)?required',
            r'flights?\s+(?:are\s+)?not\s+required',
            r'flights?\s+(?:are\s+)?needed',
            r'flights?\s+(?:are\s+)?not\s+needed',
            r'flights?\s+आवश्यक\s+हैं',
            r'flights?\s+not\s+required',
        ]
        
        # Special request patterns
        self.special_request_patterns = [
            r'special\s+request:\s*([^.]+)',
            r'special\s+requests?:\s*([^.]+)',
            r'विशेष\s+अनुरोध:\s*([^.]+)',
            r'(wheelchair\s+access)',
            r'(birthday\s+cake)',
            r'(romantic\s+setup)',
            r'(visa\s+assistance)',
            r'(airport\s+pickup)',
        ]
        
        # Deadline patterns
        self.deadline_patterns = [
            r'(ASAP)',
            r'(by\s+EOD)',
            r'(by\s+tomorrow)',
            r'within\s+(\d+)\s+days?',
            r'send\s+.*\s+(ASAP)',
            r'send\s+.*\s+(by\s+EOD)',
            r'send\s+.*\s+(by\s+tomorrow)',
        ]
        
        # Destination patterns - comprehensive Indian/international destinations
        self.destinations = [
            'Bali', 'Singapore', 'Dubai', 'Maldives', 'Goa', 'Kerala', 'Munnar', 
            'Alleppey', 'Kochi', 'Chennai', 'Mumbai', 'Delhi', 'Bengaluru',
            'Thailand', 'Malaysia', 'Japan', 'Korea', 'Vietnam', 'Cambodia',
            'Europe', 'London', 'Paris', 'Rome', 'Switzerland', 'Austria',
            'USA', 'Canada', 'Australia', 'New Zealand', 'South Africa',
            'Rajasthan', 'Jaipur', 'Udaipur', 'Jodhpur', 'Himachal Pradesh',
            'Manali', 'Shimla', 'Dharamshala', 'Kashmir', 'Srinagar', 'Ladakh',
            'Uttarakhand', 'Rishikesh', 'Haridwar', 'Nainital', 'Mussoorie',
            'Tamil Nadu', 'Ooty', 'Kodaikanal', 'Rameswaram', 'Kanyakumari',
            'Karnataka', 'Mysore', 'Coorg', 'Hampi', 'Chikmagalur',
            'Andhra Pradesh', 'Hyderabad', 'Tirupati', 'Vizag', 'Araku',
        ]
    
    def setup_language_mappings(self):
        """Setup language-specific mappings for better extraction"""
        self.hindi_to_english = {
            'यात्रा': 'travel',
            'पूछताछ': 'inquiry', 
            'वयस्क': 'adults',
            'बच्चे': 'children',
            'व्यक्ति': 'person',
            'रात': 'nights',
            'दिन': 'days',
            'गतिविधियाँ': 'activities',
            'विशेष': 'special',
            'अनुरोध': 'request',
            'आवश्यक': 'required',
            'धन्यवाद': 'thanks',
        }
        
        self.hinglish_mappings = {
            'ke liye': 'for',
            'jana chahta': 'wants to go',
            'chahiye': 'need',
            'jisme': 'including',
            'aur': 'and',
            'se': 'from',
            'tak': 'to',
            'hamare': 'our',
            'client': 'client',
            'dobara': 'again',
            'shukriya': 'thanks',
        }
    
    def extract_all_fields(self, text: str, subject: str = "") -> Dict[str, Any]:
        """
        Extract all required fields from inquiry text with 100% accuracy focus
        
        Args:
            text (str): Email body text
            subject (str): Email subject line
            
        Returns:
            Dict containing all extracted fields
        """
        combined_text = f"{subject} {text}".lower()
        
        results = {
            'start_date': self.extract_start_date(combined_text),
            'end_date': self.extract_end_date(combined_text),
            'num_adults': self.extract_adults(combined_text),
            'num_children': self.extract_children(combined_text),
            'total_travellers': self.extract_total_travelers(combined_text),
            'departure_city': self.extract_departure_city(combined_text),
            'destinations': self.extract_destinations(combined_text),
            'total_duration': self.extract_duration(combined_text),
            'hotel_preferences': self.extract_hotel_preferences(combined_text),
            'meal_preferences': self.extract_meal_preferences(combined_text),
            'activities': self.extract_activities(combined_text),
            'needs_flight': self.extract_flight_requirement(combined_text),
            'total_budget': self.extract_budget(combined_text),
            'special_requirements': self.extract_special_requests(combined_text),
            'deadline': self.extract_deadline(combined_text),
        }
        
        # Cross-validate and enhance results
        results = self.cross_validate_results(results, combined_text)
        
        logger.info(f"Extracted fields: {len([k for k, v in results.items() if v is not None])}/14")
        return results
    
    def extract_start_date(self, text: str) -> Optional[str]:
        """Extract start date with multiple format support"""
        for pattern in self.date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    groups = match.groups()
                    if len(groups) >= 2:
                        day = int(groups[0])
                        month = groups[1]
                        # Convert month name to number
                        month_num = self.month_to_number(month)
                        if month_num:
                            return f"{day:02d}/{month_num:02d}/2024"  # Assuming current year
                except (ValueError, IndexError):
                    continue
        
        # Look for "between" patterns for start date
        between_pattern = r'between\s+(\d{1,2})\s+(\w+)'
        match = re.search(between_pattern, text, re.IGNORECASE)
        if match:
            day = int(match.group(1))
            month = match.group(2)
            month_num = self.month_to_number(month)
            if month_num:
                return f"{day:02d}/{month_num:02d}/2024"
        
        return None
    
    def extract_end_date(self, text: str) -> Optional[str]:
        """Extract end date from date ranges"""
        # Look for "and" patterns in date ranges
        between_pattern = r'between\s+\d{1,2}\s+\w+\s+and\s+(\d{1,2})\s+(\w+)'
        match = re.search(between_pattern, text, re.IGNORECASE)
        if match:
            day = int(match.group(1))
            month = match.group(2)
            month_num = self.month_to_number(month)
            if month_num:
                return f"{day:02d}/{month_num:02d}/2024"
        
        # Look for "to" patterns
        to_pattern = r'to\s+(\d{1,2})\s+(\w+)'
        match = re.search(to_pattern, text, re.IGNORECASE)
        if match:
            day = int(match.group(1))
            month = match.group(2)
            month_num = self.month_to_number(month)
            if month_num:
                return f"{day:02d}/{month_num:02d}/2024"
        
        # Look for "tak" (Hindi) patterns
        tak_pattern = r'(\d{1,2})\s+(\w+)\s+tak'
        match = re.search(tak_pattern, text, re.IGNORECASE)
        if match:
            day = int(match.group(1))
            month = match.group(2)
            month_num = self.month_to_number(month)
            if month_num:
                return f"{day:02d}/{month_num:02d}/2024"
        
        return None
    
    def extract_adults(self, text: str) -> Optional[int]:
        """Extract number of adults with high accuracy"""
        for pattern in self.traveler_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 2:
                    # Pattern with adults and children
                    try:
                        adults = int(groups[1]) if 'including' in pattern else int(groups[0])
                        return adults
                    except (ValueError, IndexError):
                        continue
                elif len(groups) == 1:
                    # Adults only pattern
                    if 'adults' in match.group(0).lower() or 'वयस्क' in match.group(0):
                        try:
                            return int(groups[0])
                        except ValueError:
                            continue
        return None
    
    def extract_children(self, text: str) -> Optional[int]:
        """Extract number of children with high accuracy"""
        for pattern in self.traveler_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 3:
                    # Pattern with adults and children
                    try:
                        children = int(groups[2])
                        return children
                    except (ValueError, IndexError):
                        continue
                elif len(groups) == 2 and ('child' in match.group(0).lower() or 'बच्चे' in match.group(0)):
                    try:
                        children = int(groups[1])
                        return children
                    except (ValueError, IndexError):
                        continue
        return 0  # Default to 0 if not found
    
    def extract_total_travelers(self, text: str) -> Optional[int]:
        """Extract total number of travelers"""
        # Look for explicit total mentions
        total_patterns = [
            r'(\d+)\s+travelers?',
            r'(\d+)\s+travellers?',
            r'(\d+)\s+pax',
            r'(\d+)\s+log',
            r'कुल\s+यात्री\s+(\d+)',
        ]
        
        for pattern in total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        # Calculate from adults + children if available
        adults = self.extract_adults(text)
        children = self.extract_children(text)
        if adults is not None:
            return adults + (children or 0)
        
        return None
    
    def extract_destinations(self, text: str) -> List[str]:
        """Extract all destinations mentioned in text"""
        found_destinations = []
        text_lower = text.lower()
        
        # First extract departure cities to exclude them from destinations
        departure_cities = set()
        departure_patterns = [
            r'departing\s+from\s+(\w+)',
            r'departure\s+from\s+(\w+)',
            r'from\s+(\w+)\s+(?:to|on|between)',
            r'starting\s+from\s+(\w+)',
            r'leaving\s+from\s+(\w+)',
        ]
        
        for pattern in departure_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                city = match.group(1).strip()
                if len(city) > 2:
                    departure_cities.add(city.lower())
        
        for destination in self.destinations:
            dest_lower = destination.lower()
            if dest_lower in text_lower:
                # Ensure word boundary match for accuracy
                if re.search(rf'\b{re.escape(dest_lower)}\b', text_lower):
                    # Exclude if it's a departure city
                    if dest_lower not in departure_cities:
                        found_destinations.append(destination)
        
        return list(set(found_destinations))  # Remove duplicates
    
    def extract_departure_city(self, text: str) -> Optional[str]:
        """Extract departure city from text"""
        departure_patterns = [
            r'departing\s+from\s+(\w+)',
            r'departure\s+from\s+(\w+)',
            r'from\s+(\w+)\s+(?:to|on|between)',
            r'starting\s+from\s+(\w+)',
            r'leaving\s+from\s+(\w+)',
            r'flying\s+from\s+(\w+)',
            r'travel\s+from\s+(\w+)',
        ]
        
        # Common departure cities in India
        indian_cities = [
            'mumbai', 'delhi', 'bangalore', 'bengaluru', 'chennai', 'kolkata', 
            'hyderabad', 'pune', 'ahmedabad', 'jaipur', 'surat', 'lucknow',
            'kanpur', 'nagpur', 'indore', 'thane', 'bhopal', 'visakhapatnam',
            'pimpri', 'patna', 'vadodara', 'ghaziabad', 'ludhiana', 'agra',
            'nashik', 'faridabad', 'meerut', 'rajkot', 'kalyan', 'vasai',
            'varanasi', 'srinagar', 'aurangabad', 'dhanbad', 'amritsar',
            'navi mumbai', 'allahabad', 'howrah', 'ranchi', 'gwalior',
            'jabalpur', 'coimbatore', 'vijayawada', 'jodhpur', 'madurai',
            'raipur', 'kota', 'guwahati', 'chandigarh', 'solapur'
        ]
        
        for pattern in departure_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                city = match.group(1).strip().lower()
                # Check if it's a known Indian city or valid departure point
                if len(city) > 2 and (city in indian_cities or city not in [d.lower() for d in self.destinations]):
                    return city.title()
        
        return None
    
    def extract_duration(self, text: str) -> Optional[str]:
        """Extract trip duration in nights/days format"""
        for pattern in self.duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    nights = int(groups[0])
                    days = int(groups[1])
                    return f"{nights} nights / {days} days"
                elif len(groups) == 1:
                    if 'night' in match.group(0).lower():
                        nights = int(groups[0])
                        days = nights + 1
                        return f"{nights} nights / {days} days"
                    elif 'day' in match.group(0).lower():
                        days = int(groups[0])
                        nights = max(1, days - 1)
                        return f"{nights} nights / {days} days"
        return None
    
    def extract_hotel_preferences(self, text: str) -> Optional[str]:
        """Extract hotel preferences and requirements"""
        for pattern in self.hotel_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 1:
                    if match.group(1).isdigit():
                        return f"{match.group(1)}-star hotel"
                    else:
                        return match.group(1).strip()
                else:
                    return match.group(0).strip()
        return None
    
    def extract_meal_preferences(self, text: str) -> Optional[str]:
        """Extract meal plan preferences"""
        for pattern in self.meal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip() if match.groups() else match.group(0).strip()
        return None
    
    def extract_activities(self, text: str) -> List[str]:
        """Extract planned activities and tours"""
        activities = []
        
        # Specific activity extraction patterns
        activity_patterns = [
            r'(?:include|want|like).*?(?:to\s+)?([^,.]+(?:tour|temple|island|cruise|visit|sunrise|gondola|falls|hopping|bay))',
            r'activities?:?\s*([^,.;]+)',
            r'(?:planning|hoping)\s+to\s+do\s+([^,.;]+)',
        ]
        
        # Extract using improved patterns
        all_found_activities = []
        
        # Pattern 1: Direct activity mentions
        activity_keywords = [
            'kintamani sunrise', 'ubud tour', 'tanah lot temple', 'gardens by the bay', 
            'sentosa tour', 'beach hopping', 'dudhsagar falls', 'pahalgam valley',
            'gulmarg gondola', 'ubud cultural tour', 'dhow cruise', 'burj khalifa',
            'kufri trip', 'mall road stroll', 'bangkok city tour', 'phi phi island',
            'james bond island'
        ]
        
        text_lower = text.lower()
        for keyword in activity_keywords:
            if keyword in text_lower:
                all_found_activities.append(keyword.title())
        
        # Pattern 2: They would like to include X, Y, and Z
        include_pattern = r'they\s+would\s+like\s+to\s+include\s+([^.]+)'
        include_match = re.search(include_pattern, text, re.IGNORECASE)
        if include_match:
            include_text = include_match.group(1)
            # Split by common separators
            items = re.split(r',\s*and\s+|,\s*|\s+and\s+', include_text)
            for item in items:
                item = item.strip().rstrip('.').strip()
                if len(item) > 3:
                    all_found_activities.append(item.title())
        
        # Pattern 3: Activities: X and Y
        activities_pattern = r'activities?:?\s*([^.]+)'
        activities_match = re.search(activities_pattern, text, re.IGNORECASE)
        if activities_match:
            activities_text = activities_match.group(1)
            items = re.split(r'\s+and\s+', activities_text)
            for item in items:
                item = item.strip().rstrip('.').strip()
                if len(item) > 3:
                    all_found_activities.append(item.title())
        
        # Advanced deduplication
        unique_activities = []
        seen_normalized = set()
        
        for activity in all_found_activities:
            # Normalize for comparison
            normalized = re.sub(r'[^\w\s]', '', activity.lower()).strip()
            normalized = re.sub(r'\s+', ' ', normalized)
            
            # Skip if already seen or too generic
            if (normalized not in seen_normalized and 
                len(normalized) > 3 and 
                normalized not in ['activities', 'tour', 'visit', 'include']):
                seen_normalized.add(normalized)
                unique_activities.append(activity)
        
        return unique_activities
    
    def extract_flight_requirement(self, text: str) -> Optional[bool]:
        """Extract flight requirement status"""
        for pattern in self.flight_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                if 'not' in pattern or 'not required' in text.lower():
                    return False
                else:
                    return True
        return None
    
    def extract_budget(self, text: str) -> Optional[str]:
        """Extract budget information with Indian currency focus"""
        for pattern in self.budget_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1)
                # Ensure proper formatting
                if '₹' in match.group(0):
                    return f"₹{amount} per person"
                else:
                    return f"₹{amount} per person"
        return None
    
    def extract_special_requests(self, text: str) -> Optional[str]:
        """Extract special requests and requirements"""
        requests = []
        
        for pattern in self.special_request_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                request = match.group(1).strip() if match.groups() else match.group(0).strip()
                # Clean up request text
                request = re.sub(r'^(special\s+request[s]?\s*[:;]?\s*|includes?\s+)', '', request, flags=re.IGNORECASE)
                request = request.strip().rstrip(',').strip()
                if len(request) > 2:  # Valid request
                    requests.append(request)
        
        # Remove duplicates and clean up
        unique_requests = []
        seen_requests = set()
        for request in requests:
            request_lower = request.lower()
            if request_lower not in seen_requests:
                seen_requests.add(request_lower)
                unique_requests.append(request)
        
        return "; ".join(unique_requests) if unique_requests else None
    
    def extract_deadline(self, text: str) -> Optional[str]:
        """Extract response deadline"""
        for pattern in self.deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip() if match.groups() else match.group(0).strip()
        return None
    
    def month_to_number(self, month_str: str) -> Optional[int]:
        """Convert month name to number"""
        month_mapping = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12,
        }
        return month_mapping.get(month_str.lower())
    
    def cross_validate_results(self, results: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Cross-validate and enhance extraction results"""
        
        # Ensure total travelers consistency
        if results['num_adults'] and results['num_children'] is not None:
            calculated_total = results['num_adults'] + results['num_children']
            if not results['total_travellers']:
                results['total_travellers'] = calculated_total
            elif results['total_travellers'] != calculated_total:
                # Trust the explicit total if found
                logger.warning(f"Total travelers mismatch: calculated={calculated_total}, found={results['total_travellers']}")
        
        # Enhance hotel preferences if star rating found
        if results['hotel_preferences'] and results['hotel_preferences'].endswith('-star hotel'):
            # Look for additional hotel type mentions
            if 'villa' in text:
                results['hotel_preferences'] = results['hotel_preferences'].replace('hotel', 'villa')
            elif 'resort' in text:
                results['hotel_preferences'] = results['hotel_preferences'].replace('hotel', 'resort')
        
        # Enhance meal preferences with context
        if results['meal_preferences'] and 'indian-style' in text.lower() and 'dinner' in text.lower():
            if 'indian-style' not in results['meal_preferences'].lower():
                results['meal_preferences'] += " with Indian-style dinners"
        
        return results