"""
Quick test script to verify all modules load and basic functionality
"""

import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("🔍 Testing Invoice Automation System...\n")

# Test 1: Import all modules
print("1️⃣ Testing module imports...")
try:
    from config import INVOICE_FIELDS, TEMPLATE_FILE
    print("   ✓ config module loaded")
    
    from excel_handler import ExcelHandler
    print("   ✓ excel_handler module loaded")
    
    from validator import InvoiceValidator
    print("   ✓ validator module loaded")
    
    from client_manager import ClientManager
    print("   ✓ client_manager module loaded")
    
    from bo_pdf_parser import BOPDFParser
    print("   ✓ bo_pdf_parser module loaded")
    
    print("\n✅ All modules imported successfully!\n")
except ImportError as e:
    print(f"\n❌ Import error: {e}\n")
    sys.exit(1)

# Test 2: Check template file
print("2️⃣ Checking template file...")
if os.path.exists(TEMPLATE_FILE):
    print(f"   ✓ Template found: {TEMPLATE_FILE}")
else:
    print(f"   ❌ Template not found: {TEMPLATE_FILE}")
    sys.exit(1)

# Test 3: Load template
print("\n3️⃣ Testing template loading...")
try:
    handler = ExcelHandler()
    handler.load_template()
    print("   ✓ Template loaded successfully")
    
    values = handler.get_all_template_values()
    print(f"   ✓ Retrieved {len(values)} field values from template")
    handler.close()
except Exception as e:
    print(f"   ❌ Error loading template: {e}")
    sys.exit(1)

# Test 4: Client Manager
print("\n4️⃣ Testing client manager...")
try:
    manager = ClientManager()
    clients = manager.get_all_clients()
    print(f"   ✓ Loaded {len(clients)} clients")
    print(f"   ✓ Predefined clients: {len(manager.get_predefined_clients())}")
    print(f"   ✓ Custom clients: {len(manager.get_custom_clients())}")
except Exception as e:
    print(f"   ❌ Error with client manager: {e}")
    sys.exit(1)

# Test 5: BO PDF Parser
print("\n5️⃣ Testing BO PDF parser...")
try:
    sample_text = """
    MEDIA BOOKING ORDER
    
    Attention: Yazle Marketing Management
    Client: Unilever Master - GCC
    Campaign Name: Unilever - Axe - 2025 - Digital Campaign
    Order No: PD25|2041|4
    Order Date: 04/09/2025
    
    VAT REGISTRATION No. 100041432Z0003
    
    Details | Volume | Date | Gross | Disc | Exp | Unit Cost | Net Cost | Taxes | Total Cost
    Mixed Placement - ar, en - United Arab Emirates | 14 USD | 4th Sep - 30th Sep | 14 USD | | | 14.00 USD | 5,000.00 USD | 5% VAT | 5,250.00 USD
    Clickable In-Game Banners - - Saudi Arabia | 14 USD | 4th Sep - 30th Sep | 14 USD | | | 14.00 USD | 10,000.00 USD | 5% VAT | 10,500.00 USD
    """
    
    parser = BOPDFParser(sample_text)
    data = parser.extract_all_data()
    
    print(f"   ✓ BO Number: {data.get('bo_no')}")
    print(f"   ✓ Client Name: {data.get('client_name')}")
    print(f"   ✓ Client TRN: {data.get('client_trn')}")
    print(f"   ✓ Descriptions found: {len(data.get('descriptions', []))}")
    print(f"   ✓ Quantities found: {len(data.get('quantities', []))}")
    print(f"   ✓ Rates found: {len(data.get('rates', []))}")
except Exception as e:
    print(f"   ❌ Error with PDF parser: {e}")
    sys.exit(1)

# Test 6: Validator
print("\n6️⃣ Testing validator...")
try:
    validator = InvoiceValidator()
    
    # Test valid data
    test_data = {
        'invoice_no': 'INV-001',
        'client_name': 'Test Client',
        'client_address': '123 Main St',
        'client_trn': '123456789',
        'date': '01/01/2026',
        'bo_no': 'BO001',
        'delivery_month': '01/2026',
        'description': 'Test Item',
        'quantity': 10,
        'rate': 100.0,
        'budget': 1000.0,
        'vat_rate': 5,
    }
    
    result = validator.validate_all(test_data)
    if result:
        print("   ✓ Validation passed for valid data")
    else:
        print(f"   ❌ Unexpected validation failure: {validator.get_errors()}")
except Exception as e:
    print(f"   ❌ Error with validator: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("✅ All tests passed successfully!")
print("="*50)
print("\nTo run the Streamlit UI, use:")
print("   streamlit run ui.py")
