# Technical Implementation Details

## Modified Files Summary

### 1. `clients.json` - Data Structure Change

**Old Format (Array):**
```json
{
  "predefined": [
    "Client Name 1",
    "Client Name 2"
  ],
  "custom": [
    "Custom Client 1"
  ]
}
```

**New Format (Dictionary with Key-Value Pairs):**
```json
{
  "predefined": {
    "Unilever Master - GCC": "Dubai Business Park, Dubai, UAE",
    "AXE MALE DEODORANT 20": "Jebel Ali, Dubai, UAE"
  },
  "custom": {
    "Optimum Media Direction FZ-LLC": "Optimum Media Office, Dubai, UAE"
  },
  "next_invoice_number": 1
}
```

**Key Changes:**
- `predefined` and `custom` changed from arrays to dictionaries
- Added `next_invoice_number` field to track invoice numbering
- Each client name now maps to their address
- Invoice number counter persists across sessions

---

## 2. `client_manager.py` - Class Updates

### New Methods Added:

#### `get_client_address(client_name: str) -> str`
```python
def get_client_address(self, client_name):
    """Get address for a specific client"""
    # Check predefined clients
    if client_name in self.clients.get('predefined', {}):
        return self.clients['predefined'][client_name]
    
    # Check custom clients
    if client_name in self.clients.get('custom', {}):
        return self.clients['custom'][client_name]
    
    return ""
```
**Purpose:** Retrieve the address associated with a client name  
**Returns:** Address string or empty string if client not found

#### `get_next_invoice_number() -> str`
```python
def get_next_invoice_number(self):
    """Get the next invoice number in format 001, 002, etc."""
    next_num = self.clients.get('next_invoice_number', 1)
    invoice_number = f"{next_num:03d}"
    return invoice_number
```
**Purpose:** Get the next invoice number to be used  
**Returns:** Zero-padded 3-digit string (001, 002, 003, etc.)

#### `increment_invoice_number()`
```python
def increment_invoice_number(self):
    """Increment the invoice number counter after saving an invoice"""
    current = self.clients.get('next_invoice_number', 1)
    self.clients['next_invoice_number'] = current + 1
    self._save_clients(self.clients)
```
**Purpose:** Increment the counter and persist to file  
**Called:** After successful invoice save

### Updated Methods:

#### `_load_clients()`
- Now handles dictionary format instead of arrays
- Ensures `next_invoice_number` field exists (defaults to 1)
- Backward compatible with old format (converts on load)

#### `get_all_clients() -> list`
```python
def get_all_clients(self):
    """Get all client names (predefined + custom) as a single list"""
    predefined = list(self.clients.get('predefined', {}).keys())
    custom = list(self.clients.get('custom', {}).keys())
    return predefined + custom
```
**Changed:** Now uses `.keys()` instead of treating as list

#### `add_custom_client(client_name: str, client_address: str = "") -> str`
```python
def add_custom_client(self, client_name, client_address=""):
    """Add a new custom client with address"""
    # ... validation ...
    self.clients['custom'][client_name] = client_address
    self._save_clients(self.clients)
    return client_name
```
**Changed:** Now accepts optional `client_address` parameter

#### `get_predefined_clients() -> list`
```python
def get_predefined_clients(self):
    """Get only predefined client names"""
    return list(self.clients.get('predefined', {}).keys())
```
**Changed:** Now extracts keys from dictionary instead of returning array

#### `get_custom_clients() -> list`
```python
def get_custom_clients(self):
    """Get only custom client names"""
    return list(self.clients.get('custom', {}).keys())
```
**Changed:** Now extracts keys from dictionary instead of returning array

---

## 3. `ui.py` - UI Component Changes

### Invoice Number Field Handling

**Before:**
```python
invoice_number = st.text_input(
    "Number",
    value=st.session_state.get(f"field_{field_key}", ""),
    placeholder=inv_val or "e.g., 001",
    key=f"field_{field_key}"
)
form_data[field_key] = (f"INV-FY2526-{invoice_number}" if str(invoice_number).strip() else "")
```

**After:**
```python
# Get next invoice number from ClientManager
if 'current_invoice_number' not in st.session_state:
    st.session_state.current_invoice_number = st.session_state.client_manager.get_next_invoice_number()

# Display auto-generated number (non-editable)
auto_invoice_num = st.session_state.current_invoice_number
st.text_input(
    "Number",
    value=auto_invoice_num,
    disabled=True,  # Non-editable
    key=f"field_{field_key}"
)
form_data[field_key] = f"INV-FY2526-{auto_invoice_num}"
```

**Key Changes:**
- Initialize `current_invoice_number` from ClientManager on app load
- Display with `disabled=True` to make non-editable
- Update form_data with auto-generated number

### Client Name Field Handling

**Added Auto-Population Logic:**
```python
# Auto-populate client address when client is selected
client_address = st.session_state.client_manager.get_client_address(selected_client)
if client_address:
    st.session_state['auto_client_address'] = client_address
```

**Updated Add Client Dialog:**
```python
new_address = st.text_input(
    "Enter client address:",
    key="new_client_address_input",
    placeholder="e.g., Dubai Business Park, Dubai, UAE"
)
# ...
st.session_state.client_manager.add_custom_client(new_client, new_address)
```

### New Client Address Field Handling

**Added new conditional block:**
```python
elif field_key == 'client_address':
    # Get auto-populated address from session state
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
```

### Save Invoice Button Enhancement

**Added after successful save:**
```python
# Increment invoice number after successful save
st.session_state.client_manager.increment_invoice_number()
st.session_state.current_invoice_number = st.session_state.client_manager.get_next_invoice_number()
```

**Purpose:** Increment counter and update session state for next invoice

### Clear Fields Button Enhancement

**Added to clear auto-populated address:**
```python
st.session_state.auto_client_address = ""
```

---

## Session State Variables

### New Variables:
- `current_invoice_number`: Stores the current invoice number (001, 002, etc.)
- `auto_client_address`: Stores the auto-populated address for the selected client
- `show_add_client`: Boolean flag for showing/hiding add client dialog

---

## Data Flow Diagram

```
User Opens App
    ↓
ClientManager.get_next_invoice_number() → "001"
    ↓
Invoice Number Field displays "001" (disabled)
    ↓
User selects Client
    ↓
ClientManager.get_client_address(client_name) → "Dubai Business Park, Dubai, UAE"
    ↓
Client Address Field auto-populates
    ↓
User fills remaining fields and clicks Save
    ↓
Invoice saved to Excel
    ↓
ClientManager.increment_invoice_number() → next_invoice_number becomes 2
    ↓
User creates next invoice
    ↓
Invoice Number Field displays "002" (disabled)
```

---

## Error Handling

### In ClientManager:
- `get_client_address()`: Returns empty string if client not found
- `add_custom_client()`: Raises `ValueError` for empty names or duplicates
- `get_next_invoice_number()`: Defaults to 1 if field missing
- `increment_invoice_number()`: Safely handles missing field

### In UI:
- Try-catch blocks preserve existing error handling
- Auto-population fails gracefully (shows empty field)
- Save still works even if address doesn't auto-populate

---

## Testing Code Examples

### Test Invoice Numbering Persistence:
```python
from client_manager import ClientManager

cm = ClientManager()
print(f"Current: {cm.get_next_invoice_number()}")  # 001

cm.increment_invoice_number()
print(f"After increment: {cm.get_next_invoice_number()}")  # 002

# Create new instance - should remember the value
cm2 = ClientManager()
print(f"New instance: {cm2.get_next_invoice_number()}")  # 002
```

### Test Client Address Retrieval:
```python
from client_manager import ClientManager

cm = ClientManager()

# Test predefined client
addr = cm.get_client_address("Unilever Master - GCC")
assert addr == "Dubai Business Park, Dubai, UAE"

# Test non-existent client
addr = cm.get_client_address("Non Existent Client")
assert addr == ""

# Test custom client
cm.add_custom_client("Test Company", "Test Address")
addr = cm.get_client_address("Test Company")
assert addr == "Test Address"
```

### Test Add Client with Address:
```python
from client_manager import ClientManager

cm = ClientManager()

# Add new client
cm.add_custom_client("New Client Ltd", "New Address, City, Country")

# Verify it's in the list
clients = cm.get_all_clients()
assert "New Client Ltd" in clients

# Verify address is stored
addr = cm.get_client_address("New Client Ltd")
assert addr == "New Address, City, Country"

# Verify it persists
cm2 = ClientManager()
assert "New Client Ltd" in cm2.get_all_clients()
```

---

## Compatibility Notes

### Backward Compatibility:
- App checks for `next_invoice_number` field and defaults to 1 if missing
- Old array format would need migration (one-time conversion recommended)
- All existing functionality preserved

### Forward Compatibility:
- Structure designed to easily add more client metadata (phone, email, etc.)
- Invoice numbering allows up to 999 invoices before requiring format change

---

## Performance Considerations

- All client data loaded into memory (suitable for < 1000 clients)
- File I/O only on save operations (efficient)
- No database required - JSON file is sufficient
- Address lookup is O(1) dictionary lookup

---

## Future Enhancements

Possible improvements built on this foundation:
- Add phone number and email to clients
- Add client TRN field to client data (auto-populate TRN too)
- Add client category/type field
- Implement invoice number format customization
- Add client archival instead of deletion
- Add client audit trail/change history
