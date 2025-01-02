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

                # Get wellness data with proper error handling
                try:
                    wellness_data = data_repo.get_employee_risk_assessment(employee_id)
                    if not wellness_data:
                        wellness_data = {
                            'metrics': {},
                            'risk_factors': [],
                            'recommendations': []
                        }
                except Exception as e:
                    print(f"Error fetching wellness data: {str(e)}")
                    wellness_data = {
                        'metrics': {},
                        'risk_factors': [],
                        'recommendations': []
                    }

                metrics = wellness_data.get('metrics', {})
                risk_factors = wellness_data.get('risk_factors', [])
                recommendations = wellness_data.get('recommendations', [])

                # Ensure metrics are properly formatted
                formatted_metrics = {
                    'heart_rate': metrics.get('heart_rate', 'N/A'),
                    'sleep_hours': metrics.get('sleep_hours', 'N/A'),
                    'exercise_minutes': metrics.get('exercise_minutes', 'N/A'),
                    'daily_steps': metrics.get('daily_steps', 'N/A'),
                    'stress_level': metrics.get('stress_level', 'N/A')
                }

                # Create task description with proper error handling for each section
                task_description = f"""
                Answer the following benefits question for {employee.get('name', 'the user')}.

                Employee Profile:
                - Name: {employee.get('name', 'the user')}
                - FSA Eligible: {profile.get('employee', {}).get('fsa_eligible', 'Unknown')}
                - HSA Eligible: {profile.get('employee', {}).get('hsa_eligible', 'Unknown')}
                - COBRA Status: {profile.get('employee', {}).get('cobra_status', 'Unknown')}
                - Dependents: {', '.join([f"{d.get('name', '')} ({d.get('relationship', '')})" for d in profile.get('employee', {}).get('dependents', [])])}
                
                Benefits Status:
                - Current Claims: {len(profile.get('claims', []))} active claims
                - Recent Life Events: {len(profile.get('life_events', []))} events in the past year
                
                Wellness Data:
                - Heart Rate: {formatted_metrics['heart_rate']} bpm
                - Sleep Hours: {formatted_metrics['sleep_hours']} hours/night
                - Exercise Minutes: {formatted_metrics['exercise_minutes']} minutes/day
                - Daily Steps: {formatted_metrics['daily_steps']} steps
                - Stress Level: {formatted_metrics['stress_level']}/10
                - Risk Factors: {', '.join(str(factor) for factor in risk_factors) if risk_factors else 'None identified'}
                - Health Recommendations: {', '.join(str(r.get('message', '')) for r in recommendations) if recommendations else 'None available'}

                Question: {query}

                Relevant Policy: {policy_details}

                You MUST format your response exactly like this:
                
                Thought: [Your analysis of the situation based on their specific profile and data]
                
                Reasoning: [Your explanation that references their specific eligibility status, wellness metrics, and history]
                
                Final Answer: {greeting}[Your detailed response that addresses their specific situation]
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
                
                # Extract the final answer with better error handling
                try:
                    if "Final Answer:" in processed_response:
                        final_answer = processed_response.split("Final Answer:")[1].strip()
                        if "[Your detailed response that addresses their specific situation]" in final_answer:
                            final_answer = final_answer.split("[Your detailed response that addresses their specific situation]")[0].strip()
                        processed_response = final_answer
                    elif "Thought:" in processed_response:
                        sections = processed_response.split("Thought:")
                        processed_response = sections[-1].strip()
                        if "Reasoning:" in processed_response:
                            sections = processed_response.split("Reasoning:")
                            processed_response = sections[-1].strip()
                    
                    # If we still have placeholder text, provide a default response
                    if "[Your" in processed_response or "Your final answer must be:" in processed_response:
                        # Create a default response based on the wellness data
                        metrics = wellness_data.get('metrics', {})
                        risk_factors = wellness_data.get('risk_factors', [])
                        
                        response_parts = []
                        response_parts.append(f"Based on your wellness data, here's a summary of your health metrics:")
                        
                        if metrics:
                            if metrics.get('heart_rate'):
                                response_parts.append(f"- Your heart rate is {metrics['heart_rate']} bpm")
                            if metrics.get('sleep_hours'):
                                response_parts.append(f"- You're getting {metrics['sleep_hours']} hours of sleep per night")
                            if metrics.get('exercise_minutes'):
                                response_parts.append(f"- You're exercising {metrics['exercise_minutes']} minutes per day")
                            if metrics.get('daily_steps'):
                                response_parts.append(f"- You're taking {metrics['daily_steps']} steps daily")
                            if metrics.get('stress_level'):
                                response_parts.append(f"- Your stress level is {metrics['stress_level']}/10")
                        
                        if risk_factors:
                            response_parts.append("\nIdentified risk factors:")
                            for factor in risk_factors:
                                response_parts.append(f"- {factor}")
                        
                        processed_response = "\n".join(response_parts)
                        
                except Exception as e:
                    print(f"Error processing response: {str(e)}")
                    processed_response = "Based on your wellness data, I recommend scheduling a check-up to review your health metrics and discuss personalized improvement strategies with a healthcare provider."

                # Get recommendations and format response
                recommendations = self._get_recommendations(query, profile)
                action_items = self._get_action_items(query, profile)
                next_steps = self._get_next_steps(query, profile)
                
                # Ensure the response is a dictionary with the required structure
                return {
                    "response": {
                        "message": processed_response,
                        "details": {
                            "recommendations": recommendations,
                            "action_items": action_items,
                            "next_steps": next_steps
                        }
                    }
                }
                
            except Exception as e:
                print(f"Error in analyze_query inner try block: {str(e)}")
                return self._format_empty_response(f"Error processing request: {str(e)}")
                
        except Exception as e:
            print(f"Error in analyze_query outer try block: {str(e)}")
            return self._format_empty_response("Sorry, I encountered an error processing your request. Please try again.")
            
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
        
        # Get wellness data
        wellness_data = profile.get('wellness_data', {})
        metrics = wellness_data.get('metrics', {})
        
        # Initialize recommendations list
        recommendations = []
        
        # Add wellness-specific recommendations if relevant
        if "WELLNESS" in query or "HEALTH" in query:
            try:
                # Convert metrics to integers for comparison, using 0 as default
                heart_rate = int(metrics.get('heart_rate', 0))
                sleep_hours = int(metrics.get('sleep_hours', 0))
                exercise_minutes = int(metrics.get('exercise_minutes', 0))
                daily_steps = int(metrics.get('daily_steps', 0))
                stress_level = int(metrics.get('stress_level', 0))
                
                if heart_rate > 80:
                    recommendations.append(
                        "Your heart rate is elevated. Consider incorporating more cardiovascular exercise and stress reduction techniques."
                    )
                if sleep_hours < 7:
                    recommendations.append(
                        "You're getting less than the recommended amount of sleep. Try to establish a regular sleep schedule aiming for 7-9 hours."
                    )
                if exercise_minutes < 30:
                    recommendations.append(
                        "Increase your daily physical activity to at least 30 minutes of moderate exercise most days."
                    )
                if daily_steps < 8000:
                    recommendations.append(
                        "Try to increase your daily step count. A goal of 10,000 steps per day can improve overall health."
                    )
                if stress_level > 6:
                    recommendations.append(
                        "Your stress levels are elevated. Consider stress management techniques like meditation or counseling."
                    )
            except (ValueError, TypeError):
                # If any conversion fails, add a generic recommendation
                recommendations.append(
                    "Consider scheduling a wellness check-up to establish your baseline health metrics."
                )
                
        # Add FSA-specific recommendations
        if "FSA" in query and "REIMBURSEMENT" in query:
            recommendations.extend([
                "Take photos of receipts immediately after purchases to avoid losing them",
                "Set up direct deposit for faster reimbursement processing",
                "Keep a digital backup of all submitted receipts and claim forms",
                "Consider using your FSA debit card for instant payment when available",
                "Create a folder system to organize receipts by date and category"
            ])
        elif "FSA" in query and "CONTRIBUTION" in query:
            recommendations.extend([
                f"Review your annual healthcare expenses to optimize contribution amount (up to $3,200 for 2024)",
                "Consider upcoming medical procedures when setting contribution amount",
                "Remember the use-it-or-lose-it rule when planning contributions",
                "Check if your plan offers a grace period or carryover option",
                "Set up monthly expense tracking to stay within your FSA budget"
            ])
        elif "FSA" in query:
            recommendations.extend([
                "Keep a list of FSA-eligible expenses for reference",
                "Save receipts for all healthcare-related purchases",
                "Download your FSA administrator's mobile app for easy access",
                "Review your FSA balance regularly",
                "Plan major medical expenses around your FSA cycle"
            ])
            
        return recommendations

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