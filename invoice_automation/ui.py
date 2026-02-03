"""
Streamlit-based UI for Invoice Template Automation with BO data mapping
Enhanced with client dropdown, PDF parsing, and field auto-population
"""

import streamlit as st
from config import INVOICE_FIELDS
from excel_handler import ExcelHandler
from validator import InvoiceValidator
from client_manager import ClientManager
from bo_pdf_parser import BOPDFParser
from datetime import datetime, date, timedelta
import calendar
import math
from io import BytesIO


# Page config
st.set_page_config(
    page_title="Invoice Template Automation",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Invoice Template Editor")
st.markdown("---")

# File uploader for BO (Business Order) files at the top
st.subheader("📤 Upload Business Order (BO)")
bo_file = st.file_uploader(
    "Drag and drop or click to upload BO file (CSV, Excel or PDF)",
    type=["csv", "xlsx", "xls", "pdf"],
    help="Upload a BO file to auto-populate invoice fields"
)

# Initialize session state
if 'excel_handler' not in st.session_state:
    st.session_state.excel_handler = ExcelHandler()
    st.session_state.validator = InvoiceValidator()
    st.session_state.client_manager = ClientManager()
    try:
        st.session_state.excel_handler.load_template()
        st.session_state.current_data = st.session_state.excel_handler.get_all_template_values()
    except Exception as e:
        st.error(f"Error loading template: {str(e)}")
        st.stop()

# Initialize fields that were auto-populated from BO
if 'auto_populated_fields' not in st.session_state:
    st.session_state.auto_populated_fields = set()

# Initialize fields with multiple values (line items)
if 'line_items' not in st.session_state:
    st.session_state.line_items = []

# Process uploaded BO file
if bo_file is not None:
    try:
        fname = bo_file.name.lower()
        # Handle CSV / Excel
        if fname.endswith('.csv') or fname.endswith('.xls') or fname.endswith('.xlsx'):
            import pandas as pd
            if fname.endswith('.csv'):
                bo_data = pd.read_csv(bo_file)
            else:
                bo_data = pd.read_excel(bo_file)

            # Auto-map common column names to invoice fields
            bo_mapping = {
                'client_name': ['Client Name', 'client', 'customer', 'company'],
                'client_address': ['Address', 'client_address', 'address'],
                'client_trn': ['TRN', 'trn', 'tax_id', 'vat'],
                'bo_no': ['BO Number', 'bo_no', 'order_no', 'order_number', 'po_no'],
                'description': ['Description', 'item', 'product', 'details'],
                'quantity': ['Quantity', 'qty', 'units', 'volume'],
                'rate': ['Rate', 'unit_price', 'price', 'unit_cost', 'amount'],
                'delivery_month': ['Delivery Month', 'delivery', 'month'],
            }

            # Extract and populate fields
            bo_values = {}
            for field_key, column_names in bo_mapping.items():
                for col in column_names:
                    if col in bo_data.columns:
                        value = bo_data[col].iloc[0]
                        bo_values[field_key] = value
                        st.session_state.auto_populated_fields.add(field_key)
                        break

            # Store in session state for form population
            if bo_values:
                st.session_state.bo_values = bo_values
                st.success(f"✓ BO file loaded! Found {len(bo_values)} field(s). Form will be populated below.")

        # Handle PDF uploads with advanced parsing
        elif fname.endswith('.pdf'):
            try:
                # read raw bytes
                content = bo_file.read()
                # Try PyPDF2 or pypdf for text extraction
                PdfReader = None
                try:
                    from PyPDF2 import PdfReader
                    PdfReader = PdfReader
                except Exception:
                    try:
                        from pypdf import PdfReader
                        PdfReader = PdfReader
                    except Exception:
                        PdfReader = None

                if PdfReader is None:
                    st.session_state.bo_file_bytes = content
                    st.warning("PDF uploaded but PDF parsing library (PyPDF2/pypdf) is not installed. File accepted but auto-parsing is unavailable.")
                else:
                    reader = PdfReader(BytesIO(content))
                    text_parts = []
                    # extract text from up to first 5 pages
                    for i, p in enumerate(reader.pages):
                        if i >= 5:
                            break
                        try:
                            t = p.extract_text() or ''
                        except Exception:
                            t = ''
                        text_parts.append(t)
                    extracted = "\n\n".join(text_parts).strip()
                    st.session_state.bo_text = extracted
                    
                    # Parse BO data using advanced parser
                    parser = BOPDFParser(extracted)
                    bo_parsed_data = parser.extract_all_data()
                    
                    # Prepare bo_values from parsed data
                    bo_values = {}
                    if bo_parsed_data.get('bo_no'):
                        bo_values['bo_no'] = bo_parsed_data['bo_no']
                        st.session_state.auto_populated_fields.add('bo_no')
                    if bo_parsed_data.get('client_name'):
                        bo_values['client_name'] = bo_parsed_data['client_name']
                        st.session_state.auto_populated_fields.add('client_name')
                    if bo_parsed_data.get('client_trn'):
                        bo_values['client_trn'] = bo_parsed_data['client_trn']
                        st.session_state.auto_populated_fields.add('client_trn')
                    
                    # Handle line items (multiple descriptions, quantities, rates)
                    if bo_parsed_data.get('descriptions'):
                        line_items = []
                        descriptions = bo_parsed_data['descriptions']
                        quantities = bo_parsed_data['quantities']
                        rates = bo_parsed_data['rates']
                        
                        max_items = max(len(descriptions), len(quantities), len(rates))
                        for i in range(max_items):
                            item = {
                                'description': descriptions[i] if i < len(descriptions) else '',
                                'quantity': quantities[i] if i < len(quantities) else None,
                                'rate': rates[i] if i < len(rates) else None,
                            }
                            line_items.append(item)
                        
                        st.session_state.line_items = line_items
                        
                        # Use first line item as main entry
                        if line_items:
                            if line_items[0]['description']:
                                bo_values['description'] = line_items[0]['description']
                                st.session_state.auto_populated_fields.add('description')
                            if line_items[0]['quantity'] is not None:
                                bo_values['quantity'] = line_items[0]['quantity']
                                st.session_state.auto_populated_fields.add('quantity')
                            if line_items[0]['rate'] is not None:
                                bo_values['rate'] = line_items[0]['rate']
                                st.session_state.auto_populated_fields.add('rate')
                    
                    if bo_values:
                        st.session_state.bo_values = bo_values
                        st.success(f"✓ PDF uploaded and parsed! Auto-populated {len(bo_values)} field(s).")
                        
                        # Show extracted data for review
                        with st.expander("📋 View Extracted BO Data"):
                            st.write("**BO Number:**", bo_parsed_data.get('bo_no') or "Not found")
                            st.write("**Client Name:**", bo_parsed_data.get('client_name') or "Not found")
                            st.write("**Client TRN:**", bo_parsed_data.get('client_trn') or "Not found")
                            
                            if st.session_state.line_items:
                                st.write("**Line Items:**")
                                for idx, item in enumerate(st.session_state.line_items, 1):
                                    st.write(f"  Item {idx}:")
                                    st.write(f"    - Description: {item['description']}")
                                    st.write(f"    - Quantity: {item['quantity']}")
                                    st.write(f"    - Rate: {item['rate']}")
                    else:
                        st.warning("PDF extracted but no structured BO data found. Please fill fields manually.")

            except Exception as e:
                st.error(f"Error processing PDF file: {str(e)}")

        else:
            st.error("Unsupported file type. Please upload CSV, Excel, or PDF files.")

    except Exception as e:
        st.error(f"Error processing BO file: {str(e)}")

# Initialize calculation fields in session state
if 'calc_quantity' not in st.session_state:
    st.session_state.calc_quantity = float(st.session_state.current_data.get('quantity', 0) or 0)
if 'calc_rate' not in st.session_state:
    st.session_state.calc_rate = float(st.session_state.current_data.get('rate', 0) or 0)
if 'calc_budget' not in st.session_state:
    st.session_state.calc_budget = 0.0
if 'calc_vat_type' not in st.session_state:
    st.session_state.calc_vat_type = 'non-GCC'
if 'calc_vat_amount' not in st.session_state:
    st.session_state.calc_vat_amount = 0.0
if 'calc_total_amount' not in st.session_state:
    st.session_state.calc_total_amount = 0.0

# Create columns for better layout
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Invoice Details")
    
    # Create form fields
    form_data = {}
    
    for field_key, field_config in INVOICE_FIELDS.items():
        # Skip calculated fields from UI display except total_amount which we show read-only
        if field_key in ['due_date', 'vat_amount', 'total_in_words']:
            continue
        
        label = field_config['label']
        is_readonly = field_config.get('read_only', False)
        field_type = field_config.get('type', 'string')
        current_value = st.session_state.current_data.get(field_key, '')
        
        if current_value is None:
            current_value = ''
        
        # Check if this field was auto-populated from BO
        is_auto_populated = field_key in st.session_state.auto_populated_fields
        
        # Special handling for invoice_no with prefix
        if field_key == 'invoice_no':
            st.markdown("**Invoice No.**")
            col_prefix, col_number = st.columns([0.4, 0.6])
            with col_prefix:
                st.text_input("Prefix", value="INV-FY2526-", disabled=True, key="invoice_prefix")
            with col_number:
                # Check for BO values first; do not prefill with template invoice number
                bo_val = st.session_state.get('bo_values', {}).get(field_key, '')
                inv_val = str(current_value).replace("INV-FY2526-", "") if current_value else ""
                # Use BO value as the input value; otherwise keep the field empty and show template as placeholder
                invoice_number = st.text_input(
                    "Number",
                    value=bo_val or "",
                    placeholder=inv_val or "e.g., 001",
                    key=f"field_{field_key}",
                    disabled=is_auto_populated  # Make read-only if auto-populated
                )
                form_data[field_key] = (f"INV-FY2526-{invoice_number}" if str(invoice_number).strip() else "")
        
        # Special handling for client_name with dropdown
        elif field_key == 'client_name':
            st.markdown("**Client Name**")
            
            col_dropdown, col_add = st.columns([0.8, 0.2])
            
            with col_dropdown:
                # Get all clients
                all_clients = st.session_state.client_manager.get_all_clients()
                bo_val = st.session_state.get('bo_values', {}).get(field_key, '')
                
                # If BO value exists, add it to the list if not already there
                if bo_val and bo_val not in all_clients:
                    all_clients = [bo_val] + all_clients
                
                # Set default index
                default_idx = 0
                if bo_val and bo_val in all_clients:
                    default_idx = all_clients.index(bo_val)
                
                selected_client = st.selectbox(
                    label=label,
                    options=all_clients,
                    index=default_idx,
                    key=f"field_{field_key}",
                    disabled=is_auto_populated  # Make read-only if auto-populated
                )
                form_data[field_key] = selected_client
            
            with col_add:
                if st.button("➕ Add Client", key="add_client_btn", help="Add new client", use_container_width=True):
                    st.session_state.show_add_client = True
            
            # Show add client dialog
            if st.session_state.get('show_add_client', False):
                st.info("**Add New Client**")
                new_client = st.text_input(
                    "Enter client name:",
                    key="new_client_input",
                    placeholder="e.g., New Company Name"
                )
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("Save Client", key="save_client_btn"):
                        if new_client and new_client.strip():
                            try:
                                st.session_state.client_manager.add_custom_client(new_client)
                                st.session_state.show_add_client = False
                                st.success(f"✓ Client '{new_client}' added successfully!")
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))
                        else:
                            st.error("Client name cannot be empty")
                with col_cancel:
                    if st.button("Cancel", key="cancel_client_btn"):
                        st.session_state.show_add_client = False
                        st.rerun()
        
        # Special handling for date - add calendar picker
        elif field_key == 'date':
            st.markdown("**Date**")
            col_input, col_button = st.columns([0.8, 0.2])
            with col_input:
                # Use temp_date if it was set from picker; otherwise show template value as placeholder
                temp_date = st.session_state.get('temp_date')
                placeholder_val = str(current_value) if current_value else "DD/MM/YYYY"
                date_input = st.text_input(
                    label="Select Date",
                    value=temp_date or "",
                    key=f"field_{field_key}",
                    placeholder=placeholder_val,
                    disabled=is_auto_populated  # Make read-only if auto-populated
                )
                form_data[field_key] = date_input
            with col_button:
                if st.button("📅", key="date_picker_btn", help="Pick Date", use_container_width=True):
                    st.session_state.show_date_picker = True
            
            if st.session_state.get('show_date_picker', False):
                st.write("**Select Date:**")
                picker_col1, picker_col2, picker_col3 = st.columns(3)
                with picker_col1:
                    day = st.selectbox("Day", list(range(1, 32)), key="date_day")
                with picker_col2:
                    month = st.selectbox("Month", list(range(1, 13)), format_func=lambda x: calendar.month_name[x], key="date_month")
                with picker_col3:
                    year = st.number_input("Year", min_value=2020, max_value=2100, value=datetime.now().year, key="date_year")
                
                if st.button("Apply Date", key="apply_date_btn"):
                    selected_date = f"{day:02d}/{month:02d}/{year:04d}"
                    st.session_state.temp_date = selected_date
                    st.session_state.show_date_picker = False
                    st.rerun()
        
        # Special handling for delivery_month - add calendar picker
        elif field_key == 'delivery_month':
            st.markdown("**Delivery Month**")
            col_input, col_button = st.columns([0.8, 0.2])
            with col_input:
                # Check BO values first, then temp, then template
                bo_val = st.session_state.get('bo_values', {}).get(field_key, '')
                temp_delivery = st.session_state.get('temp_delivery_month')
                placeholder_dm = str(current_value) if current_value else "MM/YYYY"
                delivery_month_input = st.text_input(
                    label="Select Month",
                    value=bo_val or temp_delivery or "",
                    key=f"field_{field_key}",
                    placeholder=placeholder_dm if not (bo_val or temp_delivery) else "",
                    disabled=is_auto_populated  # Make read-only if auto-populated
                )
                form_data[field_key] = delivery_month_input
            with col_button:
                if st.button("📅", key="delivery_calendar", help="Select Month and Year", use_container_width=True):
                    st.session_state.show_delivery_picker = True
            
            if st.session_state.get('show_delivery_picker', False):
                st.write("**Select Month and Year:**")
                picker_col1, picker_col2 = st.columns(2)
                with picker_col1:
                    month = st.selectbox("Month", list(range(1, 13)), format_func=lambda x: calendar.month_name[x], key="delivery_month_select")
                with picker_col2:
                    year = st.number_input("Year", min_value=2020, max_value=2100, value=datetime.now().year, key="delivery_year_select")
                
                if st.button("Apply Month", key="apply_delivery_month_btn"):
                    selected_date = f"{month:02d}/{year}"
                    st.session_state.temp_delivery_month = selected_date
                    st.session_state.show_delivery_picker = False
                    st.rerun()
        
        # Special handling for quantity (show template as placeholder, accept numeric input)
        elif field_key == 'quantity':
            bo_val = st.session_state.get('bo_values', {}).get(field_key, '')
            placeholder_qty = str(int(float(current_value or 0))) if current_value else ""
            qty_input = st.text_input(
                label=label,
                value=str(bo_val) if bo_val else "",
                placeholder=placeholder_qty if not bo_val else "",
                key=f"field_{field_key}",
                disabled=is_auto_populated  # Make read-only if auto-populated
            )
            try:
                quantity_val = int(float(qty_input)) if str(qty_input).strip() != '' else 0
            except Exception:
                quantity_val = 0
            form_data[field_key] = quantity_val
            st.session_state.calc_quantity = float(quantity_val)
        
        # Special handling for rate (show template as placeholder, accept numeric input)
        elif field_key == 'rate':
            bo_val = st.session_state.get('bo_values', {}).get(field_key, '')
            placeholder_rate = str(float(current_value)) if current_value else ""
            rate_input = st.text_input(
                label=label,
                value=str(bo_val) if bo_val else "",
                placeholder=placeholder_rate if not bo_val else "",
                key=f"field_{field_key}",
                disabled=is_auto_populated  # Make read-only if auto-populated
            )
            try:
                rate_val = float(rate_input) if str(rate_input).strip() != '' else 0.0
            except Exception:
                rate_val = 0.0
            form_data[field_key] = rate_val
            st.session_state.calc_rate = rate_val
        
        # Special handling for description
        elif field_key == 'description':
            bo_val = st.session_state.get('bo_values', {}).get(field_key, '')
            placeholder_desc = str(current_value) if current_value else ""
            desc_input = st.text_area(
                label=label,
                value=bo_val or "",
                placeholder=placeholder_desc if not bo_val else "",
                key=f"field_{field_key}",
                height=80,
                disabled=is_auto_populated  # Make read-only if auto-populated
            )
            form_data[field_key] = desc_input
        
        # Special handling for BO No
        elif field_key == 'bo_no':
            bo_val = st.session_state.get('bo_values', {}).get(field_key, '')
            placeholder_bo = str(current_value) if current_value else ""
            bo_no_input = st.text_input(
                label=label,
                value=bo_val or "",
                placeholder=placeholder_bo if not bo_val else "",
                key=f"field_{field_key}",
                disabled=is_auto_populated  # Make read-only if auto-populated
            )
            form_data[field_key] = bo_no_input
        
        # Special handling for Client TRN
        elif field_key == 'client_trn':
            bo_val = st.session_state.get('bo_values', {}).get(field_key, '')
            placeholder_trn = str(current_value) if current_value else ""
            trn_input = st.text_input(
                label=label,
                value=bo_val or "",
                placeholder=placeholder_trn if not bo_val else "",
                key=f"field_{field_key}",
                disabled=is_auto_populated  # Make read-only if auto-populated
            )
            form_data[field_key] = trn_input
        
        # Special handling for budget (read-only, calculated)
        elif field_key == 'budget':
            st.session_state.calc_budget = (st.session_state.calc_quantity * st.session_state.calc_rate) / 1000
            st.number_input(
                label=label,
                value=st.session_state.calc_budget,
                disabled=True,
                key=f"display_{field_key}",
                format="%.2f"
            )
            form_data[field_key] = st.session_state.calc_budget
        
        # Special handling for VAT rate (dropdown)
        elif field_key == 'vat_rate':
            vat_option = st.selectbox(
                label=label,
                options=['non-GCC (0%)', 'GCC (5%)'],
                index=0 if st.session_state.calc_vat_type == 'non-GCC' else 1,
                key=f"field_{field_key}"
            )
            
            if 'non-GCC' in vat_option:
                st.session_state.calc_vat_type = 'non-GCC'
                vat_percent = 0
            else:
                st.session_state.calc_vat_type = 'GCC'
                vat_percent = 5
            
            form_data[field_key] = vat_percent
            
            # Calculate VAT amount (not shown in UI)
            st.session_state.calc_vat_amount = (st.session_state.calc_budget * vat_percent) / 100
        
        # Read-only fields (including total_amount handled here)
        elif is_readonly:
            # For total_amount, show calculated value instead of template/formula
            if field_key == 'total_amount':
                st.session_state.calc_total_amount = st.session_state.calc_budget + st.session_state.calc_vat_amount
                st.text_input(
                    label=label,
                    value=f"{st.session_state.calc_total_amount:.2f}",
                    disabled=True,
                    key=f"field_{field_key}"
                )
                form_data[field_key] = st.session_state.calc_total_amount
            else:
                st.text_input(
                    label=label,
                    value=str(current_value),
                    disabled=True,
                    key=f"field_{field_key}"
                )
                form_data[field_key] = str(current_value)
        
        # Regular text/date inputs
        else:
            # Use BO value if available, otherwise show template as placeholder
            bo_val = st.session_state.get('bo_values', {}).get(field_key, '')
            placeholder_val = str(current_value) if current_value else ""
            form_data[field_key] = st.text_input(
                label=label,
                value=bo_val or "",
                placeholder=placeholder_val if not bo_val else "",
                key=f"field_{field_key}",
                disabled=is_auto_populated  # Make read-only if auto-populated
            )

        # (total_amount rendered above as read-only)

    # Show header preview (merged B1) as read-only so user can verify
    try:
        from config import INVOICE_HEADER_CELL
        header_val = st.session_state.current_data.get('header', '')
        if header_val is None:
            header_val = ''
        st.markdown("**Header Preview (top row)**")
        st.text_area("Header", value=str(header_val), disabled=True, height=70)
    except Exception:
        pass
    
    # Show line items if multiple exist
    if st.session_state.line_items:
        st.markdown("---")
        st.subheader("📋 Additional Line Items (from BO)")
        st.info(f"Found {len(st.session_state.line_items)} line item(s) in the BO. First item is shown above.")
        with st.expander("View all line items", expanded=False):
            for idx, item in enumerate(st.session_state.line_items[1:], 2):
                st.write(f"**Item {idx}:**")
                st.write(f"- Description: {item['description']}")
                st.write(f"- Quantity: {item['quantity']}")
                st.write(f"- Rate: {item['rate']}")

with col2:
    st.subheader("Actions")
    
    # Save button
    if st.button("💾 Save Invoice", use_container_width=True):
        try:
            # Validate data
            if not st.session_state.validator.validate_all(form_data):
                errors = st.session_state.validator.get_errors()
                st.error("**Validation Errors:**\n\n" + "\n".join(f"- {e}" for e in errors))
            else:
                # Ensure due date is computed as Date + 30 days (if date provided)
                date_str = form_data.get('date')
                if date_str:
                    try:
                        parsed = datetime.strptime(date_str, "%d/%m/%Y")
                        due_dt = parsed + timedelta(days=30)
                        due_str = due_dt.strftime("%d/%m/%Y")
                        form_data['due_date'] = due_str
                    except Exception:
                        pass

                # Include calculated VAT amount
                form_data['vat_amount'] = st.session_state.calc_vat_amount
                
                # Compute total amount
                st.session_state.calc_total_amount = st.session_state.calc_budget + st.session_state.calc_vat_amount
                form_data['total_amount'] = st.session_state.calc_total_amount
                
                # Compute total in words (dollars only)
                try:
                    total_val = float(form_data.get('total_amount', 0) or 0)
                except Exception:
                    total_val = 0.0

                def _int_to_words(n):
                    # supports 0 <= n < 1 trillion
                    to19 = ['Zero','One','Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten','Eleven','Twelve','Thirteen','Fourteen','Fifteen','Sixteen','Seventeen','Eighteen','Nineteen']
                    tens = ['','','Twenty','Thirty','Forty','Fifty','Sixty','Seventy','Eighty','Ninety']

                    def words(num):
                        if num < 20:
                            return to19[num]
                        if num < 100:
                            return tens[num//10] + ('' if num%10==0 else ' ' + to19[num%10])
                        if num < 1000:
                            return to19[num//100] + ' Hundred' + ('' if num%100==0 else ' ' + words(num%100))
                        for p, w in [(10**9, 'Billion'), (10**6, 'Million'), (1000, 'Thousand')]:
                            if num >= p:
                                return words(num//p) + ' ' + w + ('' if num%p==0 else ' ' + words(num%p))
                        return ''
                    return words(n)

                dollars = int(math.floor(abs(total_val)))
                cents = int(round((abs(total_val) - dollars) * 100))
                words_parts = []
                if dollars == 0:
                    words_parts.append('Zero Dollars')
                else:
                    words_parts.append(f"{_int_to_words(dollars)} Dollars")
                if cents > 0:
                    words_parts.append(f"and {_int_to_words(cents)} Cents")
                total_words = ' '.join(words_parts)
                # Force uppercase (user-friendly)
                form_data['total_in_words'] = total_words.upper()

                # Save invoice; filename should be invoice number
                inv_no = form_data.get('invoice_no') or 'Invoice'
                safe_name = str(inv_no).strip().replace('/', '-').replace('\n', '_')
                filename = f"{safe_name}.xlsx"

                # Prepare data for writing to Excel: vat_rate cell should contain "VAT(5%)" or "VAT(0%)"
                excel_data = dict(form_data)
                try:
                    vat_percent = int(float(form_data.get('vat_rate', 0) or 0))
                except Exception:
                    vat_percent = 0
                excel_data['vat_rate'] = f"VAT({vat_percent}%)"

                st.session_state.excel_handler.update_invoice(excel_data)
                output_path = st.session_state.excel_handler.save_invoice(output_filename=filename)
                st.success(f"✓ Invoice saved successfully!\n\nLocation: `{output_path}`")
        except Exception as e:
            st.error(f"Error saving invoice: {str(e)}")
    
    # Clear button
    if st.button("🗑️ Clear Fields", use_container_width=True):
        # Reset non-readonly fields
        for field_key, field_config in INVOICE_FIELDS.items():
            if not field_config.get('read_only', False):
                st.session_state.pop(f"field_{field_key}", None)
        st.session_state.calc_quantity = 0.0
        st.session_state.calc_rate = 0.0
        st.session_state.calc_budget = 0.0
        st.session_state.calc_vat_type = 'non-GCC'
        st.session_state.calc_vat_amount = 0.0
        st.session_state.calc_total_amount = 0.0
        st.session_state.auto_populated_fields = set()
        st.session_state.line_items = []
        st.rerun()

st.markdown("---")

# Summary section
st.subheader("📊 Summary")
summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

with summary_col1:
    st.metric("Budget", f"$ {st.session_state.calc_budget:,.2f}")
with summary_col2:
    st.metric("VAT Type", st.session_state.calc_vat_type)
with summary_col3:
    st.metric("VAT Amount", f"$ {st.session_state.calc_vat_amount:,.2f}")
with summary_col4:
    st.session_state.calc_total_amount = st.session_state.calc_budget + st.session_state.calc_vat_amount
    st.metric("Total Amount", f"$ {st.session_state.calc_total_amount:,.2f}", delta=f"+{st.session_state.calc_vat_amount:.2f}" if st.session_state.calc_vat_amount > 0 else None)

st.caption("Invoice Template Automation System with BO Data Mapping")
