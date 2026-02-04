# Quick Reference: New Features

## 🔢 Invoice Number Auto-Increment

### What Changed?
- Invoice numbers are now **automatically generated** (001, 002, 003...)
- You **cannot edit** the invoice number manually
- The number **automatically increments** after each save

### How to Use:
1. Open the app → See invoice number "001" (read-only)
2. Fill in your invoice details
3. Click "💾 Save Invoice"
4. Next invoice will automatically show "002"
5. Keep creating invoices - numbers continue: 003, 004, 005...

### Format:
```
Invoice No: INV-FY2526-001  (first invoice)
            INV-FY2526-002  (second invoice)
            INV-FY2526-003  (third invoice)
            etc...
```

---

## 📍 Client Addresses (Auto-Populated)

### What Changed?
- Each client now has an address stored in the system
- When you select a client, the address **automatically fills in**
- You can still manually edit the address if needed
- When adding a new client, you provide both name AND address

### How to Use:

#### Selecting an Existing Client:
1. Click on "Client Name" dropdown
2. Select a client (e.g., "Unilever Master - GCC")
3. The "Client Address" field **automatically fills in** with the stored address
4. The address appears in the form - you can edit it if needed

#### Adding a New Client:
1. Click the "➕ Add Client" button
2. Enter client name (e.g., "My New Company")
3. Enter client address (e.g., "Dubai Investment Park, Dubai, UAE")
4. Click "Save Client"
5. The new client is added to the dropdown with its address stored
6. Next time you select this client, the address will auto-populate

### Predefined Clients with Addresses:
- **Unilever Master - GCC** → Dubai Business Park, Dubai, UAE
- **AXE MALE DEODORANT 20** → Jebel Ali, Dubai, UAE
- **Yazle Media** → Jumeirah Business Centre, Dubai, UAE
- **Emirates Marketing Group** → Media City, Dubai, UAE
- **Dubai Media Corporation** → Downtown Dubai, Dubai, UAE
- **ABC Trading LLC** → Dubai Investment Park, Dubai, UAE
- **XYZ Distribution Company** → Free Zone, Dubai, UAE

---

## 🎯 Benefits

### Invoice Numbering:
✅ No more manual number entry  
✅ No duplicate invoice numbers  
✅ No forgetting what number you're on  
✅ Automatic progression  

### Client Addresses:
✅ Less typing - address appears automatically  
✅ Consistency - same client = same address  
✅ Easy to add new clients with their addresses  
✅ Quick data entry  

---

## 📝 Example Workflow

### Step 1: Open Invoice Creator
```
Invoice No: INV-FY2526-001  [READ-ONLY]
Client Name: [Select from dropdown]
Client Address: [Auto-fills when you select client]
```

### Step 2: Select a Client
```
Client Name: Unilever Master - GCC  ← You click here
↓
Client Address: Dubai Business Park, Dubai, UAE  ← Auto-fills!
```

### Step 3: Complete Other Fields and Save
```
- Fill in Date, Description, Quantity, Rate
- Click "💾 Save Invoice"
- Invoice saved!
```

### Step 4: Create Next Invoice
```
Invoice No: INV-FY2526-002  ← Number auto-incremented!
```

---

## ❓ FAQ

**Q: Can I change the invoice number?**  
A: No, the number is read-only and auto-generated for consistency and uniqueness.

**Q: Can I edit the auto-populated address?**  
A: Yes! You can always manually edit the address field if needed. The auto-population just fills it in for convenience.

**Q: What if I want to reset the invoice counter?**  
A: Edit the `clients.json` file and change the `"next_invoice_number"` value to any number you want.

**Q: Can I add multiple invoices with the same client?**  
A: Yes! Each invoice gets a unique number (001, 002, 003...) regardless of which client it's for.

**Q: What happens if I clear fields?**  
A: The invoice number doesn't change - only other fields are cleared. The counter stays with its current value.

**Q: Can custom clients have addresses too?**  
A: Yes! When you add a custom client, you provide the address along with the name.

---

## 💾 Data Persistence

All data is stored in `clients.json`:
- Client names and their addresses
- Invoice number counter
- Automatically saved when you:
  - Add a new client
  - Save an invoice (counter increments)

The data persists even if you close and reopen the app.

---

## 🔄 Reset Instructions

If you want to start fresh:

### Reset Invoice Counter to 001:
1. Open `invoice_automation/clients.json`
2. Find `"next_invoice_number": X`
3. Change it to `"next_invoice_number": 1`
4. Save the file
5. Next invoice will be 001

### Reset Clients and Addresses:
Contact your administrator - ask them to restore the default `clients.json`.
