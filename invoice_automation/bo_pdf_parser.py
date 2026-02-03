"""
Enhanced PDF parser for Business Order (BO) documents
Extracts relevant invoice data from PDF files
"""

import re
from typing import Dict, List, Optional, Tuple


class BOPDFParser:
    """Parse Business Order PDFs and extract invoice-relevant data"""
    
    def __init__(self, extracted_text: str):
        """
        Initialize parser with extracted PDF text
        
        Args:
            extracted_text: Raw text extracted from PDF
        """
        self.text = extracted_text
        self.lines = extracted_text.split('\n')
    
    def extract_all_data(self) -> Dict:
        """Extract all BO data"""
        return {
            'bo_no': self.extract_bo_number(),
            'client_name': self.extract_client_name(),
            'client_trn': self.extract_trn_number(),
            'descriptions': self.extract_descriptions(),
            'quantities': self.extract_quantities(),
            'rates': self.extract_rates(),
            'raw_text': self.text
        }
    
    def extract_bo_number(self) -> Optional[str]:
        """
        Extract BO/PO/Schedule number
        Looks for patterns like: PD25|2041|4, BONumber:, ScheduleNo:, PONo:, OrderNo:
        """
        # Pattern 1: PD25|2041|4 style (order format from screenshot)
        match = re.search(r'(?:PD|PO|BO|Schedule)\d{2}\|?\d+\|?\d+', self.text, re.IGNORECASE)
        if match:
            return match.group().strip()
        
        # Pattern 2: Key-value format
        patterns = [
            r'(?:Order\s*No|BO\s*No|PO\s*No|Schedule\s*No)[:\s]+([A-Za-z0-9\-|]+)',
            r'(?:BONumber|PONumber|ScheduleNumber)[:\s]+([A-Za-z0-9\-|]+)',
            r'(?:Order\s*Number)[:\s]+([A-Za-z0-9\-|]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_client_name(self) -> Optional[str]:
        """
        Extract client/customer name
        Looks for patterns like: Client:, Customer:, Attention:, Recipient:
        """
        patterns = [
            r'(?:Attention|Client|Customer|Recipient|Company)[:\s]+([^\n]+)',
            r'(?:Attention|Client|Customer)[:\s]+([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Clean up common artifacts
                value = re.sub(r'\s{2,}', ' ', value)
                if value and len(value) < 150:  # Reasonable length for client name
                    return value
        
        return None
    
    def extract_trn_number(self) -> Optional[str]:
        """
        Extract TRN (Tax Registration Number) / VAT number
        Looks for patterns like: TRN, VAT ID, VAT Registration, Tax ID
        """
        patterns = [
            r'(?:VAT\s*(?:Registration|No|Number|ID)|TRN|Tax\s*(?:ID|Registration))[:\s]+([0-9\s\-]+)',
            r'(?:TRN|VAT)[:\s]+([0-9\s\-]+)',
            r'VAT\s*REGISTRATION\s*No[.:]?\s*([0-9\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Extract only numbers
                numbers = re.sub(r'\D', '', value)
                if numbers and len(numbers) >= 8:  # TRN/VAT usually have many digits
                    return numbers
        
        return None
    
    def extract_descriptions(self) -> List[str]:
        """
        Extract item descriptions from PDF
        Looks for section like "Details", "Items", or table with descriptions
        """
        descriptions = []
        
        # Look for patterns like "Mixed Placement" or "Clickable In-Game Banners"
        # This could be in a table or list format
        detail_patterns = [
            r'(?:Mixed\s+Placement|Clickable|Banner|Video|Impression|Campaign|Ad\s+(?:Space|Placement))[^\n]*',
            r'([A-Z][A-Za-z\s]{10,}(?:Placement|Banner|Video|Campaign|Ad))[^\n]*',
        ]
        
        for pattern in detail_patterns:
            matches = re.findall(pattern, self.text)
            for match in matches:
                desc = match.strip()
                if desc and len(desc) < 200:  # Reasonable description length
                    if desc not in descriptions:
                        descriptions.append(desc)
        
        # Look for "Details" section followed by content
        details_section = re.search(r'Details[:\s]+([^\n]+(?:\n[^\n]*){0,5})', self.text, re.IGNORECASE)
        if details_section:
            detail_text = details_section.group(1)
            # Extract meaningful portions
            detail_lines = [line.strip() for line in detail_text.split('\n') if line.strip()]
            for line in detail_lines[:5]:  # Limit to first 5 lines
                if line and len(line) > 5 and line not in descriptions:
                    descriptions.append(line)
        
        # Look in table rows (detect by looking for numeric values)
        lines_with_numbers = []
        for line in self.lines:
            if re.search(r'\d+', line) and len(line) > 20:
                lines_with_numbers.append(line)
        
        # Try to extract description from lines that might be table rows
        for line in lines_with_numbers:
            # Remove leading numbers and common separators
            cleaned = re.sub(r'^[\d\-\|]+\s*', '', line)
            if cleaned and len(cleaned) > 10 and any(c.isalpha() for c in cleaned):
                cleaned = cleaned.strip()
                if cleaned not in descriptions and len(cleaned) < 200:
                    descriptions.append(cleaned)
        
        return descriptions[:5]  # Return top 5 descriptions
    
    def extract_quantities(self) -> List[float]:
        """
        Extract quantities/volumes
        Looks for patterns like: Volume:, Quantity:, QTY, Units
        """
        quantities = []
        
        # Look for "Volume", "Quantity", "Units" followed by numbers
        patterns = [
            r'(?:Volume|Quantity|QTY|Units?)[:\s]+(\d+(?:,\d{3})*(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, self.text, re.IGNORECASE)
            for match in matches:
                try:
                    # Remove commas and convert to float
                    value = float(match.replace(',', ''))
                    if value > 0:
                        quantities.append(value)
                except ValueError:
                    pass
        
        # Look in lines that look like table data (contain multiple numbers)
        for line in self.lines:
            # Extract numbers that might be quantities (usually medium-sized numbers)
            numbers = re.findall(r'\b(\d+(?:,\d{3})*)\b', line)
            for num_str in numbers:
                try:
                    num = float(num_str.replace(',', ''))
                    # Filter: quantities are usually between 1 and 100,000
                    if 1 <= num <= 100000 and num not in quantities:
                        quantities.append(num)
                except ValueError:
                    pass
        
        return quantities[:10]  # Return top 10 quantities
    
    def extract_rates(self) -> List[float]:
        """
        Extract unit rates/unit costs
        Looks for patterns like: Rate:, Unit Cost:, Price:, Amount:
        """
        rates = []
        
        # Look for "Rate", "Unit Cost", "Price" followed by numbers with currency
        patterns = [
            r'(?:Rate|Unit\s*Cost|Unit\s*Price|Price)[:\s]+(?:\$|USD\s*)?(\d+(?:,\d{3})*(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, self.text, re.IGNORECASE)
            for match in matches:
                try:
                    value = float(match.replace(',', ''))
                    if value > 0:
                        rates.append(value)
                except ValueError:
                    pass
        
        # Look for currency amounts that might be rates
        currency_patterns = [
            r'\$\s*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'USD\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        ]
        
        for pattern in currency_patterns:
            matches = re.findall(pattern, self.text)
            for match in matches:
                try:
                    value = float(match.replace(',', ''))
                    if 1 <= value <= 1000000 and value not in rates:  # Reasonable rate range
                        rates.append(value)
                except ValueError:
                    pass
        
        return rates[:10]  # Return top 10 rates
    
    def extract_line_items(self) -> List[Dict]:
        """
        Extract complete line items (description, quantity, rate) together
        """
        items = []
        descriptions = self.extract_descriptions()
        quantities = self.extract_quantities()
        rates = self.extract_rates()
        
        # Pair them together
        max_items = max(len(descriptions), len(quantities), len(rates))
        for i in range(max_items):
            item = {
                'description': descriptions[i] if i < len(descriptions) else '',
                'quantity': quantities[i] if i < len(quantities) else None,
                'rate': rates[i] if i < len(rates) else None,
            }
            items.append(item)
        
        return items
