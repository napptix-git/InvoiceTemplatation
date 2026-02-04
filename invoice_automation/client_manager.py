"""
Client management system for invoice automation
Manages predefined client names with addresses and custom client additions
"""

import json
import os
from config import BASE_DIR


class ClientManager:
    """Manage client names with addresses and invoice numbering"""
    
    def __init__(self):
        self.clients_file = os.path.join(BASE_DIR, 'clients.json')
        self.clients = self._load_clients()
    
    def _load_clients(self):
        """Load clients from JSON file"""
        default_clients = {
            "predefined": {
                "Unilever Master - GCC": "Dubai Business Park, Dubai, UAE",
                "AXE MALE DEODORANT 20": "Jebel Ali, Dubai, UAE",
                "Yazle Media": "Jumeirah Business Centre, Dubai, UAE",
                "Emirates Marketing Group": "Media City, Dubai, UAE",
                "Dubai Media Corporation": "Downtown Dubai, Dubai, UAE",
                "ABC Trading LLC": "Dubai Investment Park, Dubai, UAE",
                "XYZ Distribution Company": "Free Zone, Dubai, UAE"
            },
            "custom": {
                "Optimum Media Direction FZ-LLC": "Optimum Media Office, Dubai, UAE"
            },
            "next_invoice_number": 1
        }
        
        if os.path.exists(self.clients_file):
            try:
                with open(self.clients_file, 'r') as f:
                    loaded = json.load(f)
                    # Ensure next_invoice_number exists
                    if 'next_invoice_number' not in loaded:
                        loaded['next_invoice_number'] = 1
                    return loaded
            except Exception:
                return default_clients
        else:
            # Create file with defaults
            self._save_clients(default_clients)
            return default_clients
    
    def _save_clients(self, clients):
        """Save clients to JSON file"""
        try:
            with open(self.clients_file, 'w') as f:
                json.dump(clients, f, indent=2)
        except Exception as e:
            raise Exception(f"Error saving clients: {str(e)}")
    
    def get_all_clients(self):
        """Get all client names (predefined + custom) as a single list"""
        predefined = list(self.clients.get('predefined', {}).keys())
        custom = list(self.clients.get('custom', {}).keys())
        return predefined + custom
    
    def get_client_address(self, client_name):
        """Get address for a specific client"""
        # Check predefined clients
        if client_name in self.clients.get('predefined', {}):
            return self.clients['predefined'][client_name]
        
        # Check custom clients
        if client_name in self.clients.get('custom', {}):
            return self.clients['custom'][client_name]
        
        return ""
    
    def add_custom_client(self, client_name, client_address=""):
        """Add a new custom client with address"""
        if not client_name or client_name.strip() == '':
            raise ValueError("Client name cannot be empty")
        
        client_name = client_name.strip()
        client_address = client_address.strip() if client_address else ""
        
        # Check if already exists
        all_clients = self.get_all_clients()
        if client_name in all_clients:
            raise ValueError(f"Client '{client_name}' already exists")
        
        # Add to custom list
        self.clients['custom'][client_name] = client_address
        self._save_clients(self.clients)
        return client_name
    
    def remove_custom_client(self, client_name):
        """Remove a custom client"""
        if client_name in self.clients.get('custom', {}):
            del self.clients['custom'][client_name]
            self._save_clients(self.clients)
            return True
        return False
    
    def get_predefined_clients(self):
        """Get only predefined client names"""
        return list(self.clients.get('predefined', {}).keys())
    
    def get_custom_clients(self):
        """Get only custom client names"""
        return list(self.clients.get('custom', {}).keys())
    
    def get_next_invoice_number(self):
        """Get the next invoice number in format 001, 002, etc."""
        next_num = self.clients.get('next_invoice_number', 1)
        invoice_number = f"{next_num:03d}"
        return invoice_number
    
    def increment_invoice_number(self):
        """Increment the invoice number counter after saving an invoice"""
        current = self.clients.get('next_invoice_number', 1)
        self.clients['next_invoice_number'] = current + 1
        self._save_clients(self.clients)

