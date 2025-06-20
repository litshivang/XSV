import logging
from pathlib import Path
from typing import Dict, Any

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


class ExcelGenerator:
    """
    Generate user-friendly Excel reports for travel inquiries
    """
    
    def __init__(self):
        """Initialize Excel generator"""
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_inquiry_report(self, processed_data: Dict[str, Any]) -> str:
        """
        Generate Excel report for processed inquiry
        
        Args:
            processed_data (Dict): Processed inquiry data
            
        Returns:
            str: Path to generated Excel file
        """
        try:
            inquiry_id = processed_data.get('inquiry_id', 'UNKNOWN')
            filename = f"Travel_Inquiry_{inquiry_id}.xlsx"
            filepath = self.output_dir / filename
            
            # Create workbook and worksheet
            import xlsxwriter
            workbook = xlsxwriter.Workbook(str(filepath))
            worksheet = workbook.add_worksheet('Travel Inquiry Details')
            
            # Define formats
            bold_format = workbook.add_format({'bold': True, 'font_size': 12})
            header_format = workbook.add_format({
                'bold': True, 
                'font_size': 14, 
                'bg_color': '#4F81BD',
                'font_color': 'white'
            })
            location_format = workbook.add_format({
                'bold': True, 
                'font_size': 13, 
                'bg_color': '#B8CCE4'
            })
            
            row = 0
            
            # Header
            worksheet.write(row, 0, 'TRAVEL INQUIRY DETAILS', header_format)
            worksheet.merge_range(row, 0, row, 3, 'TRAVEL INQUIRY DETAILS', header_format)
            row += 2
            
            # Basic Information
            basic_info = processed_data.get('basic_info', {})
            
            worksheet.write(row, 0, 'INQUIRY ID:', bold_format)
            worksheet.write(row, 1, inquiry_id)
            row += 1
            
            worksheet.write(row, 0, 'INQUIRY TYPE:', bold_format)
            worksheet.write(row, 1, processed_data.get('inquiry_type', {}).get('type', 'Unknown'))
            row += 1
            
            worksheet.write(row, 0, 'LANGUAGE:', bold_format)
            worksheet.write(row, 1, processed_data.get('language_info', {}).get('primary_language', 'Unknown'))
            row += 1
            
            worksheet.write(row, 0, 'SENDER:', bold_format)
            worksheet.write(row, 1, basic_info.get('sender', 'Unknown'))
            row += 1
            
            worksheet.write(row, 0, 'CONTACT EMAIL:', bold_format)
            worksheet.write(row, 1, basic_info.get('contact_email', {}).get('value', 'Not provided'))
            row += 1
            
            worksheet.write(row, 0, 'PHONE:', bold_format)
            worksheet.write(row, 1, basic_info.get('phone', {}).get('value', 'Not provided'))
            row += 2
            
            # General Details
            worksheet.write(row, 0, 'TOTAL TRAVELERS:', bold_format)
            travelers_info = basic_info.get('travelers', {})
            worksheet.write(row, 1, travelers_info.get('value', 'Not specified'))
            row += 1
            
            worksheet.write(row, 0, 'TOTAL BUDGET:', bold_format)
            budget_info = basic_info.get('budget', {})
            worksheet.write(row, 1, budget_info.get('value', 'Not specified'))
            row += 1
            
            worksheet.write(row, 0, 'TOTAL DURATION:', bold_format)
            duration_info = basic_info.get('duration', {})
            worksheet.write(row, 1, duration_info.get('value', 'Not specified'))
            row += 1
            
            worksheet.write(row, 0, 'DESTINATIONS:', bold_format)
            dest_info = basic_info.get('destinations', {})
            destinations = ', '.join(dest_info.get('value', [])) if dest_info.get('value') else 'Not specified'
            worksheet.write(row, 1, destinations)
            row += 2
            
            # Location-specific details
            location_details = processed_data.get('location_details', {})
            
            if location_details.get('type') == 'MULTI_LEG':
                worksheet.write(row, 0, 'LOCATION-SPECIFIC DETAILS:', location_format)
                worksheet.merge_range(row, 0, row, 3, 'LOCATION-SPECIFIC DETAILS:', location_format)
                row += 2
                
                location_specific = location_details.get('location_specific', {})
                
                for location, details in location_specific.items():
                    # Location header
                    worksheet.write(row, 0, f'LOCATION: {location.upper()}', location_format)
                    worksheet.merge_range(row, 0, row, 3, f'LOCATION: {location.upper()}', location_format)
                    row += 1
                    
                    worksheet.write(row, 1, 'Duration:', bold_format)
                    worksheet.write(row, 2, details.get('duration', {}).get('value', 'Not specified'))
                    row += 1
                    
                    worksheet.write(row, 1, 'Hotel Preferences:', bold_format)
                    hotel_prefs = details.get('hotel_preferences', {}).get('value', [])
                    worksheet.write(row, 2, ', '.join(hotel_prefs) if hotel_prefs else 'Not specified')
                    row += 1
                    
                    worksheet.write(row, 1, 'Activities:', bold_format)
                    activities = details.get('activities', {}).get('value', [])
                    worksheet.write(row, 2, ', '.join(activities) if activities else 'Not specified')
                    row += 1
                    
                    worksheet.write(row, 1, 'Special Requirements:', bold_format)
                    special_reqs = details.get('special_requirements', {}).get('value', [])
                    worksheet.write(row, 2, ', '.join(special_reqs) if special_reqs else 'Not specified')
                    row += 2
            
            else:
                # Single leg details
                worksheet.write(row, 0, 'GENERAL PREFERENCES:', bold_format)
                row += 1
                
                worksheet.write(row, 0, 'Hotel Preferences:', bold_format)
                hotel_prefs = basic_info.get('hotel_preferences', {}).get('value', [])
                worksheet.write(row, 1, ', '.join(hotel_prefs) if hotel_prefs else 'Not specified')
                row += 1
                
                worksheet.write(row, 0, 'Activities:', bold_format)
                activities = basic_info.get('activities', {}).get('value', [])
                worksheet.write(row, 1, ', '.join(activities) if activities else 'Not specified')
                row += 1
                
                worksheet.write(row, 0, 'Special Requirements:', bold_format)
                special_reqs = basic_info.get('special_requirements', {}).get('value', [])
                worksheet.write(row, 1, ', '.join(special_reqs) if special_reqs else 'Not specified')
                row += 2            
            
            # Adjust column widths
            worksheet.set_column(0, 0, 25)
            worksheet.set_column(1, 1, 40)
            worksheet.set_column(2, 2, 30)
            worksheet.set_column(3, 3, 20)
            
            workbook.close()
            
            logger.info(f"Excel report generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating Excel report: {e}")
            return None
