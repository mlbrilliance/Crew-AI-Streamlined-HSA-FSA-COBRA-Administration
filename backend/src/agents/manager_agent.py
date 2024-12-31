from typing import Dict, Any, List, Optional
from crewai import Agent, Task, Crew
from .eligibility_agent import EligibilityAgent
from ..repositories.data_repository import DataRepository
import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
import json

class ManagerAgent:
    """Agent responsible for managing and coordinating benefits analysis tasks."""
    
    def __init__(self):
        """Initialize the ManagerAgent."""
        # Load environment variables
        load_dotenv(find_dotenv())
        
        # Get API key and print debug info
        openai_api_key = os.getenv("OPENAI_API_KEY")
        print(f"Debug - Manager Agent - API Key exists: {bool(openai_api_key)}")
        print(f"Debug - Manager Agent - API Key length: {len(openai_api_key) if openai_api_key else 0}")
        print(f"Debug - Manager Agent - Current working directory: {os.getcwd()}")
        
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Initialize eligibility agent
        self.eligibility_agent = EligibilityAgent()
        
        # Initialize the base Agent
        self.agent = Agent(
            role='Benefits Expert',
            goal='Provide detailed, personalized benefits guidance',
            backstory="""You are a senior benefits advisor with deep expertise in HSA, FSA, and COBRA benefits. 
            Your responses must be detailed, personalized, and actionable. Never use generic phrases like 'I understand your query.'
            Instead, you provide specific information based on the employee's situation and eligibility status.
            
            When comparing HSA and FSA, you always mention these key differences:
            1. Ownership and portability
            2. Contribution limits and changes
            3. Rollover rules
            4. Eligibility requirements
            5. Use with other accounts
            6. Tax advantages""",
            verbose=True,
            allow_delegation=False,
            llm=ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
                api_key=openai_api_key
            )
        )
    
    async def analyze_query(self, employee_id: str, query: str) -> Dict[str, Any]:
        """
        Analyze a benefits query by coordinating with specialized agents.
        
        Args:
            employee_id: The ID of the employee.
            query: The benefits query to analyze.
            
        Returns:
            Dict[str, Any]: Analysis results and recommendations.
        """
        try:
            # Create data repository instance
            data_repo = DataRepository()
            
            # Get employee context and additional data
            context = data_repo.get_chat_context(employee_id)
            if not context.get("employee"):
                return self._format_empty_response("Employee not found")
                
            # Get comprehensive employee profile
            profile = data_repo.get_employee_profile(employee_id)
            employee = profile.get("employee", {})
            
            # Check if this is the first message in the conversation
            chat_history = context.get("chat_history", [])
            is_first_message = len(chat_history) == 0
            
            try:
                greeting = f"Hello {employee.get('name', 'there')}! " if is_first_message else ""
                
                # Determine query type and get relevant policy details
                query_type = self._determine_query_type(query)
                policies = data_repo.get_relevant_policies(query)
                policy_details = policies[0]["policy_text"] if policies else ""

                # Create task description
                task_description = f"""
                Answer the following benefits question for {employee.get('name', 'the user')}.

                Employee Profile:
                - Name: {employee.get('name', 'the user')}
                - FSA Eligible: {profile['employee'].get('fsa_eligible', 'Unknown')}
                - HSA Eligible: {profile['employee'].get('hsa_eligible', 'Unknown')}
                - COBRA Status: {profile['employee'].get('cobra_status', 'Unknown')}

                Question: {query}

                Relevant Policy: {policy_details}

                You MUST format your response exactly like this:
                
                Thought: [Your analysis of the situation]
                
                Reasoning: [Your explanation of the approach]
                
                Final Answer: {greeting}[Your detailed response that MUST:
                - Use their name
                - Reference their benefits status
                - Provide specific details about HSA/FSA differences
                - Include relevant policy information
                - Be conversational but professional]

                IMPORTANT:
                1. NEVER respond with "I understand your query" or any similar generic phrase
                2. ALWAYS provide specific information based on their eligibility status
                3. ALWAYS include detailed comparisons when discussing HSA vs FSA
                4. ALWAYS make the response personal to their situation
                5. ALWAYS format exactly as shown above with Thought, Reasoning, and Final Answer sections
                """

                # Create and execute the task
                task = Task(
                    description=task_description,
                    expected_output="A detailed, personalized response that addresses the employee's specific situation and benefits question",
                    agent=self.agent
                )

                # Create a crew with just this agent and task
                crew = Crew(
                    agents=[self.agent],
                    tasks=[task],
                    verbose=True
                )

                # Execute the crew's task and get the response
                raw_response = crew.kickoff()
                print(f"Debug - Raw response from agent: {raw_response}")

                # Process the response
                processed_response = str(raw_response).strip()
                
                # Extract the final answer
                if "Final Answer:" in processed_response:
                    final_answer = processed_response.split("Final Answer:")[1].strip()
                    print(f"Debug - Found Final Answer: {final_answer}")
                    processed_response = final_answer
                elif "Thought:" in processed_response:
                    # If we have Thought but no Final Answer, take everything after the last section
                    sections = processed_response.split("Thought:")
                    processed_response = sections[-1].strip()
                    if "Reasoning:" in processed_response:
                        sections = processed_response.split("Reasoning:")
                        processed_response = sections[-1].strip()
                    print(f"Debug - Extracted response from sections: {processed_response}")
                else:
                    # Fallback: Use the raw response but ensure it's not just "I understand"
                    processed_response = processed_response if not processed_response.startswith("I understand") else """
                    Based on your question about HSA and FSA differences, let me explain the key distinctions:
                    
                    1. Ownership: HSAs are owned by you and stay with you even if you change jobs, while FSAs are owned by your employer
                    2. Rollover: HSA funds roll over year to year, while FSA funds typically must be used within the plan year
                    3. Contribution Changes: HSA contributions can be changed anytime, FSA contributions are usually fixed for the year
                    4. Eligibility: HSAs require a high-deductible health plan (HDHP), FSAs don't have this requirement
                    5. Account Combinations: HSAs can be used with Limited Purpose FSAs, but not with standard FSAs
                    
                    Please check your specific plan details for more information about your options.
                    """
                    print(f"Debug - Using fallback response: {processed_response}")
                
                # Get query-specific recommendations and steps
                recommendations = self._get_recommendations(query, profile)
                action_items = self._get_action_items(query, profile)
                next_steps = self._get_next_steps(query, profile)
                
                # Structure the final response
                final_response = {
                    "response": {
                        "message": processed_response.strip(),
                        "details": {
                            "recommendations": recommendations,
                            "action_items": action_items
                        }
                    },
                    "next_steps": next_steps
                }
                
                print(f"Debug - Final structured response: {json.dumps(final_response, indent=2)}")
                
                # Save the interaction
                data_repo.save_chat_interaction(
                    employee_id=employee_id,
                    messages=[
                        {"role": "user", "content": query},
                        {"role": "assistant", "content": processed_response}
                    ]
                )
                
                return final_response
                
            except Exception as e:
                print(f"Error executing agent task: {str(e)}")
                return self._format_empty_response(f"Error processing request: {str(e)}")
            
        except Exception as e:
            print(f"Error in analyze_query: {str(e)}")
            return self._format_empty_response(str(e))
            
    def _determine_query_type(self, query: str) -> str:
        """Determine the type of query based on keywords."""
        query = query.upper()
        if "FSA" in query and "REIMBURSEMENT" in query:
            return "FSA Reimbursement Process"
        elif "FSA" in query and "CONTRIBUTION" in query:
            return "FSA Contribution Changes"
        elif "FSA" in query:
            return "FSA Benefits"
        elif "HSA" in query and "CONTRIBUTION" in query:
            return "HSA Contribution Limits"
        elif "HSA" in query:
            return "HSA Benefits"
        elif "COBRA" in query:
            return "COBRA Benefits"
        return "General Benefits"
            
    def _format_chat_history(self, history: List[Dict[str, Any]]) -> str:
        """Format chat history for context."""
        if not history:
            return "No previous conversation."
            
        formatted = []
        # Only use last 2 interactions (4 messages: 2 questions and 2 responses)
        recent_history = history[-4:] if len(history) > 4 else history
        
        for msg in recent_history:
            role = msg.get("role", "unknown").title()
            content = msg.get("content", "").strip()
            if role == "User":
                formatted.append(f"Question: {content}")
            else:
                # Only include the main response, not the recommendations/next steps
                response_lines = content.split('\n')
                main_response = next((line for line in response_lines if line.strip()), content)
                formatted.append(f"Response: {main_response}")
            
        return "\n".join(formatted)
    
    def _get_recommendations(self, query: str, profile: Dict) -> List[str]:
        """Generate personalized recommendations based on the query and profile."""
        query = query.upper()
        if "FSA" in query and "REIMBURSEMENT" in query:
            return [
                "Take photos of receipts immediately after purchases to avoid losing them",
                "Set up direct deposit for faster reimbursement processing",
                "Keep a digital backup of all submitted receipts and claim forms",
                "Consider using your FSA debit card for instant payment when available",
                "Create a folder system to organize receipts by date and category"
            ]
        elif "FSA" in query and "CONTRIBUTION" in query:
            return [
                f"Review your annual healthcare expenses to optimize contribution amount (up to $3,200 for 2024)",
                "Consider upcoming medical procedures when setting contribution amount",
                "Remember the use-it-or-lose-it rule when planning contributions",
                "Check if your plan offers a grace period or carryover option",
                "Set up monthly expense tracking to stay within your FSA budget"
            ]
        elif "FSA" in query:
            return [
                "Keep a list of FSA-eligible expenses for reference",
                "Save receipts for all healthcare-related purchases",
                "Download your FSA administrator's mobile app for easy access",
                "Review your FSA balance regularly",
                "Plan major medical expenses around your FSA cycle"
            ]
        return []

    def _get_action_items(self, query: str, profile: Dict) -> List[str]:
        """Generate specific action items based on the query and profile."""
        query = query.upper()
        if "FSA" in query and "REIMBURSEMENT" in query:
            return [
                "Collect all receipts and supporting documentation",
                "Verify each receipt shows date, provider, service, and amount paid",
                "Complete the reimbursement form with accurate information",
                "Make copies or scans of all documentation before submitting",
                "Note your claim confirmation number for future reference"
            ]
        elif "FSA" in query and "CONTRIBUTION" in query:
            return [
                "Calculate your expected healthcare expenses for the year",
                "Review the current FSA contribution limits",
                "Check for any qualifying life events that allow changes",
                "Document the reason for your contribution change request",
                "Submit your change request through the proper channels"
            ]
        elif "FSA" in query:
            return [
                "Review your current FSA balance",
                "Check your remaining deadline for using funds",
                "List any upcoming eligible expenses",
                "Verify your FSA card is active",
                "Update your contact information if needed"
            ]
        return []

    def _get_next_steps(self, query: str, profile: Dict) -> List[str]:
        """Generate next steps based on the query and profile."""
        query = query.upper()
        if "FSA" in query and "REIMBURSEMENT" in query:
            return [
                "Access your FSA account portal or mobile app",
                "Select the reimbursement claim option",
                "Enter expense details and upload documentation",
                "Review all information for accuracy",
                "Submit your claim and save the confirmation"
            ]
        elif "FSA" in query and "CONTRIBUTION" in query:
            return [
                "Log into your benefits portal",
                "Navigate to FSA settings",
                "Enter your desired contribution change",
                "Provide any required documentation",
                "Submit your request for approval"
            ]
        elif "FSA" in query:
            return [
                "Review your FSA plan details",
                "Check your current balance",
                "List your upcoming expenses",
                "Gather necessary documentation",
                "Contact FSA administrator with questions"
            ]
        return []
    
    def _calculate_age(self, dob_str: str) -> int:
        """Calculate age from date of birth string."""
        from datetime import datetime
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d")
            today = datetime.now()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return age
        except:
            return "N/A"
    
    def _format_response(self, analysis_result: str) -> Dict[str, Any]:
        """
        Format the analysis result into a structured response.
        
        Args:
            analysis_result: Raw analysis result.
            
        Returns:
            Dict[str, Any]: Structured response.
        """
        # Extract key components from the analysis result
        lines = analysis_result.strip().split("\n")
        
        message = ""
        details = {
            "eligibility_status": "",
            "recommendations": [],
            "action_items": []
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "eligibility status:" in line.lower():
                current_section = "eligibility"
                continue
            elif "recommendations:" in line.lower():
                current_section = "recommendations"
                continue
            elif "action items:" in line.lower():
                current_section = "actions"
                continue
                
            if current_section == "eligibility":
                details["eligibility_status"] += line + " "
            elif current_section == "recommendations":
                if line.startswith("-"):
                    details["recommendations"].append(line[1:].strip())
            elif current_section == "actions":
                if line.startswith("-"):
                    details["action_items"].append(line[1:].strip())
            else:
                message += line + " "
        
        # If no structured sections were found, use the entire text as the message
        if not any(details.values()):
            message = analysis_result.strip()
            
        return {
            "message": message.strip(),
            "details": details
        }
    
    def _format_empty_response(self, message: str) -> Dict[str, Any]:
        """
        Format an empty response with an error message.
        
        Args:
            message: Error message to include.
            
        Returns:
            Dict[str, Any]: Empty response structure with required fields.
        """
        return {
            "response": {
                "message": message,
                "details": {
                    "recommendations": [],
                    "action_items": []
                }
            },
            "next_steps": []
        } 