from typing import Dict, List, Any, Optional
from datetime import datetime
from ..config.supabase import SupabaseClient

class DatabaseService:
    """Service class for handling database operations."""
    
    def __init__(self):
        """Initialize the database service with Supabase client."""
        self.supabase = SupabaseClient().client
    
    def get_employee(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """
        Get employee data by ID.
        
        Args:
            employee_id: The ID of the employee.
            
        Returns:
            Optional[Dict[str, Any]]: Employee data if found, None otherwise.
        """
        try:
            response = self.supabase.table('mock_employees') \
                .select('*') \
                .eq('employee_id', employee_id) \
                .limit(1) \
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting employee: {str(e)}")
            return None
    
    def get_benefits_status(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """
        Get employee benefits status by ID.
        
        Args:
            employee_id: The ID of the employee.
            
        Returns:
            Optional[Dict[str, Any]]: Benefits status if found, None otherwise.
        """
        try:
            response = self.supabase.table('mock_employees') \
                .select('hsa_eligible,fsa_eligible,cobra_status') \
                .eq('employee_id', employee_id) \
                .limit(1) \
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting benefits status: {str(e)}")
            return None
    
    def get_chat_history(self, employee_id: str) -> List[Dict[str, Any]]:
        """
        Get chat history for an employee.
        
        Args:
            employee_id: The ID of the employee.
            
        Returns:
            List[Dict[str, Any]]: List of chat history records.
        """
        try:
            response = self.supabase.table('mock_chat_history') \
                .select('chat_history') \
                .eq('employee_id', employee_id) \
                .order('timestamp', desc=True) \
                .limit(1) \
                .execute()
            
            if response.data and response.data[0].get('chat_history'):
                return response.data[0]['chat_history']
            return []
        except Exception as e:
            print(f"Error getting chat history: {str(e)}")
            return []
    
    def save_chat(self, employee_id: str, messages: List[Dict[str, str]]) -> bool:
        """
        Save chat messages to history.
        
        Args:
            employee_id: The ID of the employee.
            messages: List of chat messages.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            response = self.supabase.table('mock_chat_history') \
                .upsert({
                    'employee_id': employee_id,
                    'chat_history': messages,
                    'timestamp': datetime.now().isoformat()
                }) \
                .execute()
            
            return bool(response.data)
        except Exception as e:
            print(f"Error saving chat: {str(e)}")
            return False 