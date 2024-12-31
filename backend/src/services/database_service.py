from typing import Dict, List, Any, Optional
from datetime import datetime

class DatabaseService:
    """Service class for handling database operations."""
    
    def __init__(self):
        """Initialize the database service with mock data."""
        # Initialize with mock data
        self.mock_data = {
            "employees": {
                "emp001": {
                    "name": "Emily Davis",
                    "email": "emily.davis@example.com",
                    "dob": "1995-09-30",
                    "hsa_eligible": True,
                    "fsa_eligible": False,
                    "cobra_status": "not_applicable"
                }
            },
            "chat_history": {},
            "benefits_status": {
                "emp001": {
                    "hsa_eligible": True,
                    "fsa_eligible": False,
                    "cobra_status": "not_applicable"
                }
            }
        }
    
    def get_employee(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """
        Get employee data by ID.
        
        Args:
            employee_id: The ID of the employee.
            
        Returns:
            Optional[Dict[str, Any]]: Employee data if found, None otherwise.
        """
        return self.mock_data["employees"].get(employee_id)
    
    def get_benefits_status(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """
        Get employee benefits status by ID.
        
        Args:
            employee_id: The ID of the employee.
            
        Returns:
            Optional[Dict[str, Any]]: Benefits status if found, None otherwise.
        """
        return self.mock_data["benefits_status"].get(employee_id)
    
    def get_chat_history(self, employee_id: str) -> List[Dict[str, Any]]:
        """
        Get chat history for an employee.
        
        Args:
            employee_id: The ID of the employee.
            
        Returns:
            List[Dict[str, Any]]: List of chat history records.
        """
        return self.mock_data["chat_history"].get(employee_id, [])
    
    def save_chat(self, employee_id: str, messages: List[Dict[str, str]]) -> bool:
        """
        Save chat messages to history.
        
        Args:
            employee_id: The ID of the employee.
            messages: List of chat messages.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if employee_id not in self.mock_data["chat_history"]:
            self.mock_data["chat_history"][employee_id] = []
            
        self.mock_data["chat_history"][employee_id].extend(messages)
        return True 