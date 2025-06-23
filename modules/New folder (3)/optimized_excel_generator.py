import logging
from pathlib import Path
from typing import Dict, Any, List
import xlsxwriter
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedExcelGenerator:
    """
    Optimized Excel generator for complete travel inquiry reports
    Generates all required fields from schema with professional formatting
    """
    
    def __init__(self, output_dir: str = "output"):
        """Initialize Excel generator"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info("Optimized Excel Generator initialized")
    
    def generate_inquiry_report(self, processed_data: Dict[str, Any]) -> str:
        """
        Generate comprehensive Excel report for processed inquiry
        
        Args:
            processed_data (Dict): Processed inquiry data
            
        Returns:
            str: Path to generated Excel file
        """
        inquiry_id = processed_data.get('inquiry_id', 'UNKNOWN')
        inquiry_type = processed_data.get('inquiry_type', {}).get('type', 'UNKNOWN')
        
        filename = f"Travel_Inquiry_{inquiry_id}_{inquiry_type}.xlsx"
        filepath = self.output_dir / filename
        
        # Create workbook and worksheet
        workbook = xlsxwriter.Workbook(str(filepath))
        worksheet = workbook.add_worksheet('Inquiry Details')
        
        # Setup formatting
        formats = self.setup_formats(workbook)
        
        # Generate report based on inquiry type
        if inquiry_type == 'MULTI_LEG':
            self.generate_multi_leg_report(worksheet, processed_data, formats)
        elif inquiry_type == 'MODIFICATION':
            self.generate_modification_report(worksheet, processed_data, formats)
        else:
            self.generate_single_leg_report(worksheet, processed_data, formats)
        
        workbook.close()
        logger.info(f"Excel report generated: {filepath}")
        return str(filepath)
    
    def setup_formats(self, workbook) -> Dict[str, Any]:
        """Setup professional Excel formatting"""
        return {
            'title': workbook.add_format({
                'bold': True, 'font_size': 16, 'align': 'center',
                'valign': 'vcenter', 'bg_color': '#2E75B6', 'font_color': 'white'
            }),
            'header': workbook.add_format({
                'bold': True, 'font_size': 12, 'bg_color': '#D9E2F3',
                'align': 'left', 'valign': 'vcenter', 'border': 1
            }),
            'label': workbook.add_format({
                'bold': True, 'align': 'right', 'valign': 'vcenter',
                'bg_color': '#F2F2F2', 'border': 1
            }),
            'value': workbook.add_format({
                'align': 'left', 'valign': 'vcenter', 'border': 1,
                'text_wrap': True
            }),
            'currency': workbook.add_format({
                'align': 'left', 'valign': 'vcenter', 'border': 1,
                'bg_color': '#E2EFDA'
            }),
            'date': workbook.add_format({
                'align': 'center', 'valign': 'vcenter', 'border': 1,
                'bg_color': '#FFF2CC'
            }),
            'important': workbook.add_format({
                'bold': True, 'align': 'left', 'valign': 'vcenter',
                'border': 1, 'bg_color': '#FFE6E6'
            })
        }
    
    def generate_single_leg_report(self, worksheet, data: Dict[str, Any], formats: Dict[str, Any]):
        """Generate report for single destination inquiry"""
        
        # Set column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 40)
        
        row = 0
        
        # Title
        worksheet.merge_range(f'A{row+1}:B{row+1}', 'SINGLE DESTINATION TRAVEL INQUIRY', formats['title'])
        row += 2
        
        # Basic Information Section
        row = self.add_section_header(worksheet, row, "BASIC INFORMATION", formats)
        row = self.add_field(worksheet, row, "Inquiry ID", data.get('inquiry_id', 'N/A'), formats)
        row = self.add_field(worksheet, row, "Inquiry Type", data.get('inquiry_type', {}).get('type', 'N/A'), formats)
        row = self.add_field(worksheet, row, "Language", data.get('language_info', {}).get('primary_language', 'N/A'), formats)
        row = self.add_field(worksheet, row, "Customer Email", data.get('customer_details', {}).get('email', 'N/A'), formats)
        row += 1
        
        # Travel Details Section
        row = self.add_section_header(worksheet, row, "TRAVEL DETAILS", formats)
        
        # Extract fields from nested structure
        traveler_details = data.get('traveler_details', {})
        date_details = data.get('date_details', {})
        location_details = data.get('location_details', {})
        preference_details = data.get('preference_details', {})
        budget_details = data.get('budget_details', {})
        
        row = self.add_field(worksheet, row, "Start Date", date_details.get('start_date'), formats, field_type='date')
        row = self.add_field(worksheet, row, "End Date", date_details.get('end_date'), formats, field_type='date')
        row = self.add_field(worksheet, row, "Total Duration", date_details.get('duration'), formats)
        row = self.add_field(worksheet, row, "Departure City", data.get('departure_city', 'Not specified'), formats)
        row = self.add_field(worksheet, row, "Destination(s)", ", ".join(location_details.get('all_destinations', [])), formats)
        row += 1
        
        # Traveler Information Section
        row = self.add_section_header(worksheet, row, "TRAVELER INFORMATION", formats)
        row = self.add_field(worksheet, row, "Total Travelers", traveler_details.get('total_travelers'), formats)
        row = self.add_field(worksheet, row, "Number of Adults", traveler_details.get('adults'), formats)
        row = self.add_field(worksheet, row, "Number of Children", traveler_details.get('children'), formats)
        row += 1
        
        # Accommodation & Preferences Section
        row = self.add_section_header(worksheet, row, "ACCOMMODATION & PREFERENCES", formats)
        row = self.add_field(worksheet, row, "Hotel Type", preference_details.get('hotel', 'N/A'), formats)
        row = self.add_field(worksheet, row, "Meal Plan", preference_details.get('meals', 'N/A'), formats)
        row = self.add_field(worksheet, row, "Planned Activities", ", ".join(preference_details.get('activities', [])), formats)
        row = self.add_field(worksheet, row, "Flight Required", "Yes" if preference_details.get('flight_required') else "No", formats)
        row += 1
        
        # Budget & Special Requests Section
        row = self.add_section_header(worksheet, row, "BUDGET & SPECIAL REQUESTS", formats)
        row = self.add_field(worksheet, row, "Total Budget", budget_details.get('amount', 'N/A'), formats, field_type='currency')
        row = self.add_field(worksheet, row, "Special Requests", preference_details.get('special_requirements', 'N/A'), formats, field_type='important')
        row = self.add_field(worksheet, row, "Deadline", data.get('deadline', 'N/A'), formats, field_type='important')
        
        # Add processing timestamp
        row += 2
        worksheet.write(f'A{row+1}', 'Report Generated:', formats['label'])
        worksheet.write(f'B{row+1}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), formats['date'])
    
    def generate_multi_leg_report(self, worksheet, data: Dict[str, Any], formats: Dict[str, Any]):
        """Generate report for multi-destination inquiry"""
        
        # Set column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 40)
        
        row = 0
        
        # Title
        worksheet.merge_range(f'A{row+1}:B{row+1}', 'MULTI-DESTINATION TRAVEL INQUIRY', formats['title'])
        row += 2
        
        # Basic Information Section
        row = self.add_section_header(worksheet, row, "BASIC INFORMATION", formats)
        row = self.add_field(worksheet, row, "Inquiry ID", data.get('inquiry_id', 'N/A'), formats)
        row = self.add_field(worksheet, row, "Inquiry Type", data.get('inquiry_type', {}).get('type', 'N/A'), formats)
        row = self.add_field(worksheet, row, "Language", data.get('language_info', {}).get('primary_language', 'N/A'), formats)
        row = self.add_field(worksheet, row, "Customer Email", data.get('customer_details', {}).get('email', 'N/A'), formats)
        row += 1
        
        # Overall Travel Details
        row = self.add_section_header(worksheet, row, "OVERALL TRAVEL DETAILS", formats)
        
        traveler_details = data.get('traveler_details', {})
        date_details = data.get('date_details', {})
        location_details = data.get('location_details', {})
        budget_details = data.get('budget_details', {})
        
        row = self.add_field(worksheet, row, "Total Duration", date_details.get('duration'), formats)
        row = self.add_field(worksheet, row, "All Destinations", ", ".join(location_details.get('all_destinations', [])), formats)
        row = self.add_field(worksheet, row, "Total Travelers", traveler_details.get('total_travelers'), formats)
        row = self.add_field(worksheet, row, "Adults", traveler_details.get('adults'), formats)
        row = self.add_field(worksheet, row, "Children", traveler_details.get('children'), formats)
        row = self.add_field(worksheet, row, "Total Budget", budget_details.get('amount', 'N/A'), formats, field_type='currency')
        row += 1
        
        # Location-Specific Details (matching user's expected format)
        legs = location_details.get('legs', [])
        if legs:
            row = self.add_section_header(worksheet, row, "LOCATION-SPECIFIC DETAILS", formats)
            
            for i, leg in enumerate(legs, 1):
                row += 1
                
                # Location header
                dest_name = leg.get("destination", "Unknown").upper()
                worksheet.write(f'A{row+1}', f'LOCATION: {dest_name}', formats['header'])
                row += 1
                
                # Location details with proper formatting
                duration = leg.get('duration', 'Not specified')
                hotel_prefs = leg.get('hotel', 'Not specified')
                activities = leg.get('activities', [])
                activities_text = ', '.join(activities) if activities else 'Not specified'
                
                # Meal preferences and special requests combined
                meals = leg.get('meals', '')
                transport = leg.get('transportation', '')
                special_reqs = []
                if meals:
                    special_reqs.append(meals)
                if transport:
                    special_reqs.append(f"Transportation: {transport}")
                
                special_text = ', '.join(special_reqs) if special_reqs else 'Not specified'
                
                row = self.add_field(worksheet, row, "Duration:", duration, formats)
                row = self.add_field(worksheet, row, "Hotel Preferences:", hotel_prefs, formats)
                row = self.add_field(worksheet, row, "Activities:", activities_text, formats)
                row = self.add_field(worksheet, row, "Special Requirements:", special_text, formats)
                
                row += 1  # Add space between locations
        
        # Add processing timestamp
        row += 2
        worksheet.write(f'A{row+1}', 'Report Generated:', formats['label'])
        worksheet.write(f'B{row+1}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), formats['date'])
    
    def generate_modification_report(self, worksheet, data: Dict[str, Any], formats: Dict[str, Any]):
        """Generate report for modification inquiry"""
        
        # Set column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 40)
        
        row = 0
        
        # Title
        worksheet.merge_range(f'A{row+1}:B{row+1}', 'TRAVEL INQUIRY MODIFICATION', formats['title'])
        row += 2
        
        # Basic Information Section
        row = self.add_section_header(worksheet, row, "MODIFICATION REQUEST", formats)
        row = self.add_field(worksheet, row, "Inquiry ID", data.get('inquiry_id', 'N/A'), formats)
        row = self.add_field(worksheet, row, "Inquiry Type", "MODIFICATION", formats, field_type='important')
        row = self.add_field(worksheet, row, "Language", data.get('language_info', {}).get('primary_language', 'N/A'), formats)
        row = self.add_field(worksheet, row, "Customer Email", data.get('customer_details', {}).get('email', 'N/A'), formats)
        row += 1
        
        # Modification Details
        row = self.add_section_header(worksheet, row, "REQUESTED CHANGES", formats)
        
        modification_details = data.get('modification_details', {})
        changes = modification_details.get('changes', [])
        
        if changes:
            for i, change in enumerate(changes, 1):
                row = self.add_field(worksheet, row, f"Change {i}", change, formats, field_type='important')
        else:
            # Extract changes from general details if not structured
            preference_details = data.get('preference_details', {})
            if preference_details.get('special_requirements'):
                row = self.add_field(worksheet, row, "Modifications", preference_details.get('special_requirements'), formats, field_type='important')
        
        row = self.add_field(worksheet, row, "Deadline", data.get('deadline', 'N/A'), formats, field_type='important')
        
        # Add processing timestamp
        row += 2
        worksheet.write(f'A{row+1}', 'Report Generated:', formats['label'])
        worksheet.write(f'B{row+1}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), formats['date'])
    
    def add_section_header(self, worksheet, row: int, title: str, formats: Dict[str, Any]) -> int:
        """Add a section header"""
        worksheet.merge_range(f'A{row+1}:B{row+1}', title, formats['header'])
        return row + 1
    
    def add_field(self, worksheet, row: int, label: str, value: Any, formats: Dict[str, Any], field_type: str = 'normal') -> int:
        """Add a field with label and value"""
        
        # Handle None values
        if value is None:
            value = 'Not specified'
        elif isinstance(value, (list, tuple)) and not value:
            value = 'Not specified'
        elif isinstance(value, str) and not value.strip():
            value = 'Not specified'
        
        # Select appropriate format
        value_format = formats['value']
        if field_type == 'currency':
            value_format = formats['currency']
        elif field_type == 'date':
            value_format = formats['date']
        elif field_type == 'important':
            value_format = formats['important']
        
        worksheet.write(f'A{row+1}', label, formats['label'])
        worksheet.write(f'B{row+1}', str(value), value_format)
        
        return row + 1