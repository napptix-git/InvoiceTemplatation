"""
Streamlit-based UI for Invoice Template Automation with BO data mapping
Enhanced with client dropdown, PDF parsing, and field auto-population
"""

import streamlit as st
from config import INVOICE_FIELDS
from excel_handler import ExcelHandler
from validator import InvoiceValidator
from client_manager import ClientManager
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

# BO drag-and-drop upload removed per user request.
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
    
    # Callback functions for date/delivery month pickers
    def apply_date_callback():
        """Callback to apply selected date before widget re-renders"""
        day = st.session_state.get('date_day', 1)
        month = st.session_state.get('date_month', 1)
        year = st.session_state.get('date_year', 2026)
        selected_date = f"{day:02d}/{month:02d}/{year:04d}"
        st.session_state['field_date'] = selected_date
        st.session_state.show_date_picker = False
    
    def apply_delivery_month_callback():
        """Callback to apply selected delivery month before widget re-renders"""
        month = st.session_state.get('delivery_month_select', 1)
        year = st.session_state.get('delivery_year_select', 2026)
        selected_date = f"{month:02d}/{year}"
        st.session_state['field_delivery_month'] = selected_date
        st.session_state.show_delivery_picker = False
    
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
        
        # We do not auto-populate fields from BO uploads; keep all fields editable.
        is_auto_populated = False
        
        # Special handling for invoice_no with prefix - Auto-generated, non-editable
        if field_key == 'invoice_no':
            # Get next invoice number from ClientManager
            if 'current_invoice_number' not in st.session_state:
                st.session_state.current_invoice_number = st.session_state.client_manager.get_next_invoice_number()
            
            st.markdown("**Invoice No.**")
            col_prefix, col_number = st.columns([0.4, 0.6])
            with col_prefix:
                st.text_input("Prefix", value="INV-FY2526-", disabled=True, key="invoice_prefix")
            with col_number:
                # Display auto-generated number (non-editable)
                auto_invoice_num = st.session_state.current_invoice_number
                st.text_input(
                    "Number",
                    value=auto_invoice_num,
                    disabled=True,  # Non-editable
                    key=f"field_{field_key}"
                )
                form_data[field_key] = f"INV-FY2526-{auto_invoice_num}"
        
        # Special handling for client_name with dropdown and auto-address population
        elif field_key == 'client_name':
            st.markdown("**Client Name**")
            
            col_dropdown, col_add = st.columns([0.8, 0.2])
            
            with col_dropdown:
                # Get all clients
                all_clients = st.session_state.client_manager.get_all_clients()
                selected_client = st.selectbox(
                    label=label,
                    options=all_clients,
                    index=0,
                    key=f"field_{field_key}"
                )
                form_data[field_key] = selected_client
                
                # Auto-populate client address when client is selected
                client_address = st.session_state.client_manager.get_client_address(selected_client)
                if client_address:
                    st.session_state['auto_client_address'] = client_address
            
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
                new_address = st.text_input(
                    "Enter client address:",
                    key="new_client_address_input",
                    placeholder="e.g., Dubai Business Park, Dubai, UAE"
                )
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("Save Client", key="save_client_btn"):
                        if new_client and new_client.strip():
                            try:
                                st.session_state.client_manager.add_custom_client(new_client, new_address)
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
        
        # Special handling for client_address - Auto-populated from selected client
        elif field_key == 'client_address':
            # Get auto-populated address from session state (set when client is selected)
            auto_address = st.session_state.get('auto_client_address', '')
            st.markdown("**Client Address** (Auto-populated)")
            address_input = st.text_area(
                label=label,
                value=auto_address or st.session_state.get(f"field_{field_key}", ""),
                placeholder="Address will auto-populate when you select a client",
                key=f"field_{field_key}",
                height=60,
            )
            form_data[field_key] = address_input
        
        # Special handling for date - add calendar picker
        elif field_key == 'date':
            st.markdown("**Date**")
            col_input, col_button = st.columns([0.8, 0.2])
            with col_input:
                # Initialize session state for date if not present - ensure it's a string
                if f"field_{field_key}" not in st.session_state:
                    st.session_state[f"field_{field_key}"] = str(current_value) if current_value else ""
                
                # Display the text input - Streamlit manages state via key parameter
                st.text_input(
                    label="Select Date",
                    key=f"field_{field_key}",
                    placeholder="DD/MM/YYYY",
                )
                # Get value from session state for form_data
                form_data[field_key] = st.session_state.get(f"field_{field_key}", "")
            
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
                
                st.button("Apply Date", key="apply_date_btn", on_click=apply_date_callback)
        
        # Special handling for delivery_month - add calendar picker
        elif field_key == 'delivery_month':
            st.markdown("**Delivery Month**")
            col_input, col_button = st.columns([0.8, 0.2])
            with col_input:
                # Initialize session state for delivery month if not present - ensure it's a string
                if f"field_{field_key}" not in st.session_state:
                    st.session_state[f"field_{field_key}"] = str(current_value) if current_value else ""
                
                # Display the text input - Streamlit manages state via key parameter
                st.text_input(
                    label="Select Month",
                    key=f"field_{field_key}",
                    placeholder="MM/YYYY",
                )
                # Get value from session state for form_data
                form_data[field_key] = st.session_state.get(f"field_{field_key}", "")
            
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
                
                st.button("Apply Month", key="apply_delivery_month_btn", on_click=apply_delivery_month_callback)
        
        # Special handling for quantity (show template as placeholder, accept numeric input)
        elif field_key == 'quantity':
            placeholder_qty = str(int(float(current_value or 0))) if current_value else ""
            qty_input = st.text_input(
                label=label,
                value=str(st.session_state.get(f"field_{field_key}", "")),
                placeholder=placeholder_qty,
                key=f"field_{field_key}",
            )
            try:
                quantity_val = int(float(qty_input)) if str(qty_input).strip() != '' else 0
            except Exception:
                quantity_val = 0
            form_data[field_key] = quantity_val
            st.session_state.calc_quantity = float(quantity_val)
        
        # Special handling for rate (show template as placeholder, accept numeric input)
        elif field_key == 'rate':
            placeholder_rate = str(float(current_value)) if current_value else ""
            rate_input = st.text_input(
                label=label,
                value=str(st.session_state.get(f"field_{field_key}", "")),
                placeholder=placeholder_rate,
                key=f"field_{field_key}",
            )
            try:
                rate_val = float(rate_input) if str(rate_input).strip() != '' else 0.0
            except Exception:
                rate_val = 0.0
            form_data[field_key] = rate_val
            st.session_state.calc_rate = rate_val
        
        # Special handling for description
        elif field_key == 'description':
            placeholder_desc = str(current_value) if current_value else ""
            desc_input = st.text_area(
                label=label,
                value=st.session_state.get(f"field_{field_key}", ""),
                placeholder=placeholder_desc,
                key=f"field_{field_key}",
                height=80,
            )
            form_data[field_key] = desc_input
        
        # Special handling for BO No
        elif field_key == 'bo_no':
            placeholder_bo = str(current_value) if current_value else ""
            bo_no_input = st.text_input(
                label=label,
                value=st.session_state.get(f"field_{field_key}", ""),
                placeholder=placeholder_bo,
                key=f"field_{field_key}",
            )
            form_data[field_key] = bo_no_input
        
        # Special handling for Client TRN
        elif field_key == 'client_trn':
            placeholder_trn = str(current_value) if current_value else ""
            trn_input = st.text_input(
                label=label,
                value=st.session_state.get(f"field_{field_key}", ""),
                placeholder=placeholder_trn,
                key=f"field_{field_key}",
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
    if st.session_state.get('line_items'):
        st.markdown("---")
        st.subheader("📋 Additional Line Items (from BO)")
        st.info(f"Found {len(st.session_state.get('line_items'))} line item(s) in the BO. First item is shown above.")
        with st.expander("View all line items", expanded=False):
            for idx, item in enumerate(st.session_state.get('line_items')[1:], 2):
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
                
                # Increment invoice number after successful save
                st.session_state.client_manager.increment_invoice_number()
                st.session_state.current_invoice_number = st.session_state.client_manager.get_next_invoice_number()
                
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
        st.session_state.auto_client_address = ""
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
