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
from .wellness_agent import WellnessAgent
from .policy_agent import PolicyAgent
from ..repositories.data_repository import DataRepository
import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
import json
from datetime import datetime
import re
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

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
        
        # Initialize data repository
        self.data_repo = DataRepository()
        
        # Initialize agents
        self.eligibility_agent = EligibilityAgent()
        self.wellness_agent = WellnessAgent()
        self.policy_agent = PolicyAgent()
        
        # Initialize the LLM
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=openai_api_key
        )
        
        # Initialize the LLM chain with a simple prompt template
        template = """
        You are a senior benefits advisor with deep expertise in HSA, FSA, and COBRA benefits.
        Your responses must be detailed, personalized, and actionable.
        
        Context:
        {task_description}
        
        Please analyze the situation and provide a response in the following format:
        
        Thought: [Your analysis of the situation]
        
        Reasoning: [Your explanation]
        
        Final Answer: [Your detailed response]
        
        Remember to:
        1. Be specific and reference the employee's situation
        2. Include clear recommendations
        3. Provide actionable next steps
        4. Reference relevant policies
        5. Consider wellness data in your response
        """
        
        prompt = PromptTemplate(
            input_variables=["task_description"],
            template=template
        )
        
        self.llm_chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            verbose=True
        )
        
        # Initialize the base Agent for complex queries
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
            llm=self.llm
        )
    
    async def analyze_query(self, employee_id: str, query: str) -> Dict[str, Any]:
        """
        Analyze a user query and provide a response using the agent chain.
        
        Args:
            employee_id: The ID of the employee making the query.
            query: The question or request from the user.
            
        Returns:
            Dict[str, Any]: Formatted response with recommendations and next steps.
        """
        try:
            print("\n=== Starting analyze_query ===")
            debug_info = []
            
            print("\nStep 1: Getting employee profile...")
            profile = self.data_repo.get_employee_profile(employee_id)
            print(f"Profile received: {json.dumps(profile, indent=2)}")
            employee = profile.get('employee', {})
            
            print("\nStep 2: Determining query type...")
            query_type = self._determine_query_type(query)
            print(f"Query type determined: {query_type}")
            
            print("\nStep 3: Getting relevant policies...")
            policies = self.policy_agent.get_relevant_policies(query_type)
            print(f"Policies received: {json.dumps(policies, indent=2)}")
            policy_details = "\n".join([f"- {str(p)}" for p in policies])
            
            print("\nStep 4: Adding policy debug info...")
            debug_info.append({
                "agent": "Policy Agent",
                "timestamp": str(datetime.now().isoformat()),
                "action": "Policy Research",
                "thought": "Searching knowledge base for relevant policies",
                "reasoning": "Need to ensure response aligns with current policy guidelines",
                "result": f"Found {len(policies)} relevant policies for {query_type}"
            })

            print("\nStep 5: Getting wellness data...")
            wellness_analysis = self.wellness_agent.get_wellness_analysis(employee_id)
            print(f"Wellness analysis received: {json.dumps(wellness_analysis, indent=2)}")
            wellness_data = wellness_analysis.get("wellness_data", {})
            
            print("\nStep 6: Sanitizing debug info from wellness analysis...")
            if isinstance(wellness_analysis.get("debug_info"), list):
                for debug_entry in wellness_analysis["debug_info"]:
                    if isinstance(debug_entry, dict):
                        sanitized_entry = {
                            "agent": str(debug_entry.get("agent", "Unknown")),
                            "timestamp": str(debug_entry.get("timestamp", datetime.now().isoformat())),
                            "action": str(debug_entry.get("action", "")),
                            "thought": str(debug_entry.get("thought", "")),
                            "reasoning": str(debug_entry.get("reasoning", "")),
                            "result": str(debug_entry.get("result", ""))
                        }
                        debug_info.append(sanitized_entry)
            elif wellness_analysis.get("debug_info"):
                debug_entry = wellness_analysis["debug_info"]
                if isinstance(debug_entry, dict):
                    sanitized_entry = {
                        "agent": str(debug_entry.get("agent", "Unknown")),
                        "timestamp": str(debug_entry.get("timestamp", datetime.now().isoformat())),
                        "action": str(debug_entry.get("action", "")),
                        "thought": str(debug_entry.get("thought", "")),
                        "reasoning": str(debug_entry.get("reasoning", "")),
                        "result": str(debug_entry.get("result", ""))
                    }
                    debug_info.append(sanitized_entry)

            print("\nStep 7: Formatting metrics...")
            formatted_metrics = {}
            for key, value in wellness_data.get("metrics", {}).items():
                if isinstance(value, dict):
                    formatted_metrics[key] = {k: str(v) for k, v in value.items()}
                else:
                    formatted_metrics[key] = str(value)
            print(f"Formatted metrics: {json.dumps(formatted_metrics, indent=2)}")

            print("\nStep 8: Sanitizing risk factors and recommendations...")
            risk_factors = [str(factor) for factor in wellness_data.get('risk_factors', [])]
            wellness_recommendations = [str(rec) for rec in wellness_data.get('recommendations', [])]
            print(f"Risk factors: {json.dumps(risk_factors, indent=2)}")
            print(f"Wellness recommendations: {json.dumps(wellness_recommendations, indent=2)}")

            print("\nStep 9: Creating task description...")
            current_hour = datetime.now().hour
            greeting = "Good morning" if 5 <= current_hour < 12 else "Good afternoon" if 12 <= current_hour < 17 else "Good evening"
            greeting = f"{greeting}, {employee.get('name', 'there')}! "

            task_description = f"""
            Answer the following benefits question for {employee.get('name', 'the user')}.

            Employee Profile:
            - Name: {employee.get('name', 'the user')}
            - FSA Eligible: {profile.get('employee', {}).get('fsa_eligible', 'Unknown')}
            - HSA Eligible: {profile.get('employee', {}).get('hsa_eligible', 'Unknown')}
            - COBRA Status: {profile.get('employee', {}).get('cobra_status', 'Unknown')}
            - Dependents: {', '.join([f"{d.get('name', '')} ({d.get('relationship', '')})" for d in profile.get('dependents', [])])}
            
            Benefits Status:
            - Current Claims: {len(profile.get('claims', []))} active claims
            - Recent Life Events: {len(profile.get('life_events', []))} events in the past year
            
            Wellness Data:
            - Heart Rate: {formatted_metrics.get('heart_rate', 'N/A')}
            - Sleep Hours: {formatted_metrics.get('sleep_hours', 'N/A')}
            - Exercise Minutes: {formatted_metrics.get('exercise_minutes', 'N/A')}
            - Daily Steps: {formatted_metrics.get('daily_steps', 'N/A')}
            - Stress Level: {formatted_metrics.get('stress_level', 'N/A')}
            - Risk Factors: {', '.join(risk_factors) if risk_factors else 'None identified'}
            - Health Recommendations: {', '.join(wellness_recommendations) if wellness_recommendations else 'None available'}

            Question: {query}

            Relevant Policy: {policy_details}

            You MUST format your response exactly like this:
            
            Thought: [Your analysis of the situation based on their specific profile and data]
            
            Reasoning: [Your explanation that references their specific eligibility status, wellness metrics, and history]
            
            Final Answer: {greeting}[Your detailed response that addresses their specific situation]
            """
            print("\nTask description created successfully")

            print("\nStep 10: Running LLM chain...")
            try:
                print("\nRunning LLM chain with task description...")
                chain_response = self.llm_chain.run(task_description)
                print(f"\nLLM chain response received: {chain_response[:200]}...")
                
                print("\nStep 11: Formatting response...")
                # Extract action items before formatting response
                action_items = self._get_action_items(query)
                
                # Convert chain_response to string if it's not already
                if not isinstance(chain_response, str):
                    chain_response = str(chain_response)
                
                # Ensure debug_info is properly formatted
                sanitized_debug = []
                for entry in debug_info:
                    if isinstance(entry, dict):
                        sanitized_entry = {
                            "agent": str(entry.get("agent", "Unknown")),
                            "timestamp": str(entry.get("timestamp", datetime.now().isoformat())),
                            "action": str(entry.get("action", "")),
                            "thought": str(entry.get("thought", "")),
                            "reasoning": str(entry.get("reasoning", "")),
                            "result": str(entry.get("result", ""))
                        }
                        sanitized_debug.append(sanitized_entry)
                
                formatted_response = self._format_response(chain_response, sanitized_debug, action_items)
                print(f"\nFormatted response: {json.dumps(formatted_response, indent=2)}")
                
                return formatted_response
                
            except Exception as chain_error:
                print(f"\nError in LLM chain: {str(chain_error)}")
                print(f"Error type: {type(chain_error)}")
                print(f"Error details: {chain_error.__dict__ if hasattr(chain_error, '__dict__') else 'No details'}")
                debug_info.append({
                    "agent": "LLM Chain",
                    "timestamp": str(datetime.now().isoformat()),
                    "action": "Process Query",
                    "thought": "Error occurred during LLM processing",
                    "reasoning": "Chain execution failed",
                    "result": str(chain_error)
                })
                return self._format_empty_response(f"An error occurred while processing your request: {str(chain_error)}")
                
        except Exception as e:
            print(f"\nError in analyze_query: {str(e)}")
            print(f"Error type: {type(e)}")
            print(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details'}")
            return self._format_empty_response(f"An error occurred while processing your request: {str(e)}")
            
    def _determine_query_type(self, query: str) -> str:
        """
        Determine the type of query based on keywords.
        
        Args:
            query: The query string to analyze.
            
        Returns:
            str: The determined query type.
        """
        query = query.lower()
        
        # Check for specific combinations first
        if "hsa" in query and "fsa" in query:
            return "HSA Benefits"  # Default to HSA when comparing both
        elif "fsa" in query and "reimbursement" in query:
            return "FSA Reimbursement Process"
        elif "fsa" in query and "contribution" in query:
            return "FSA Contribution Changes"
        elif "fsa" in query:
            return "FSA Benefits"
        elif "hsa" in query and "contribution" in query:
            return "HSA Contribution Limits"
        elif "hsa" in query:
            return "HSA Benefits"
        elif "cobra" in query:
            return "COBRA Benefits"
        
        # Default to General Benefits if no specific type is found
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
        """
        Generate recommendations based on the query and profile.
        
        Args:
            query: The query string to analyze.
            profile: Employee profile data.
            
        Returns:
            List[str]: List of recommendations.
        """
        try:
            query = query.lower()
            recommendations = []
            
            # Add base recommendations based on query type
            if "hsa" in query and "fsa" in query:
                recommendations.extend([
                    "Compare HSA and FSA features based on your healthcare needs",
                    "Review contribution limits for both accounts",
                    "Consider your eligibility status for each account",
                    "Evaluate your expected healthcare expenses",
                    "Understand the tax advantages of each account type"
                ])
            elif "hsa" in query and "contribution" in query:
                recommendations.extend([
                    f"Review 2024 HSA contribution limits: $4,150 individual, $8,300 family",
                    "Consider catch-up contributions if you're 55 or older",
                    "Plan contributions based on expected medical expenses",
                    "Review employer HSA contribution matching if available",
                    "Set up automatic payroll deductions for consistent saving"
                ])
            elif "hsa" in query:
                recommendations.extend([
                    "Verify your HDHP enrollment status",
                    "Review HSA investment options if available",
                    "Keep records of all qualified medical expenses",
                    "Consider long-term HSA growth strategy",
                    "Understand HSA rollover and portability benefits"
                ])
            elif "fsa" in query and "reimbursement" in query:
                recommendations.extend([
                    "Keep all receipts organized by date and category",
                    "Submit claims promptly to avoid processing delays",
                    "Use FSA debit card for immediate payment when possible",
                    "Maintain digital copies of all submitted documentation",
                    "Track reimbursement status and follow up if needed"
                ])
            elif "fsa" in query and "contribution" in query:
                recommendations.extend([
                    "Review your annual healthcare expenses to optimize contribution amount",
                    "Consider upcoming medical procedures when planning",
                    "Remember the use-it-or-lose-it rule",
                    "Check if your plan offers a grace period or carryover",
                    "Set up monthly expense tracking"
                ])
            elif "fsa" in query:
                recommendations.extend([
                    "Keep a list of FSA-eligible expenses",
                    "Save receipts for all healthcare purchases",
                    "Download your FSA administrator's mobile app",
                    "Review your FSA balance regularly",
                    "Plan major medical expenses around your FSA cycle"
                ])
            elif "cobra" in query:
                recommendations.extend([
                    "Compare COBRA costs with marketplace options",
                    "Understand coverage continuation periods",
                    "Review all available insurance alternatives",
                    "Consider HSA funds for premium payments if applicable",
                    "Keep track of important COBRA deadlines"
                ])
            else:
                recommendations.extend([
                    "Schedule a benefits consultation for personalized guidance",
                    "Review your current benefits elections",
                    "Consider any upcoming life changes",
                    "Keep your benefits information up to date",
                    "Document your healthcare expenses"
                ])
            
            # Add wellness-based recommendations if profile has wellness data
            if profile.get('wellness_data', {}).get('risk_factors'):
                recommendations.extend([
                    "Consider using HSA/FSA funds for preventive care",
                    "Review coverage for wellness programs",
                    "Track health-related expenses for tax purposes"
                ])
            
            # Ensure all recommendations are strings
            return [str(rec) for rec in recommendations]
            
        except Exception as e:
            print(f"Error in _get_recommendations: {str(e)}")
            return ["Schedule a benefits consultation for personalized guidance"]

    def _get_action_items(self, query: str, profile: Optional[Dict] = None) -> List[str]:
        """
        Generate specific action items based on the query and profile.
        
        Args:
            query: The query string to analyze.
            profile: Optional profile data.
            
        Returns:
            List[str]: List of action items.
        """
        try:
            query = query.lower()
            action_items = []
            
            if "fsa" in query and "reimbursement" in query:
                action_items = [
                    "Collect all receipts and supporting documentation",
                    "Verify each receipt shows date, provider, service, and amount paid",
                    "Complete the reimbursement form with accurate information",
                    "Make copies or scans of all documentation before submitting",
                    "Note your claim confirmation number for future reference"
                ]
            elif "fsa" in query and "contribution" in query:
                action_items = [
                    "Calculate your expected healthcare expenses for the year",
                    "Review the current FSA contribution limits",
                    "Check for any qualifying life events that allow changes",
                    "Document the reason for your contribution change request",
                    "Submit your change request through the proper channels"
                ]
            elif "fsa" in query:
                action_items = [
                    "Review your current FSA balance",
                    "Check your remaining deadline for using funds",
                    "List any upcoming eligible expenses",
                    "Verify your FSA card is active",
                    "Update your contact information if needed"
                ]
            elif "hsa" in query and "contribution" in query:
                action_items = [
                    "Verify your HDHP enrollment status",
                    "Review current HSA contribution limits",
                    "Calculate your maximum allowable contribution",
                    "Set up or adjust payroll deductions",
                    "Consider catch-up contributions if eligible"
                ]
            elif "hsa" in query:
                action_items = [
                    "Check your HSA balance",
                    "Review investment options if available",
                    "List upcoming qualified medical expenses",
                    "Verify your HSA debit card is active",
                    "Update your beneficiary information"
                ]
            elif "cobra" in query:
                action_items = [
                    "Review COBRA election notice",
                    "Compare COBRA premium costs",
                    "Check election deadline dates",
                    "Gather required documentation",
                    "Consider alternative coverage options"
                ]
            else:
                action_items = [
                    "Review your benefits documentation",
                    "Contact HR for clarification if needed",
                    "Update your personal information",
                    "Schedule a follow-up if necessary"
                ]
            
            return [str(item) for item in action_items]
            
        except Exception as e:
            print(f"Error in _get_action_items: {str(e)}")
            return ["Review your benefits documentation", "Contact HR for clarification if needed"]

    def _get_next_steps(self, text: str) -> List[str]:
        """
        Extract next steps from the response text.
        
        Args:
            text: The response text to analyze.
            
        Returns:
            List[str]: List of next steps.
        """
        next_steps = []
        if "next steps:" in text.lower():
            section = text.lower().split("next steps:")[1].split("\n")
            for line in section:
                line = line.strip()
                if line and (line.startswith("-") or line.startswith("*")):
                    next_steps.append(line[1:].strip())
                elif any(marker in line.lower() for marker in ["recommendations:", "action items:"]):
                    break
        
        # Default next steps if none found
        if not next_steps:
            if "hsa" in text.lower() and "fsa" in text.lower():
                next_steps = [
                    "Review your HSA and FSA eligibility status",
                    "Compare contribution limits and rollover rules",
                    "Consider your healthcare spending patterns",
                    "Consult with HR about enrollment options"
                ]
            elif "hsa" in text.lower():
                next_steps = [
                    "Check your HDHP enrollment status",
                    "Review HSA contribution limits",
                    "Consider catch-up contributions if eligible",
                    "Set up automatic HSA contributions"
                ]
            elif "fsa" in text.lower():
                next_steps = [
                    "Review FSA eligible expenses",
                    "Plan your annual FSA contribution",
                    "Set up FSA reimbursement process",
                    "Track FSA spending deadlines"
                ]
            elif "cobra" in text.lower():
                next_steps = [
                    "Review COBRA eligibility requirements",
                    "Compare COBRA costs with alternatives",
                    "Check election deadlines",
                    "Gather required documentation"
                ]
            else:
                next_steps = [
                    "Review your benefits documentation",
                    "Schedule a benefits consultation",
                    "Update your benefits preferences",
                    "Contact HR for additional guidance"
                ]
        
        return [str(step) for step in next_steps]
    
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
    
    def _format_response(self, analysis_result: str, debug_info: List[Dict] = None, action_items: List[str] = None) -> Dict[str, Any]:
        """
        Format the analysis result into a structured response.
        
        Args:
            analysis_result: Raw analysis result string.
            debug_info: List of debug entries from agents.
            action_items: List of action items.
            
        Returns:
            Dict[str, Any]: Formatted response with message, details, and next steps.
        """
        try:
            # Extract components using string parsing
            thought_match = re.search(r"Thought:(.*?)(?=Reasoning:|$)", analysis_result, re.DOTALL)
            reasoning_match = re.search(r"Reasoning:(.*?)(?=Final Answer:|$)", analysis_result, re.DOTALL)
            answer_match = re.search(r"Final Answer:(.*?)$", analysis_result, re.DOTALL)
            
            thought = thought_match.group(1).strip() if thought_match else ""
            reasoning = reasoning_match.group(1).strip() if reasoning_match else ""
            answer = answer_match.group(1).strip() if answer_match else analysis_result.strip()
            
            # Initialize debug_info if None
            if debug_info is None:
                debug_info = []
                
            # Convert any non-string values in debug_info to strings
            sanitized_debug_info = []
            for entry in debug_info:
                if not isinstance(entry, dict):
                    continue
                sanitized_entry = {
                    "agent": str(entry.get("agent", "Unknown")),
                    "timestamp": str(entry.get("timestamp", datetime.now().isoformat())),
                    "action": str(entry.get("action", "")),
                    "thought": str(entry.get("thought", "")),
                    "reasoning": str(entry.get("reasoning", "")),
                    "result": str(entry.get("result", ""))
                }
                sanitized_debug_info.append(sanitized_entry)
                
            # Add final thought to debug info if thought exists
            if thought or reasoning:
                sanitized_debug_info.append({
                    "agent": "Response Formatter",
                    "timestamp": str(datetime.now().isoformat()),
                    "action": "Format Response",
                    "thought": str(thought) if thought else "No thought provided",
                    "reasoning": str(reasoning) if reasoning else "No reasoning provided",
                    "result": "Response formatted successfully"
                })
            
            # Extract recommendations and action items
            recommendations = self._extract_recommendations(answer)
            if action_items is None:
                action_items = self._extract_action_items(answer)
            
            # Get next steps based on the answer text
            next_steps = self._get_next_steps(answer)
            
            # Ensure all lists contain only strings
            recommendations = [str(r) for r in recommendations]
            action_items = [str(a) for a in action_items]
            next_steps = [str(s) for s in next_steps]
            
            # Create the response dictionary with all values as strings
            response = {
                "response": {
                    "message": str(answer),
                    "details": {
                        "recommendations": recommendations,
                        "action_items": action_items
                    }
                },
                "next_steps": next_steps,
                "debug_info": sanitized_debug_info
            }
            
            # Convert to JSON and back to ensure all values are serializable
            return json.loads(json.dumps(response))
            
        except Exception as e:
            # If any error occurs during formatting, return an empty response with error message
            return self._format_empty_response(f"An error occurred while processing your request: {str(e)}")

    def _format_empty_response(self, message: str) -> Dict[str, Any]:
        """Format an empty response with the given message."""
        timestamp = str(datetime.now().isoformat())
        return {
            "response": {
                "message": str(message),
                "details": {
                    "recommendations": [],
                    "action_items": []
                }
            },
            "next_steps": ["Please provide more information about your benefits scenario"],
            "debug_info": [{
                "agent": "Manager Agent",
                "timestamp": timestamp,
                "action": "Empty Response",
                "thought": "Error occurred during processing",
                "reasoning": "Need to provide error message",
                "result": str(message)
            }]
        }

    def _extract_recommendations(self, text: str) -> List[str]:
        """
        Extract recommendations from the response text.
        
        Args:
            text: The response text to analyze.
            
        Returns:
            List[str]: List of recommendations.
        """
        print("\n=== Starting _extract_recommendations ===")
        recommendations = []
        try:
            print("\nStep 1: Looking for recommendations section...")
            if "recommendations:" in text.lower():
                print("Found recommendations section")
                section = text.lower().split("recommendations:")[1].split("\n")
                print(f"Found {len(section)} lines in section")
                
                for line in section:
                    line = line.strip()
                    if line and (line.startswith("-") or line.startswith("*")):
                        clean_line = line[1:].strip()
                        if clean_line:
                            print(f"Adding recommendation: {clean_line[:50]}...")
                            recommendations.append(clean_line)
                    elif any(marker in line.lower() for marker in ["action items:", "next steps:"]):
                        print("Found end of recommendations section")
                        break
            
            print(f"\nStep 2: Found {len(recommendations)} recommendations from text")
            
            # Default recommendations if none found
            if not recommendations:
                print("\nNo recommendations found, using defaults based on context...")
                if "hsa" in text.lower() and "fsa" in text.lower():
                    print("Using HSA/FSA comparison defaults")
                    recommendations = [
                        "Compare HSA and FSA features based on your healthcare needs",
                        "Review contribution limits for both accounts",
                        "Consider your eligibility status for each account",
                        "Evaluate your expected healthcare expenses"
                    ]
                elif "hsa" in text.lower():
                    print("Using HSA defaults")
                    recommendations = [
                        "Verify your HDHP enrollment status",
                        "Review HSA contribution strategies",
                        "Consider investment options if available",
                        "Track qualified medical expenses"
                    ]
                elif "fsa" in text.lower():
                    print("Using FSA defaults")
                    recommendations = [
                        "Plan your FSA contributions carefully",
                        "Review FSA-eligible expenses",
                        "Track FSA deadlines and grace periods",
                        "Keep all receipts for reimbursement"
                    ]
                else:
                    print("Using general defaults")
                    recommendations = [
                        "Schedule a benefits consultation for personalized guidance",
                        "Review your current benefits elections",
                        "Consider any upcoming life changes",
                        "Keep your benefits information up to date"
                    ]
                print(f"Added {len(recommendations)} default recommendations")
        except Exception as e:
            print(f"\nError in _extract_recommendations: {str(e)}")
            print(f"Error type: {type(e)}")
            print(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details'}")
            recommendations = ["Schedule a benefits consultation for personalized guidance"]
        
        print("\nStep 3: Converting recommendations to strings...")
        string_recommendations = []
        for rec in recommendations:
            try:
                string_recommendations.append(str(rec))
                print(f"Successfully converted: {str(rec)[:50]}...")
            except Exception as e:
                print(f"Error converting recommendation to string: {str(e)}")
        
        print(f"\nReturning {len(string_recommendations)} recommendations")
        return string_recommendations

    def _extract_action_items(self, text: str) -> List[str]:
        """
        Extract action items from the response text.
        
        Args:
            text: The response text to analyze.
            
        Returns:
            List[str]: List of action items.
        """
        action_items = []
        try:
            if "action items:" in text.lower():
                section = text.lower().split("action items:")[1].split("\n")
                for line in section:
                    line = line.strip()
                    if line and (line.startswith("-") or line.startswith("*")):
                        clean_line = line[1:].strip()
                        if clean_line:
                            action_items.append(clean_line)
                    elif "next steps:" in line.lower():
                        break
            
            # Default action items if none found
            if not action_items:
                if "hsa" in text.lower() and "fsa" in text.lower():
                    action_items = [
                        "Review current benefits enrollment status",
                        "Calculate potential contributions for each account",
                        "Document expected medical expenses",
                        "Schedule benefits consultation if needed"
                    ]
                elif "hsa" in text.lower():
                    action_items = [
                        "Verify HDHP enrollment",
                        "Set up HSA contributions",
                        "Review investment options",
                        "Organize medical expense records"
                    ]
                elif "fsa" in text.lower():
                    action_items = [
                        "Calculate FSA contribution needs",
                        "Submit FSA enrollment form",
                        "Set up FSA payment card",
                        "Create FSA expense tracking system"
                    ]
                else:
                    action_items = [
                        "Review benefits documentation",
                        "Contact HR for clarification if needed",
                        "Update personal information",
                        "Schedule follow-up if necessary"
                    ]
        except Exception:
            action_items = ["Review your benefits documentation", "Contact HR for clarification if needed"]
        
        return [str(item) for item in action_items]

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