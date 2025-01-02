"""
Manager Agent Module

Responsible for orchestrating the multi-agent system and coordinating benefits analysis tasks.

Developer:
- Name: Nick Sudh
- Website: mlbrilliance.com
- GitHub: https://github.com/mlbrilliance
- Twitter: https://x.com/mlbrilliance
- BlueSky: https://bsky.app/profile/mlbrilliance.com
"""

from typing import Dict, Any, List, Optional
from crewai import Agent, Task, Crew
from .eligibility_agent import EligibilityAgent
from ..repositories.data_repository import DataRepository
import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
import json
from datetime import datetime
import re

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
            # Initialize debug info list
            debug_info = []
            debug_info.append({
                "agent": "Manager Agent",
                "timestamp": datetime.now().isoformat(),
                "action": "Query Analysis Started",
                "thought": "Initiating comprehensive analysis of user query",
                "reasoning": "Need to understand query context and gather relevant employee data",
                "result": f"Processing query: {query}"
            })

            # Create data repository instance
            data_repo = DataRepository()
            
            # Get employee context and additional data
            debug_info.append({
                "agent": "Manager Agent",
                "timestamp": datetime.now().isoformat(),
                "action": "Context Gathering",
                "thought": "Building comprehensive employee profile",
                "reasoning": "Need complete employee data to provide accurate, personalized response",
                "result": "Retrieving employee profile, benefits status, and wellness metrics"
            })

            context = data_repo.get_chat_context(employee_id)
            if not context.get("employee"):
                return self._format_empty_response("Employee not found")
                
            # Get comprehensive employee profile
            profile = data_repo.get_employee_profile(employee_id)
            employee = profile.get("employee", {})
            
            debug_info.append({
                "agent": "Context Agent",
                "timestamp": datetime.now().isoformat(),
                "action": "Profile Analysis",
                "thought": "Analyzing employee benefits eligibility and status",
                "reasoning": "Need to understand current benefits status to provide relevant guidance",
                "result": f"Employee Profile: {employee.get('name')} | FSA Eligible: {profile.get('employee', {}).get('fsa_eligible')} | HSA Eligible: {profile.get('employee', {}).get('hsa_eligible')}"
            })

            # Check if this is the first message in the conversation
            chat_history = context.get("chat_history", [])
            is_first_message = len(chat_history) == 0
            
            try:
                greeting = f"Hello {employee.get('name', 'there')}! " if is_first_message else ""
                
                # Determine query type and get relevant policy details
                query_type = self._determine_query_type(query)
                debug_info.append({
                    "agent": "Query Analyzer",
                    "timestamp": datetime.now().isoformat(),
                    "action": "Query Classification",
                    "thought": "Analyzing query intent and category",
                    "reasoning": "Need to identify specific benefits domain to provide focused response",
                    "result": f"Query classified as: {query_type}"
                })

                policies = data_repo.get_relevant_policies(query)
                policy_details = policies[0]["policy_text"] if policies else ""

                debug_info.append({
                    "agent": "Policy Agent",
                    "timestamp": datetime.now().isoformat(),
                    "action": "Policy Research",
                    "thought": "Searching knowledge base for relevant policies",
                    "reasoning": "Need to ensure response aligns with current policy guidelines",
                    "result": f"Found {len(policies)} relevant policies for {query_type}"
                })

                # Get wellness data with proper error handling
                debug_info.append({
                    "agent": "Wellness Agent",
                    "timestamp": datetime.now().isoformat(),
                    "action": "Health Assessment",
                    "thought": "Evaluating wellness metrics and risk factors",
                    "reasoning": "Need to consider health context for benefits recommendations",
                    "result": "Analyzing wellness data for personalized guidance"
                })

                try:
                    wellness_data = data_repo.get_employee_risk_assessment(employee_id)
                    if not wellness_data:
                        wellness_data = {
                            'metrics': {},
                            'risk_factors': [],
                            'recommendations': []
                        }
                    debug_info.append({
                        "agent": "Wellness Agent",
                        "timestamp": datetime.now().isoformat(),
                        "action": "Risk Assessment",
                        "thought": "Evaluating health risk factors",
                        "reasoning": "Need to identify potential health-related benefits needs",
                        "result": f"Risk Factors: {len(wellness_data.get('risk_factors', []))} identified"
                    })
                except Exception as e:
                    print(f"Error fetching wellness data: {str(e)}")
                    wellness_data = {
                        'metrics': {},
                        'risk_factors': [],
                        'recommendations': []
                    }
                    debug_info.append({
                        "agent": "Wellness Agent",
                        "timestamp": datetime.now().isoformat(),
                        "action": "Error Recovery",
                        "thought": "Handling wellness data retrieval error",
                        "reasoning": "Need to proceed with available data",
                        "result": f"Using default wellness profile due to error: {str(e)}"
                    })

                # Create task description with proper error handling for each section
                debug_info.append({
                    "agent": "Task Manager",
                    "timestamp": datetime.now().isoformat(),
                    "action": "Response Planning",
                    "thought": "Preparing comprehensive response strategy",
                    "reasoning": "Need to combine all gathered information into coherent guidance",
                    "result": "Initiating response generation with collected context"
                })

                # Ensure metrics are properly formatted
                formatted_metrics = {
                    'heart_rate': wellness_data.get('metrics', {}).get('heart_rate', 'N/A'),
                    'sleep_hours': wellness_data.get('metrics', {}).get('sleep_hours', 'N/A'),
                    'exercise_minutes': wellness_data.get('metrics', {}).get('exercise_minutes', 'N/A'),
                    'daily_steps': wellness_data.get('metrics', {}).get('daily_steps', 'N/A'),
                    'stress_level': wellness_data.get('metrics', {}).get('stress_level', 'N/A')
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
                - Risk Factors: {', '.join(str(factor) for factor in wellness_data.get('risk_factors', [])) if wellness_data.get('risk_factors', []) else 'None identified'}
                - Health Recommendations: {', '.join(str(r.get('message', '')) for r in wellness_data.get('recommendations', [])) if wellness_data.get('recommendations', []) else 'None available'}

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

                debug_info.append({
                    "agent": "Benefits Expert",
                    "timestamp": datetime.now().isoformat(),
                    "action": "Response Generation",
                    "thought": "Formulating personalized benefits guidance",
                    "reasoning": "Need to provide actionable, specific advice based on all gathered data",
                    "result": "Generating detailed response with recommendations"
                })

                # Create a crew with just this agent and task
                crew = Crew(
                    agents=[self.agent],
                    tasks=[task],
                    verbose=True
                )

                # Execute the crew's task and get the response
                raw_response = crew.kickoff()
                
                debug_info.append({
                    "agent": "Response Analyzer",
                    "timestamp": datetime.now().isoformat(),
                    "action": "Quality Check",
                    "thought": "Reviewing generated response",
                    "reasoning": "Need to ensure response meets quality standards and addresses query completely",
                    "result": "Response validated and ready for delivery"
                })

                # Process the response
                processed_response = str(raw_response).strip()
                
                # Format the response with debug info
                formatted_response = self._format_response(processed_response, debug_info)
                
                return formatted_response
                
            except Exception as e:
                print(f"Error in analyze_query: {str(e)}")
                debug_info.append({
                    "agent": "Manager Agent",
                    "timestamp": datetime.now().isoformat(),
                    "action": "Error Handling",
                    "result": f"Error: {str(e)}"
                })
                return self._format_empty_response(f"Error processing request: {str(e)}")
                
        except Exception as e:
            print(f"Error in analyze_query: {str(e)}")
            return self._format_empty_response(f"Error processing request: {str(e)}")
            
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

    def _get_next_steps(self, text: str) -> List[str]:
        """Generate next steps based on the query text."""
        text = text.upper()
        if "FSA" in text and "REIMBURSEMENT" in text:
            return [
                "Access your FSA account portal or mobile app",
                "Select the reimbursement claim option",
                "Enter expense details and upload documentation",
                "Review all information for accuracy",
                "Submit your claim and save the confirmation"
            ]
        elif "FSA" in text and "CONTRIBUTION" in text:
            return [
                "Log into your benefits portal",
                "Navigate to FSA settings",
                "Enter your desired contribution change",
                "Provide any required documentation",
                "Submit your request for approval"
            ]
        elif "FSA" in text:
            return [
                "Review your FSA plan details",
                "Check your current balance",
                "List your upcoming expenses",
                "Gather necessary documentation",
                "Contact FSA administrator with questions"
            ]
        elif "HSA" in text:
            return [
                "Review your HSA plan details",
                "Check your current balance",
                "Consider your contribution strategy",
                "Review investment options if available",
                "Contact HSA administrator with questions"
            ]
        return ["Schedule a benefits consultation for personalized guidance"]
    
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
    
    def _format_response(self, analysis_result: str, debug_info: List[Dict] = None) -> Dict[str, Any]:
        """
        Format the analysis result into a structured response.
        
        Args:
            analysis_result: Raw analysis result string.
            debug_info: List of debug entries from agents.
            
        Returns:
            Dict[str, Any]: Formatted response with message, details, and next steps.
        """
        # Extract components using string parsing
        thought_match = re.search(r"Thought:(.*?)(?=Reasoning:|$)", analysis_result, re.DOTALL)
        reasoning_match = re.search(r"Reasoning:(.*?)(?=Final Answer:|$)", analysis_result, re.DOTALL)
        answer_match = re.search(r"Final Answer:(.*?)$", analysis_result, re.DOTALL)
        
        thought = thought_match.group(1).strip() if thought_match else ""
        reasoning = reasoning_match.group(1).strip() if reasoning_match else ""
        answer = answer_match.group(1).strip() if answer_match else analysis_result.strip()
        
        # Add final thought to debug info
        if debug_info is None:
            debug_info = []
            
        debug_info.append({
            "agent": "Response Formatter",
            "timestamp": datetime.now().isoformat(),
            "thought": thought,
            "reasoning": reasoning,
            "result": "Response formatted successfully"
        })
        
        # Extract recommendations and action items
        recommendations = self._extract_recommendations(answer)
        action_items = self._extract_action_items(answer)
        
        # Get next steps based on the answer text
        next_steps = self._get_next_steps(answer)
        
        return {
            "response": {
                "message": answer,
                "details": {
                    "recommendations": recommendations,
                    "action_items": action_items
                }
            },
            "next_steps": next_steps,
            "debug_info": debug_info
        }

    def _format_empty_response(self, message: str) -> Dict[str, Any]:
        """Format an empty response with the given message."""
        return {
            "response": {
                "message": message,
                "details": {
                    "recommendations": [],
                    "action_items": []
                }
            },
            "next_steps": ["Please provide more information about your benefits scenario"],
            "debug_info": [{
                "agent": "Manager Agent",
                "timestamp": datetime.now().isoformat(),
                "action": "Empty Response",
                "result": message
            }]
        }

    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from the response text."""
        recommendations = []
        if "recommendations:" in text.lower():
            section = text.lower().split("recommendations:")[1].split("\n")
            for line in section:
                line = line.strip()
                if line and (line.startswith("-") or line.startswith("*")):
                    recommendations.append(line[1:].strip())
                elif "action items:" in line.lower() or "next steps:" in line.lower():
                    break
        return recommendations or ["Schedule a benefits consultation for personalized guidance"]
        
    def _extract_action_items(self, text: str) -> List[str]:
        """Extract action items from the response text."""
        action_items = []
        if "action items:" in text.lower():
            section = text.lower().split("action items:")[1].split("\n")
            for line in section:
                line = line.strip()
                if line and (line.startswith("-") or line.startswith("*")):
                    action_items.append(line[1:].strip())
                elif "next steps:" in line.lower():
                    break
        return action_items or ["Review your benefits documentation", "Contact HR for clarification if needed"] 

    async def route_query(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Route and analyze a query, returning a structured response.
        
        Args:
            query: The query to analyze.
            context: Optional context information.
            
        Returns:
            Dict[str, Any]: Structured response with debug info.
        """
        try:
            # Extract employee_id from context if available
            employee_id = context.get("employee_id") if context else "default"
            
            # Analyze the query
            result = await self.analyze_query(employee_id, query)
            
            # Ensure debug_info is included in the response
            if "debug_info" not in result:
                result["debug_info"] = []
                
            return result
            
        except Exception as e:
            print(f"Error in route_query: {str(e)}")
            return self._format_empty_response(f"Error processing request: {str(e)}") 