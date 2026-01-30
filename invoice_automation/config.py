"""
Configuration file for Invoice Template Automation
"""

# Template fields mapping
INVOICE_FIELDS = {
    'invoice_no': {
        'label': 'Invoice No.',
        'sheet': 'Invoice',
        'cell': 'F11',  # user requested
        'type': 'string'
    },
    'client_name': {
        'label': 'Client Name',
        'sheet': 'Invoice',
        'cell': 'C12',
        'type': 'string'
    },
    'client_address': {
        'label': 'Client Address',
        'sheet': 'Invoice',
        'cell': ['C13', 'C14', 'C15'],
        'type': 'string'
    },
    'client_trn': {
        'label': 'Client TRN No.',
        'sheet': 'Invoice',
        'cell': 'C16',
        'type': 'string'
    },
    'date': {
        'label': 'Date',
        'sheet': 'Invoice',
        'cell': 'F12',
        'type': 'date'
    },
    'due_date': {
        'label': 'Due Date',
        'sheet': 'Invoice',
        'cell': 'F13',
        'type': 'date'
    },
    'bo_no': {
        'label': 'BO No.',
        'sheet': 'Invoice',
        'cell': 'F15',
        'type': 'string'
    },
    'delivery_month': {
        'label': 'Delivery Month',
        'sheet': 'Invoice',
        'cell': 'F16',
        'type': 'string'
    },
    'quantity': {
        'label': 'Quantity',
        'sheet': 'Invoice',
        'cell': 'D21',
        'type': 'numeric'
    },
    'rate': {
        'label': 'Rate',
        'sheet': 'Invoice',
        'cell': 'E21',
        'type': 'numeric'
    },
    'budget': {
        'label': 'Budget',
        'sheet': 'Invoice',
        'cell': ['F21', 'F25'],
        'type': 'numeric'
    },
    'vat_rate': {
        'label': 'VAT Rate (%)',
        'sheet': 'Invoice',
        'cell': 'E26',
        'type': 'numeric',
        'validation': 'VAT should be 0% for Non-GCC or 5% for UAE'
    },
    'vat_amount': {
        'label': 'VAT Amount',
        'sheet': 'Invoice',
        'cell': 'F26',
        'type': 'numeric'
    },
    'total_amount': {
        'label': 'Total Amount',
        'sheet': 'Invoice',
        'cell': 'F27',
        'type': 'numeric',
        'read_only': True
    }
}

# File paths
TEMPLATE_FILE = '../Yazle_Invoice_Template_Final.xlsx'
OUTPUT_FOLDER = './generated_invoices/'

# Validation rules
VALIDATION_RULES = {
    'quantity': {'min': 0, 'max': None},
    'rate': {'min': 0, 'max': None},
    'budget': {'min': 0, 'max': None},
    'vat_rate': {'allowed_values': [0, 5]},
}
