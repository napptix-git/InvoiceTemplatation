"""
Streamlit-based UI for Invoice Template Automation with enhanced features
"""

import streamlit as st
from config import INVOICE_FIELDS
from excel_handler import ExcelHandler
from validator import InvoiceValidator
from datetime import datetime, date, timedelta
import calendar


# Page config
st.set_page_config(
    page_title="Invoice Template Automation",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Invoice Template Editor")
st.markdown("---")

# Initialize session state
if 'excel_handler' not in st.session_state:
    st.session_state.excel_handler = ExcelHandler()
    st.session_state.validator = InvoiceValidator()
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
    
    # Create form fields
    form_data = {}
    
    for field_key, field_config in INVOICE_FIELDS.items():
        label = field_config['label']
        is_readonly = field_config.get('read_only', False)
        field_type = field_config.get('type', 'string')
        current_value = st.session_state.current_data.get(field_key, '')
        
        if current_value is None:
            current_value = ''
        
        # Special handling for invoice_no with prefix
        if field_key == 'invoice_no':
            st.markdown("**Invoice No.**")
            col_prefix, col_number = st.columns([0.4, 0.6])
            with col_prefix:
                st.text_input("Prefix", value="INV-FY2526-", disabled=True, key="invoice_prefix")
            with col_number:
                invoice_number = st.text_input("Number", value=str(current_value).replace("INV-FY2526-", ""), key=f"field_{field_key}", placeholder="e.g., 001")
                form_data[field_key] = f"INV-FY2526-{invoice_number}"
        
        # Special handling for date - add calendar picker
        elif field_key == 'date':
            st.markdown("**Date**")
            col_input, col_button = st.columns([0.8, 0.2])
            with col_input:
                # Use temp_date if it was set from picker, otherwise use current_value
                display_value = st.session_state.get('temp_date', str(current_value))
                date_input = st.text_input(
                    label="Select Date",
                    value=display_value,
                    key=f"field_{field_key}",
                    placeholder="DD/MM/YYYY"
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
                # Use temp_delivery_month if it was set from picker, otherwise use current_value
                display_value = st.session_state.get('temp_delivery_month', str(current_value))
                delivery_month_input = st.text_input(
                    label="Select Month",
                    value=display_value,
                    key=f"field_{field_key}",
                    placeholder="MM/YYYY"
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
        
        # Special handling for quantity (whole numbers only)
        elif field_key == 'quantity':
            quantity_val = st.number_input(
                label=label,
                value=int(float(current_value or 0)),
                min_value=0,
                step=1,
                key=f"field_{field_key}"
            )
            form_data[field_key] = quantity_val
            st.session_state.calc_quantity = float(quantity_val)
        
        # Special handling for rate
        elif field_key == 'rate':
            rate_val = st.number_input(
                label=label,
                value=float(current_value or 0),
                min_value=0.0,
                step=0.01,
                key=f"field_{field_key}"
            )
            form_data[field_key] = rate_val
            st.session_state.calc_rate = rate_val
        
        # Special handling for budget (read-only, calculated)
        elif field_key == 'budget':
            st.session_state.calc_budget = (st.session_state.calc_quantity * st.session_state.calc_rate) / 10000
            st.number_input(
                label=label,
                value=st.session_state.calc_budget,
                disabled=True,
                key=f"field_{field_key}",
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
            
            # Display VAT amount (read-only, calculated)
            st.session_state.calc_vat_amount = (st.session_state.calc_budget * vat_percent) / 100
            st.number_input(
                label="VAT Amount",
                value=st.session_state.calc_vat_amount,
                disabled=True,
                key="vat_amount_display",
                format="%.2f"
            )
            # include VAT amount in form data to be written to the sheet
            form_data['vat_amount'] = st.session_state.calc_vat_amount
        
        # Special handling for total amount (read-only, calculated)
        elif field_key == 'total_amount':
            st.session_state.calc_total_amount = st.session_state.calc_budget + st.session_state.calc_vat_amount
            st.number_input(
                label=label,
                value=st.session_state.calc_total_amount,
                disabled=True,
                key=f"field_{field_key}",
                format="%.2f"
            )
            form_data[field_key] = st.session_state.calc_total_amount
        
        # Read-only fields
        elif is_readonly:
            st.text_input(
                label=label,
                value=str(current_value),
                disabled=True,
                key=f"field_{field_key}"
            )
            form_data[field_key] = str(current_value)
        
        # Regular text/date inputs
        else:
            form_data[field_key] = st.text_input(
                label=label,
                value=str(current_value),
                key=f"field_{field_key}"
            )

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
                        # leave due_date as-is if parsing fails
                        pass

                # Save invoice; filename should be invoice number
                inv_no = form_data.get('invoice_no') or 'Invoice'
                safe_name = str(inv_no).strip().replace('/', '-').replace('\\n', '_')
                filename = f"{safe_name}.xlsx"
                st.session_state.excel_handler.update_invoice(form_data)
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
        st.rerun()

st.markdown("---")

# Summary section
st.subheader("📊 Summary")
summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

with summary_col1:
    st.metric("Budget", f"AED {st.session_state.calc_budget:,.2f}")
with summary_col2:
    st.metric("VAT Type", st.session_state.calc_vat_type)
with summary_col3:
    st.metric("VAT Amount", f"AED {st.session_state.calc_vat_amount:,.2f}")
with summary_col4:
    st.metric("Total Amount", f"AED {st.session_state.calc_total_amount:,.2f}", delta=f"+{st.session_state.calc_vat_amount:.2f}" if st.session_state.calc_vat_amount > 0 else None)

st.caption("Invoice Template Automation System")
