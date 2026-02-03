"""
IMPLEMENTATION GUIDE: BO Data Mapping & Auto-Population Features
=================================================================

This document describes the complete implementation of Business Order (BO) data
extraction and auto-population with field locking feature.
"""

# ============================================================================
# 1. CLIENT MANAGEMENT SYSTEM
# ============================================================================

"""
LOCATION: client_manager.py
FEATURES:
  - Predefined client dropdown list
  - Add new custom clients on-the-fly
  - Persistent storage in clients.json
  - Auto-initialize with default clients

USAGE FLOW:
  1. User opens UI
  2. ClientManager loads clients from clients.json (or initializes default)
  3. User selects from dropdown or clicks "Add Client"
  4. New client added to custom list and saved
  5. Next session will include the new client

PREDEFINED CLIENTS:
  - Unilever Master - GCC
  - AXE MALE DEODORANT 20
  - Yazle Media
  - Emirates Marketing Group
  - Dubai Media Corporation
  - ABC Trading LLC
  - XYZ Distribution Company

KEY METHODS:
  ClientManager.get_all_clients()        -> List[str]
  ClientManager.add_custom_client(name)  -> None
  ClientManager.remove_custom_client(name) -> bool
  ClientManager.get_predefined_clients() -> List[str]
  ClientManager.get_custom_clients()     -> List[str]
"""

# ============================================================================
# 2. BO PDF PARSER
# ============================================================================

"""
LOCATION: bo_pdf_parser.py
PURPOSE: Intelligently extract data from PDF Business Order documents

PARSING CAPABILITIES:

A. BO NUMBER EXTRACTION
   Patterns recognized:
   - "PD25|2041|4" format
   - "Order No:", "BO No:", "PO No:", "Schedule No:"
   
   Example from test:
   "Order No: PD25|2041|4" -> extracts "PD25|2041|4"

B. CLIENT NAME EXTRACTION
   Looks for labels:
   - "Attention:", "Client:", "Customer:", "Recipient:", "Company:"
   
   Example:
   "Attention: Yazle Marketing Management" -> "Yazle Marketing Management"

C. TRN/VAT NUMBER EXTRACTION
   Patterns:
   - "VAT REGISTRATION No.", "TRN:", "Tax ID:", "VAT Registration No."
   - Extracts only numeric digits (at least 8)
   
   Example:
   "VAT REGISTRATION No. 100041432Z0003" -> "100041432"

D. DESCRIPTION EXTRACTION
   - Looks for campaign/product names
   - Recognizes keywords: Placement, Banner, Video, Campaign, Ad
   - Limits to 5 descriptions maximum
   
   Examples:
   "Mixed Placement - ar, en - United Arab Emirates"
   "Clickable In-Game Banners"

E. QUANTITY/VOLUME EXTRACTION
   - Searches for labels: Volume, Quantity, QTY, Units
   - Extracts numeric values between 1 and 100,000
   - Limits to 10 quantities maximum

F. RATE/UNIT COST EXTRACTION
   - Searches for labels: Rate, Unit Cost, Unit Price, Price
   - Recognizes currency symbols: $, USD
   - Extracts numeric values between 1 and 1,000,000
   - Limits to 10 rates maximum

LINE ITEMS ASSEMBLY:
   - Pairs descriptions, quantities, and rates together
   - Creates list of dictionaries with all fields
   - Returns first item for main invoice, displays rest as additional items

KEY METHODS:
   BOPDFParser.extract_all_data() -> Dict with bo_no, client_name, 
                                     client_trn, descriptions, quantities, rates
   BOPDFParser.extract_line_items() -> List[Dict] with paired items
"""

# ============================================================================
# 3. UI AUTO-POPULATION & FIELD LOCKING
# ============================================================================

"""
LOCATION: ui.py
FEATURE: Auto-populate fields from BO and lock them to prevent changes

SESSION STATE TRACKING:
  - auto_populated_fields: Set of field keys that came from BO
  - bo_values: Dictionary of extracted BO data
  - line_items: List of additional line items

FIELD LOCKING MECHANISM:
  
  When BO file is processed:
  1. Data is extracted and stored in st.session_state.bo_values
  2. Field key is added to st.session_state.auto_populated_fields
  3. During form rendering, check: is_auto_populated = field_key in auto_populated_fields
  4. If auto_populated, set disabled=True on the input widget
  
  CODE EXAMPLE:
  ```python
  is_auto_populated = field_key in st.session_state.auto_populated_fields
  st.text_input(
      label="Client Name",
      value=bo_values.get('client_name', ''),
      disabled=is_auto_populated  # <- Lock if auto-populated
  )
  ```

FIELDS THAT CAN BE AUTO-POPULATED:
  - invoice_no (manual input only)
  - client_name (dropdown, locked if from BO)
  - client_trn (text input, locked if from BO)
  - bo_no (text input, locked if from BO)
  - date (manual input, can be locked)
  - delivery_month (manual input, can be locked)
  - description (text area, locked if from BO)
  - quantity (numeric, locked if from BO)
  - rate (numeric, locked if from BO)

SPECIAL HANDLING:

A. CLIENT NAME DROPDOWN
   - Always shows as dropdown for consistency
   - If BO value exists, adds it to the top of list if not already there
   - Sets it as default selection
   - Locked when auto-populated

B. DESCRIPTIONS WITH MULTIPLE ITEMS
   - First item is shown in main description field (locked)
   - Additional items displayed in expandable "Additional Line Items" section
   - Section shows Item 2, Item 3, etc.
   - Allows user to manually copy data if needed

C. DATE & DELIVERY MONTH
   - Have calendar picker buttons
   - Not locked even if auto-populated (allow user override)
   - But could be locked with: disabled=is_auto_populated

CLEARING AUTO-POPULATED DATA:
   - "Clear Fields" button resets auto_populated_fields to empty set
   - Also clears line_items list
   - User can upload a new BO to re-populate

VISUAL INDICATORS:
   - Auto-populated fields appear disabled/grayed out
   - "View Extracted BO Data" expander shows what was detected
   - "Additional Line Items" section shows multi-item info
"""

# ============================================================================
# 4. EXCEL/CSV FILE MAPPING
# ============================================================================

"""
COLUMN NAME MAPPING:

The system automatically maps common column names:

{
    'client_name': ['Client Name', 'client', 'customer', 'company'],
    'client_address': ['Address', 'client_address', 'address'],
    'client_trn': ['TRN', 'trn', 'tax_id', 'vat'],
    'bo_no': ['BO Number', 'bo_no', 'order_no', 'order_number', 'po_no'],
    'description': ['Description', 'item', 'product', 'details'],
    'quantity': ['Quantity', 'qty', 'units', 'volume'],
    'rate': ['Rate', 'unit_price', 'price', 'unit_cost', 'amount'],
    'delivery_month': ['Delivery Month', 'delivery', 'month'],
}

MATCHING LOGIC:
  1. For each field_key, try matching against column_names
  2. First match wins
  3. Takes value from first row (iloc[0])
  4. Adds field_key to auto_populated_fields
  5. Same locking behavior as PDF extraction

EXAMPLE:
  Input CSV with columns: 'client', 'Description', 'qty', 'unit_price'
  
  Maps to:
  - client_name = 'client' column value
  - description = 'Description' column value  
  - quantity = 'qty' column value
  - rate = 'unit_price' column value
"""

# ============================================================================
# 5. INTEGRATION POINTS
# ============================================================================

"""
HOW ALL PIECES WORK TOGETHER:

STEP 1: USER UPLOADS BO FILE
   ui.py:
   - User uploads PDF/Excel/CSV file
   - File type detected from extension

STEP 2: PDF EXTRACTION (if PDF)
   - PdfReader extracts text from first 5 pages
   - Text passed to BOPDFParser.extract_all_data()
   - Returns: bo_no, client_name, client_trn, descriptions, quantities, rates

STEP 3: DATA STORAGE
   Session state updated:
   - st.session_state.bo_values = {extracted data}
   - st.session_state.auto_populated_fields = {field_keys}
   - st.session_state.line_items = [{item1}, {item2}, ...]

STEP 4: FORM RENDERING
   For each field in INVOICE_FIELDS:
   - Check if in auto_populated_fields
   - Render with appropriate widget and disabled=is_auto_populated
   - Use bo_values for value, template values as placeholder

STEP 5: DISPLAY EXTRACTED DATA
   - Expandable section shows raw parsed data
   - Additional line items shown in expandable section
   - User can review before saving

STEP 6: SAVE INVOICE
   - Validate all fields
   - Save to Excel file
   - Auto-locked fields are included in saved data
"""

# ============================================================================
# 6. DATA FLOW DIAGRAM
# ============================================================================

"""
┌─────────────────────────┐
│  User Uploads BO File   │
│ (PDF/Excel/CSV)         │
└────────────┬────────────┘
             │
             ▼
    ┌────────────────────┐
    │ File Type Check    │
    └────────┬───────┬───┘
             │       │
        PDF  │       │  Excel/CSV
             ▼       ▼
      ┌──────────┐ ┌──────────────┐
      │PdfReader │ │Pandas read   │
      │Extract   │ │Map columns   │
      │text      │ └──────┬───────┘
      └────┬─────┘        │
           │              │
           ▼              ▼
      ┌──────────────────────────┐
      │ BOPDFParser.extract_all  │
      │ Returns structured data  │
      └────────┬─────────────────┘
               │
               ▼
      ┌──────────────────────────┐
      │ Update session state:    │
      │ bo_values                │
      │ auto_populated_fields    │
      │ line_items               │
      └────────┬─────────────────┘
               │
               ▼
      ┌──────────────────────────┐
      │ Render UI form           │
      │ Check is_auto_populated  │
      │ Set disabled=True        │
      │ Populate with bo_values  │
      └────────┬─────────────────┘
               │
               ▼
      ┌──────────────────────────┐
      │ User can:                │
      │ - Review extracted data  │
      │ - Edit unlocked fields   │
      │ - Cannot edit locked     │
      │ - Save invoice           │
      └──────────────────────────┘
"""

# ============================================================================
# 7. ERROR HANDLING & EDGE CASES
# ============================================================================

"""
HANDLED SCENARIOS:

1. PDF parsing library not installed
   → Show warning, allow manual entry
   
2. PDF has no extractable text
   → Show warning, allow manual entry
   
3. BO fields not found in PDF
   → Show what was found in expander
   → Continue with partially populated form
   
4. Multiple items in BO
   → First item shown in main fields (locked)
   → Rest shown in "Additional Line Items" (for reference)
   
5. Excel/CSV column names don't match
   → Fields not auto-populated
   → User must enter manually
   
6. Invalid data types
   → Validator catches and shows errors
   → Prevents save until corrected
   
7. Cleared auto-populated fields
   → User can unlock by clearing BO
   → "Clear Fields" button resets everything
"""

# ============================================================================
# 8. TESTING & VALIDATION
# ============================================================================

"""
TEST COVERAGE:

✓ All modules import successfully
✓ Template file loads correctly
✓ Client manager initializes with defaults
✓ PDF parser extracts from sample text
✓ Validator accepts valid data
✓ Field locking behavior works
✓ Multi-item handling works
✓ Excel/CSV mapping works

To run tests:
   python test_system.py

To test UI manually:
   streamlit run ui.py
   
   Then test with:
   - Sample PDF BO file (use provided screenshot example)
   - Sample Excel with client data
   - Sample CSV with BO information
"""

print("Implementation guide loaded successfully!")
