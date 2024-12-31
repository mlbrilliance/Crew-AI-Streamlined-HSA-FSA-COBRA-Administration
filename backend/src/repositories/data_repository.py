from typing import Dict, List, Any, Optional
from datetime import datetime
from ..services.database_service import DatabaseService

class DataRepository:
    """Repository class for handling data access operations."""
    
    def __init__(self):
        """Initialize the data repository."""
        self.db = DatabaseService()
    
    def get_employee_profile(self, employee_id: str) -> Dict[str, Any]:
        """
        Get comprehensive employee profile including all related data.
        
        Args:
            employee_id: The ID of the employee.
            
        Returns:
            Dict[str, Any]: Comprehensive employee profile data.
        """
        # Return mock data for testing
        return {
            "employee": {
                "name": "Emily Davis",
                "email": "emily.davis@example.com",
                "dob": "1995-09-30",
                "hsa_eligible": True,
                "fsa_eligible": False,
                "cobra_status": "not_applicable"
            },
            "dependents": [],
            "claims": [],
            "life_events": [],
            "cobra_events": [],
            "wellness_data": []
        }
    
    def get_employee_benefits_status(self, employee_id: str) -> Dict[str, Any]:
        """
        Get employee benefits eligibility status.
        
        Args:
            employee_id: The ID of the employee.
            
        Returns:
            Dict[str, Any]: Benefits eligibility status.
        """
        # Return mock data for testing
        return {
            "hsa_eligible": True,
            "fsa_eligible": False,
            "cobra_status": "not_applicable",
            "current_cobra_event": None
        }
    
    def get_employee_risk_assessment(self, employee_id: str) -> Dict[str, Any]:
        """
        Get employee health risk assessment based on wellness data.
        
        Args:
            employee_id: The ID of the employee.
            
        Returns:
            Dict[str, Any]: Health risk assessment data.
        """
        # Return mock data for testing
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "stress_level": 3,
                "sleep_hours": 7.5,
                "exercise_minutes": 45,
                "heart_rate": 72
            },
            "risk_factors": [],
            "consent_status": "approved"
        }
    
    def get_relevant_policies(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for relevant policy documents.
        
        Args:
            query: The search query.
            
        Returns:
            List[Dict[str, Any]]: List of relevant policy documents.
        """
        query = query.upper()
        
        # FSA Reimbursement Policy
        if "FSA" in query and "REIMBURSEMENT" in query:
            return [{
                "policy_id": "FSA-001",
                "policy_name": "FSA Reimbursement Guidelines",
                "version": "1.0",
                "policy_text": """
                FSA Reimbursement Guidelines:
                1. Eligible Expenses:
                   - Medical, dental, and vision care services
                   - Prescription medications
                   - Over-the-counter medicines with prescription
                   - Medical equipment and supplies
                
                2. Documentation Requirements:
                   - Original itemized receipts showing date, provider, service, and amount
                   - Explanation of Benefits (EOB) from insurance
                   - Prescription documentation for OTC medicines
                
                3. Submission Deadlines:
                   - Claims must be submitted within the plan year
                   - Grace period of 2.5 months after plan year ends
                   - Run-out period of 90 days to submit claims for previous year
                
                4. Reimbursement Process:
                   - Submit through online portal or mobile app
                   - Direct deposit available for faster reimbursement
                   - Processing typically takes 3-5 business days
                """
            }]
            
        # FSA Contribution Policy
        elif "FSA" in query and "CONTRIBUTION" in query:
            return [{
                "policy_id": "FSA-002",
                "policy_name": "FSA Contribution Guidelines",
                "version": "1.0",
                "policy_text": """
                FSA Contribution Guidelines:
                1. Annual Limits:
                   - Healthcare FSA: $3,200 for 2024
                   - Limited Purpose FSA: $3,200 for 2024
                   - Dependent Care FSA: $5,000 for 2024 (household limit)
                
                2. Changes Allowed:
                   - During annual open enrollment
                   - With qualifying life event (marriage, birth, etc.)
                   - Change must be consistent with the event
                
                3. Important Rules:
                   - Use-it-or-lose-it rule applies
                   - Changes cannot be retroactive
                   - Must remain in effect for full plan year
                   - Carryover may be available (up to $610 for 2024)
                """
            }]
            
        # HSA Policy (default)
        else:
            return [{
                "policy_id": "HSA-001",
                "policy_name": "HSA Eligibility Guidelines",
                "version": "1.0",
                "policy_text": """
                Health Savings Account (HSA) Eligibility Guidelines:
                1. Must be enrolled in a High Deductible Health Plan (HDHP)
                2. Cannot be enrolled in Medicare
                3. Cannot be claimed as a dependent on someone else's tax return
                4. Cannot have other health coverage that pays for out-of-pocket expenses before the deductible is met
                
                Annual contribution limits apply as set by the IRS.
                """
            }]
    
    def get_chat_context(self, employee_id: str) -> Dict[str, Any]:
        """
        Get chat context including employee info, benefits status, and chat history.
        
        Args:
            employee_id: The ID of the employee.
            
        Returns:
            Dict[str, Any]: Chat context data.
        """
        try:
            # Get employee profile
            profile = self.get_employee_profile(employee_id)
            
            # Get benefits status
            benefits_status = self.get_employee_benefits_status(employee_id)
            
            # Get chat history from database
            chat_history = self.get_chat_history(employee_id)
            
            return {
                "employee": profile.get("employee", {}),
                "benefits_status": benefits_status,
                "chat_history": chat_history
            }
        except Exception as e:
            print(f"Error getting chat context: {str(e)}")
            return {
                "employee": {
                    "name": "User",
                    "email": "",
                    "hsa_eligible": False,
                    "fsa_eligible": False,
                    "cobra_status": "unknown"
                },
                "benefits_status": {
                    "hsa_eligible": False,
                    "fsa_eligible": False,
                    "cobra_status": "unknown"
                },
                "chat_history": []
            }
            
    def get_chat_history(self, employee_id: str) -> List[Dict[str, Any]]:
        """
        Get chat history for an employee.
        
        Args:
            employee_id: The ID of the employee.
            
        Returns:
            List[Dict[str, Any]]: List of chat messages.
        """
        # In a real implementation, this would fetch from a database
        # For now, we'll use an in-memory store
        if not hasattr(self, '_chat_history'):
            self._chat_history = {}
        return self._chat_history.get(employee_id, [])
        
    def save_chat_interaction(self, employee_id: str, messages: List[Dict[str, str]]) -> bool:
        """
        Save a chat interaction to history.
        
        Args:
            employee_id: The ID of the employee.
            messages: List of chat messages.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            if not hasattr(self, '_chat_history'):
                self._chat_history = {}
            
            if employee_id not in self._chat_history:
                self._chat_history[employee_id] = []
                
            self._chat_history[employee_id].extend(messages)
            return True
        except Exception as e:
            print(f"Error saving chat interaction: {str(e)}")
            return False 