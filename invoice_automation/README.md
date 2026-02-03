# Invoice Template Automation

A Python-based template automation system for modifying Yazle Invoice Template with a powerful Streamlit-based GUI. Now with advanced BO (Business Order) data mapping and extraction capabilities.

## Features

- **Template-based Invoice Generation**: Modify specific invoice fields without touching the template structure
- **User-friendly Web UI**: Streamlit-based interface with modern UX
- **Business Order (BO) Data Mapping**: Automatically extract and populate fields from:
  - PDF documents (with intelligent parsing)
  - Excel/CSV files (with column mapping)
- **Smart Data Extraction**: Intelligently extracts from PDFs:
  - BO Numbers (Schedule No, PO No, Order No)
  - Client Names and TRN/VAT numbers
  - Descriptions, Quantities, Rates, and Line Items
- **Client Management**: 
  - Dropdown with predefined client names
  - Add new custom clients on-the-fly
  - Persistent client database
- **Multi-Item Support**: Handle multiple line items from BO documents
- **Auto-Population & Lock**: Fields auto-populated from BO are locked to prevent accidental changes
- **Data Validation**: Validate all inputs before saving (Quantity, Rate, Budget, VAT)
- **VAT Handling**: Automatic validation for 0% VAT (Non-GCC) and 5% VAT (UAE)
- **Calendar Pickers**: Date and delivery month selection with calendar widget

## Installation

1. Navigate to the project directory:
```bash
cd invoice_automation
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

Note: For PDF parsing capabilities, ensure PyPDF2 or pypdf is installed (included in requirements.txt)

## Project Structure

```
invoice_automation/
├── config.py              # Configuration and field mappings
├── excel_handler.py       # Excel read/write operations
├── validator.py           # Data validation rules
├── client_manager.py      # Client management system (new)
├── bo_pdf_parser.py       # BO PDF parsing and extraction (new)
├── ui.py                  # Streamlit web interface
├── clients.json           # Stored client list (auto-generated)
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Usage

### Running the Web Application

```bash
streamlit run ui.py
```

This will open the Invoice Template Editor in your browser where you can:

1. **Upload Business Order (BO) File**
   - PDF: Automatically extracts BO number, client name, TRN, descriptions, quantities, and rates
   - Excel/CSV: Maps common column names to invoice fields
   - Extracted data is auto-populated and locked (read-only)

2. **Edit Invoice Fields**
   - Manual input for: Invoice Number, Date, Delivery Month
   - Dropdown with predefined clients (or add new)
   - Auto-populated fields from BO are locked for safety
   - Calendar pickers for date selection

3. **View Extracted Data**
   - Expandable section showing all parsed BO data
   - View multiple line items detected in BO

4. **Save Invoice**
   - Validates all data before saving
   - Auto-generates filename based on invoice number
   - Saves to `generated_invoices/` folder

## Advanced BO Data Mapping

### PDF Parsing Capabilities

The `BOPDFParser` class intelligently extracts data from PDF files:

#### BO Number Extraction
Recognizes patterns like:
- `PD25|2041|4` format
- `Order No:`, `BO No:`, `PO No:`, `Schedule No:` labels
- Case-insensitive matching

#### Client Information
- **Client Name**: Extracted from "Attention:", "Client:", "Customer:" fields
- **TRN/VAT Number**: Searches for VAT Registration, TRN, Tax ID labels

#### Line Items
Extracts multiple line items including:
- **Descriptions**: Campaign names, product names, placement types
- **Quantities/Volumes**: Numeric values associated with descriptions
- **Rates/Unit Costs**: Dollar amounts associated with items

### Excel/CSV Mapping

Automatically maps common column names to invoice fields:

```python
bo_mapping = {
    'client_name': ['Client Name', 'client', 'customer', 'company'],
    'client_trn': ['TRN', 'trn', 'tax_id', 'vat'],
    'bo_no': ['BO Number', 'bo_no', 'order_no', 'order_number', 'po_no'],
    'description': ['Description', 'item', 'product', 'details'],
    'quantity': ['Quantity', 'qty', 'units', 'volume'],
    'rate': ['Rate', 'unit_price', 'price', 'unit_cost', 'amount'],
}
```

### Client Management System

The `ClientManager` class provides:

1. **Predefined Clients**: Default list of common clients
2. **Custom Clients**: Add new clients through the UI
3. **Persistent Storage**: Clients saved in `clients.json`

**Adding a Client Programmatically**:
```python
from client_manager import ClientManager

manager = ClientManager()
manager.add_custom_client("New Company Name")
all_clients = manager.get_all_clients()
```

### Auto-Population & Field Locking

Fields extracted from BO documents are:
- ✅ Auto-populated with extracted values
- 🔒 Locked (read-only) to prevent accidental changes
- 📋 Clearly displayed as extracted in the UI

To unlock a field, clear the BO file and refresh.

## Editing Configuration

The following fields are editable:

| Field | Type | Notes |
|-------|------|-------|
| Invoice No. | Text | Unique invoice identifier |
| Client Name | Text | Company or individual name |
| Client Address | Text | Full delivery/billing address |
| Client TRN No. | Text | Tax Registration Number |
| Date | Date | Format: DD/MM/YYYY |
| BO No. | Text | Business Order number |
| Delivery Month | Text | Month for delivery |
| Quantity | Number | Must be > 0 |
| Rate | Number | Must be > 0 |
| Budget | Number | Must be > 0 |
| VAT Rate (%) | Number | Must be 0 or 5 |
| Total Amount | Number | Read-only (calculated) |

## Validation Rules

### Numeric Validations
- Quantity, Rate, Budget: Must be positive numbers
- VAT Rate: Must be 0% or 5% only

### Date Validation
- Format: DD/MM/YYYY

### Required Fields
All fields except read-only fields are required

## Generated Files

Modified invoices are saved to:
```
invoice_automation/generated_invoices/Invoice_YYYYMMDD_HHMMSS.xlsx
```

## Customization

### Adding New Fields

1. Open `config.py`
2. Add entry to `INVOICE_FIELDS` dictionary:
```python
'new_field': {
    'label': 'Field Label',
    'sheet': 'Invoice',
    'cell': 'C15',
    'type': 'string'
}
```

3. Add validation rules if needed in `VALIDATION_RULES`
4. Restart the application

### Modifying Cell References

Update the `cell` property in `config.py` for each field to match your template structure.

## Troubleshooting

### Template file not found
- Ensure `Yazle_Invoice_Template_Final.xlsx` is in the parent directory
- Update `TEMPLATE_FILE` path in `config.py`

### Cell reference errors
- Verify cell references in `config.py` match your Excel template
- Use format like 'B2', 'C10', etc.

### Validation failures
- Check data types match field requirements
- Ensure VAT rate is 0 or 5
- Ensure all required fields have values

## Future Enhancements

- [ ] Batch invoice generation from CSV
- [ ] Email integration for sending invoices
- [ ] Invoice preview before saving
- [ ] Support for multiple templates
- [ ] Database backend for invoice history
- [ ] Automatic calculation fields (VAT, Total)
- [ ] Invoice template designer

## Support

For issues or feature requests, contact the development team.
