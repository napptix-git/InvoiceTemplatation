"""
Client management system for invoice automation
Manages predefined client names and custom client additions
"""

import json
import os
from config import BASE_DIR


class ClientManager:
    """Manage client names - predefined and custom"""
    
    def __init__(self):
        self.clients_file = os.path.join(BASE_DIR, 'clients.json')
        self.clients = self._load_clients()
    
    def _load_clients(self):
        """Load clients from JSON file"""
        default_clients = {
            "predefined": [
                "Unilever Master - GCC",
                "AXE MALE DEODORANT 20",
                "Yazle Media",
                "Emirates Marketing Group",
                "Dubai Media Corporation",
                "ABC Trading LLC",
                "XYZ Distribution Company"
            ],
            "custom": []
        }
        
        if os.path.exists(self.clients_file):
            try:
                with open(self.clients_file, 'r') as f:
                    return json.load(f)
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
        """Get all clients (predefined + custom) as a single list"""
        return self.clients.get('predefined', []) + self.clients.get('custom', [])
    
    def add_custom_client(self, client_name):
        """Add a new custom client"""
        if not client_name or client_name.strip() == '':
            raise ValueError("Client name cannot be empty")
        
        client_name = client_name.strip()
        
        # Check if already exists
        all_clients = self.get_all_clients()
        if client_name in all_clients:
            raise ValueError(f"Client '{client_name}' already exists")
        
        # Add to custom list
        self.clients['custom'].append(client_name)
        self._save_clients(self.clients)
        return client_name
    
    def remove_custom_client(self, client_name):
        """Remove a custom client"""
        if client_name in self.clients.get('custom', []):
            self.clients['custom'].remove(client_name)
            self._save_clients(self.clients)
            return True
        return False
    
    def get_predefined_clients(self):
        """Get only predefined clients"""
        return self.clients.get('predefined', [])
    
    def get_custom_clients(self):
        """Get only custom clients"""
        return self.clients.get('custom', [])
