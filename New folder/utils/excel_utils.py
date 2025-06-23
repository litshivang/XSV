from pathlib import Path
import xlsxwriter

class ExcelGenerator:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_inquiry_report(self, processed_data: dict) -> str:
        inquiry_id = processed_data.get('inquiry_id', 'UNKNOWN')
        filename = f"Inquiry_{inquiry_id}.xlsx"
        filepath = self.output_dir / filename

        workbook = xlsxwriter.Workbook(str(filepath))
        worksheet = workbook.add_worksheet('Inquiry Summary')

        bold = workbook.add_format({'bold': True})

        # Basic Header
        worksheet.write('A1', 'Inquiry ID', bold)
        worksheet.write('B1', inquiry_id)

        worksheet.write('A2', 'Type', bold)
        worksheet.write('B2', processed_data.get('inquiry_type', {}).get('type', ''))

        worksheet.write('A3', 'Primary Language', bold)
        worksheet.write('B3', processed_data.get('language_info', {}).get('primary_language', ''))

        worksheet.write('A4', 'Sender', bold)
        worksheet.write('B4', processed_data.get('basic_info', {}).get('sender', ''))

        # Add more structured fields as needed

        workbook.close()
        return str(filepath)
