from typing import Dict, List, Any, Optional
from datetime import datetime
from ..services.database_service import DatabaseService
from ..config.supabase import SupabaseClient

class DataRepository:
    """Repository class for handling data access operations."""
    
    def __init__(self):
        """Initialize the data repository."""
        self.db = DatabaseService()
        self.supabase = SupabaseClient().client
    
    def get_employee_profile(self, employee_id: str) -> Dict[str, Any]:
        """
        Get comprehensive employee profile including all related data from Supabase.
        
        Args:
            employee_id: The ID of the employee.
            
        Returns:
            Dict[str, Any]: Comprehensive employee profile data.
        """
        try:
            print(f"\n=== Getting employee profile for {employee_id} ===")
            
            # Get employee basic info
            print("\nFetching employee basic info...")
            employee_response = self.supabase.table('mock_employees') \
                .select('*') \
                .eq('employee_id', employee_id) \
                .limit(1) \
                .execute()
                
            print(f"\nEmployee response from Supabase: {employee_response.data}")
                
            if not employee_response.data:
                print(f"No employee found with ID {employee_id}")
                return {}
                
            employee = employee_response.data[0]
            print(f"\nFound employee data:")
            print(f"Name: {employee.get('name')}")
            print(f"Email: {employee.get('email')}")
            print(f"DOB: {employee.get('dob')}")
            print(f"HSA Eligible: {employee.get('hsa_eligible')}")
            print(f"FSA Eligible: {employee.get('fsa_eligible')}")
            print(f"COBRA Status: {employee.get('cobra_status')}")
            
            # Get dependents
            print("\nFetching dependents...")
            dependents_response = self.supabase.table('mock_employee_dependents') \
                .select('*') \
                .eq('employee_id', employee_id) \
                .execute()
            dependents = dependents_response.data
            print(f"\nDependents from Supabase: {dependents}")
            
            # Get claims
            print("\nFetching claims...")
            claims_response = self.supabase.table('mock_claims') \
                .select('*') \
                .eq('employee_id', employee_id) \
                .execute()
            claims = claims_response.data
            print(f"\nClaims from Supabase: {claims}")
            
            # Get life events
            print("\nFetching life events...")
            life_events_response = self.supabase.table('mock_life_events') \
                .select('*') \
                .eq('employee_id', employee_id) \
                .execute()
            life_events = life_events_response.data
            print(f"\nLife events from Supabase: {life_events}")
            
            # Get COBRA events
            print("\nFetching COBRA events...")
            cobra_events_response = self.supabase.table('mock_cobra_events') \
                .select('*') \
                .eq('employee_id', employee_id) \
                .execute()
            cobra_events = cobra_events_response.data
            print(f"\nCOBRA events from Supabase: {cobra_events}")
            
            # Get wellness data
            print("\nFetching wellness data...")
            wellness_response = self.supabase.table('mock_wellness_data') \
                .select('*') \
                .eq('employee_id', employee_id) \
                .order('timestamp', desc=True) \
                .limit(1) \
                .execute()
            wellness_data = wellness_response.data[0] if wellness_response.data else {}
            print(f"\nWellness data from Supabase: {wellness_data}")
            
            # Construct the complete profile
            profile = {
                "employee": {
                    "name": employee.get('name'),
                    "email": employee.get('email'),
                    "dob": employee.get('dob'),
                    "hsa_eligible": employee.get('hsa_eligible'),
                    "fsa_eligible": employee.get('fsa_eligible'),
                    "cobra_status": employee.get('cobra_status')
                },
                "dependents": dependents,
                "claims": claims,
                "life_events": life_events,
                "cobra_events": cobra_events,
                "wellness_data": wellness_data
            }
            
            print("\nReturning complete profile:")
            print(f"Profile: {profile}")
            return profile
            
        except Exception as e:
            print(f"\n=== Error in get_employee_profile ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print(f"Employee ID: {employee_id}")
            
            # Return a minimal profile on error
            return {
                "employee": {
                    "name": "Unknown",
                    "email": "",
                    "dob": "",
                    "hsa_eligible": False,
                    "fsa_eligible": False,
                    "cobra_status": "unknown"
                },
                "dependents": [],
                "claims": [],
                "life_events": [],
                "cobra_events": [],
                "wellness_data": {}
            }
    
    def get_employee_benefits_status(self, employee_id: str) -> Dict[str, Any]:
        """
        Get employee benefits eligibility status from Supabase.
        
        Args:
            employee_id: The ID of the employee.
            
        Returns:
            Dict[str, Any]: Benefits eligibility status.
        """
        try:
            print(f"\n=== Getting benefits status for {employee_id} ===")
            
            # Get employee basic info for HSA/FSA eligibility
            print("\nFetching employee benefits info...")
            employee_response = self.supabase.table('mock_employees') \
                .select('hsa_eligible,fsa_eligible,cobra_status') \
                .eq('employee_id', employee_id) \
                .limit(1) \
                .execute()
                
            print(f"\nEmployee benefits response from Supabase: {employee_response.data}")
            
            if not employee_response.data:
                print(f"No employee found with ID {employee_id}")
                return {
                    "hsa_eligible": False,
                    "fsa_eligible": False,
                    "cobra_status": "unknown",
                    "current_cobra_event": None
                }
            
            employee = employee_response.data[0]
            
            # Get current COBRA event if any
            print("\nFetching current COBRA event...")
            cobra_response = self.supabase.table('mock_cobra_events') \
                .select('*') \
                .eq('employee_id', employee_id) \
                .order('event_date', desc=True) \
                .limit(1) \
                .execute()
                
            print(f"\nCOBRA event response from Supabase: {cobra_response.data}")
            
            current_cobra_event = cobra_response.data[0] if cobra_response.data else None
            
            # Construct benefits status
            benefits_status = {
                "hsa_eligible": employee.get('hsa_eligible', False),
                "fsa_eligible": employee.get('fsa_eligible', False),
                "cobra_status": employee.get('cobra_status', 'unknown'),
                "current_cobra_event": current_cobra_event
            }
            
            print(f"\nReturning benefits status: {benefits_status}")
            return benefits_status
            
        except Exception as e:
            print(f"\n=== Error in get_employee_benefits_status ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print(f"Employee ID: {employee_id}")
            
            # Return safe defaults on error
            return {
                "hsa_eligible": False,
                "fsa_eligible": False,
                "cobra_status": "unknown",
                "current_cobra_event": None
            }
    
    def get_employee_risk_assessment(self, employee_id: str) -> Dict[str, Any]:
        """
        Get employee risk assessment based on wellness data.
        
        Args:
            employee_id: The ID of the employee.
            
        Returns:
            Dict[str, Any]: Risk assessment data including metrics, risk factors, and recommendations.
        """
        try:
            print(f"\n=== Getting risk assessment for employee {employee_id} ===")
            
            # Get latest wellness data
            print("\nFetching wellness data from Supabase...")
            response = self.supabase.table('mock_wellness_data') \
                .select('*') \
                .eq('employee_id', employee_id) \
                .order('timestamp', desc=True) \
                .limit(1) \
                .execute()
                
            print(f"\nWellness data response: {response.data}")
            
            if not response.data:
                print("No wellness data found")
                return {
                    "timestamp": None,
                    "metrics": {},
                    "risk_factors": [],
                    "recommendations": []
                }
            
            wellness_data = response.data[0]
            metrics = wellness_data.get('metrics', {})
            risk_factors = wellness_data.get('risk_factors', [])
            
            # Generate recommendations based on metrics
            recommendations = []
            
            # Check stress level
            stress_level = metrics.get('stress_level')
            if stress_level and stress_level > 6:
                recommendations.append({
                    "category": "stress_management",
                    "message": "Your stress levels are elevated. Consider stress management techniques like meditation or speaking with a counselor."
                })
            
            # Check sleep
            sleep_hours = metrics.get('sleep_hours')
            if sleep_hours and sleep_hours < 7:
                recommendations.append({
                    "category": "sleep_improvement",
                    "message": "You're getting less than recommended sleep. Try to establish a regular sleep schedule and aim for 7-9 hours per night."
                })
            
            # Check exercise
            exercise_minutes = metrics.get('exercise_minutes')
            if exercise_minutes and exercise_minutes < 30:
                recommendations.append({
                    "category": "exercise",
                    "message": "Consider increasing your daily physical activity. Aim for at least 30 minutes of moderate exercise most days."
                })
            
            # Check steps
            steps = metrics.get('steps')
            if steps and steps < 8000:
                recommendations.append({
                    "category": "activity",
                    "message": "Try to increase your daily step count. A goal of 10,000 steps per day can improve overall health."
                })
            
            print(f"\nGenerated {len(recommendations)} recommendations")
            
            return {
                "timestamp": wellness_data.get('timestamp'),
                "metrics": metrics,
                "risk_factors": risk_factors,
                "recommendations": recommendations
            }
            
        except Exception as e:
            print(f"\n=== Error in get_employee_risk_assessment ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print(f"Employee ID: {employee_id}")
            
            # Return empty assessment on error
            return {
                "timestamp": None,
                "metrics": {},
                "risk_factors": [],
                "recommendations": []
            }
    
    def get_relevant_policies(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for relevant policy documents from Supabase.
        
        Args:
            query: The search query.
            
        Returns:
            List[Dict[str, Any]]: List of relevant policy documents.
        """
        try:
            print(f"\n=== Getting relevant policies for query: {query} ===")
            query = query.upper()
            
            # Search in mock_policies table
            print("\nSearching policies in Supabase...")
            response = self.supabase.table('mock_policies') \
                .select('*') \
                .execute()
                
            print(f"\nPolicy response from Supabase: {response.data}")
            
            if not response.data:
                print("No policies found")
                return []
            
            # Filter policies based on query
            relevant_policies = []
            for policy in response.data:
                policy_text = policy.get('policy_text', '').upper()
                policy_name = policy.get('policy_name', '').upper()
                
                # Check if query terms match policy text or name
                if any(term in policy_text or term in policy_name 
                      for term in query.split()):
                    relevant_policies.append({
                        "policy_id": policy.get('policy_id'),
                        "policy_name": policy.get('policy_name'),
                        "version": policy.get('version'),
                        "policy_text": policy.get('policy_text')
                    })
            
            print(f"\nFound {len(relevant_policies)} relevant policies")
            return relevant_policies
            
        except Exception as e:
            print(f"\n=== Error in get_relevant_policies ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print(f"Query: {query}")
            
            # Return empty list on error
            return []
    
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
        Get chat history for an employee from Supabase.
        
        Args:
            employee_id: The ID of the employee.
            
        Returns:
            List[Dict[str, Any]]: List of chat messages.
        """
        try:
            print(f"\n=== Starting get_chat_history ===")
            print(f"Employee ID: {employee_id}")
            
            # Query Supabase for chat history
            print("\nQuerying Supabase for chat history...")
            response = self.supabase.table('mock_chat_history') \
                .select('chat_history') \
                .eq('employee_id', employee_id) \
                .order('timestamp', desc=True) \
                .limit(1) \
                .execute()
            
            print(f"Supabase response: {response}")
            
            # Check if we got any data
            if response.data and len(response.data) > 0:
                print("\nFound chat history data")
                # Parse the chat_history JSON field
                chat_history = response.data[0].get('chat_history', [])
                if isinstance(chat_history, str):
                    print("Converting chat history from string to JSON")
                    import json
                    chat_history = json.loads(chat_history)
                print(f"Returning chat history with {len(chat_history)} messages")
                return chat_history
            
            print("\nNo chat history found, returning empty list")
            return []
            
        except Exception as e:
            print(f"\n=== Error in get_chat_history ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print(f"Employee ID: {employee_id}")
            return []
        
    def save_chat_interaction(self, employee_id: str, messages: List[Dict[str, Any]]) -> bool:
        """
        Save a chat interaction to Supabase.
        
        Args:
            employee_id: The ID of the employee.
            messages: List of chat messages in either format:
                     - {"role": "user/assistant", "content": "message"}
                     - {"id": "...", "text": "message", "sender": "user/assistant", "timestamp": "..."}
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            print(f"\n=== Starting save_chat_interaction ===")
            print(f"Employee ID: {employee_id}")
            print(f"New messages to save: {messages}")
            
            # Get existing chat history first
            print("\nFetching existing chat history...")
            response = self.supabase.table('mock_chat_history') \
                .select('chat_history') \
                .eq('employee_id', employee_id) \
                .order('timestamp', desc=True) \
                .limit(1) \
                .execute()
            
            print(f"Supabase select response: {response}")
            
            existing_messages = []
            if response.data and len(response.data) > 0:
                print("\nFound existing chat history")
                chat_history = response.data[0].get('chat_history', {})
                if isinstance(chat_history, str):
                    print("Converting chat history from string to JSON")
                    import json
                    chat_history = json.loads(chat_history)
                
                # Extract messages from the chat_history dictionary
                if isinstance(chat_history, dict) and 'messages' in chat_history:
                    existing_messages = chat_history.get('messages', [])
                else:
                    existing_messages = []
                print(f"Existing messages: {existing_messages}")
            else:
                print("\nNo existing chat history found")
            
            # Normalize message format
            normalized_messages = []
            for msg in messages:
                if "role" in msg and "content" in msg:
                    # Convert from role/content format to id/text/sender format
                    normalized_msg = {
                        "role": msg["role"],
                        "content": msg["content"],
                        "timestamp": datetime.now().isoformat()
                    }
                    if "details" in msg:
                        normalized_msg["details"] = msg["details"]
                    if "suggestions" in msg:
                        normalized_msg["suggestions"] = msg["suggestions"]
                else:
                    # Already in the correct format
                    normalized_msg = msg
                normalized_messages.append(normalized_msg)
            
            # Combine existing and new messages
            updated_messages = existing_messages + normalized_messages
            print(f"\nCombined messages count: {len(updated_messages)}")
            
            # Save to Supabase with the correct structure
            data = {
                'employee_id': employee_id,
                'chat_history': {'messages': updated_messages},
                'timestamp': datetime.now().isoformat()
            }
            print(f"\nPrepared data for Supabase: {data}")
            
            # Upsert the data (insert or update if exists)
            print("\nAttempting to upsert data to Supabase...")
            response = self.supabase.table('mock_chat_history') \
                .upsert(data) \
                .execute()
            
            print(f"Supabase upsert response: {response}")
            success = bool(response.data)
            print(f"Operation {'successful' if success else 'failed'}")
            return success
            
        except Exception as e:
            print(f"\n=== Error in save_chat_interaction ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print(f"Employee ID: {employee_id}")
            print(f"Messages: {messages}")
            return False 