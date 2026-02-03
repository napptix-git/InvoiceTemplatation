# 🚀 Quick Start Guide - Invoice Automation with BO Mapping

## Prerequisites

- Python 3.8+
- Virtual environment (recommended)

## Installation & Setup

### 1. Install Dependencies
```bash
cd invoice_automation
pip install -r requirements.txt
```

### 2. Run System Tests (Optional but Recommended)
```bash
python test_system.py
```

Expected output:
```
✅ All tests passed successfully!
```

### 3. Start the Application
```bash
streamlit run ui.py
```

Your browser will open to http://localhost:8501

## How to Use

### 📤 Step 1: Upload Business Order (BO)

There are three ways to load data:

#### Option A: PDF Upload (Recommended)
1. Prepare your PDF BO document
2. Click "Drag and drop or click to upload BO file"
3. Select your PDF
4. System automatically extracts:
   - BO Number
   - Client Name
   - Client TRN (VAT Number)
   - Descriptions
   - Quantities
   - Rates

#### Option B: Excel Upload
1. Create/prepare Excel file with BO data
2. Column names should match:
   - "Client Name", "TRN", "BO Number", "Description", "Quantity", "Rate"
3. Upload file
4. Auto-maps recognized columns

#### Option C: CSV Upload
1. Same as Excel but with CSV format
2. System will auto-map column names

### ✏️ Step 2: Fill Invoice Details

**Auto-Populated Fields (Locked):**
- Client Name (from BO)
- Client TRN (from BO)
- BO Number (from BO)
- Description (from BO)
- Quantity (from BO)
- Rate (from BO)

**Manual Entry Required:**
- **Invoice Number**: e.g., "001" (full: INV-FY2526-001)
- **Date**: Use calendar picker or type DD/MM/YYYY
- **Delivery Month**: Use calendar picker or type MM/YYYY
- **VAT Rate**: Select from dropdown (0% or 5%)

**Auto-Calculated:**
- Budget (Quantity × Rate ÷ 1000)
- VAT Amount (Budget × VAT Rate%)
- Total Amount (Budget + VAT)

### 👥 Step 3: Manage Clients (Optional)

If the extracted client name doesn't match a predefined client:

1. Click "➕ Add Client" button next to Client Name
2. Enter new client name (e.g., "New Company Ltd")
3. Click "Save Client"
4. New client is now permanently available in dropdown

**Predefined Clients:**
- Unilever Master - GCC
- AXE MALE DEODORANT 20
- Yazle Media
- Emirates Marketing Group
- Dubai Media Corporation
- ABC Trading LLC
- XYZ Distribution Company

### 📋 Step 4: Review Extracted Data

1. Expand "📋 View Extracted BO Data" section
2. Verify all extracted information
3. Check for multiple line items in "Additional Line Items"

### 💾 Step 5: Save Invoice

1. Click "💾 Save Invoice" button
2. System validates all data
3. If errors: Shows validation errors (fix them)
4. If success: Saves to `generated_invoices/INV-FY2526-XXX.xlsx`

### 🗑️ Step 6: Clear & Start Over (Optional)

Click "🗑️ Clear Fields" to:
- Reset all fields
- Unlock any auto-populated fields
- Clear line items
- Start with fresh form

## 📚 Viewing Extracted Data

### Expandable Sections

**1. "View Extracted BO Data"**
```
Shows:
- BO Number: PD25|2041|4
- Client Name: Yazle Marketing Management
- Client TRN: 100041432
- Line Items list
```

**2. "Additional Line Items"**
```
If BO has multiple items:
Item 2:
  - Description: Mixed Placement - ar, en - Saudi Arabia
  - Quantity: 14
  - Rate: 14.00
Item 3: ...
```

## 🔒 Field Locking Explained

**Locked Fields (Grayed Out):**
- Cannot be edited because they came from the BO file
- Prevents accidental changes to extracted data
- Preserved when saving invoice

**Unlocked Fields:**
- Can be freely edited
- Manual entry required

**To Unlock All Fields:**
- Click "🗑️ Clear Fields" button
- Upload a different/new BO file

## 📊 Summary Dashboard

Bottom section shows real-time calculations:
- **Budget**: Total × Volume ÷ 1000
- **VAT Type**: Selected option (GCC 5% or Non-GCC 0%)
- **VAT Amount**: Calculated tax
- **Total Amount**: Final invoice total

## 🆘 Troubleshooting

### PDF Not Extracting Data
**Issue**: PDF uploaded but says "PDF parsing library not installed"
**Solution**: 
```bash
pip install PyPDF2 pypdf
streamlit run ui.py
```

### Client Name Not Found
**Issue**: Your client isn't in the dropdown
**Solution**: 
1. Click "➕ Add Client"
2. Type exact client name
3. Click "Save Client"
4. Refresh page or re-upload BO

### Validation Error When Saving
**Issue**: Can't save invoice
**Solution**: Fix the highlighted errors
- Ensure Date is DD/MM/YYYY format
- Ensure Quantity and Rate are numbers > 0
- Check all required fields are filled

### Generated Invoice Location
**Path**: `invoice_automation/generated_invoices/`
**Example**: `INV-FY2526-001.xlsx`

## 📧 Sample Test Data

### Test PDF BO Format:
```
MEDIA BOOKING ORDER

Attention: Yazle Marketing Management
Client: Unilever Master - GCC
Order No: PD25|2041|4
Campaign: Unilever - Axe - 2025 - Digital Campaign

VAT REGISTRATION No. 100041432

Details | Volume | Date | Unit Cost | Net Cost | Taxes | Total
Mixed Placement - ar, en | 14 USD | 4-30 Sep | 14.00 USD | 5,000.00 USD | 5% VAT | 5,250.00 USD
```

### Test Excel BO Format:
```
Client Name | TRN | BO Number | Description | Quantity | Rate
Unilever Master - GCC | 100041432 | PD25|2041|4 | Campaign Services | 14 | 14.00
```

## ⚙️ Configuration

To modify field mappings, edit `config.py`:
- Cell references
- Field labels
- Validation rules
- Template file location

To modify client list, edit `clients.json`:
```json
{
  "predefined": ["Client 1", "Client 2", ...],
  "custom": ["My Client", ...]
}
```

## 📞 Support

For detailed technical information, see:
- `README.md` - Feature documentation
- `IMPLEMENTATION_GUIDE.md` - Technical details
- `IMPLEMENTATION_SUMMARY.md` - Complete overview

## ✅ Verification Checklist

Before using in production:
- [ ] All dependencies installed (`pip list` shows all packages)
- [ ] Tests pass (`python test_system.py`)
- [ ] Template file exists
- [ ] Can upload sample PDF/Excel/CSV
- [ ] Fields auto-populate correctly
- [ ] Can save invoice
- [ ] Generated file appears in `generated_invoices/`

---

**Ready to go!** 🎉

Questions? Check the documentation files or review IMPLEMENTATION_GUIDE.md for technical details.
