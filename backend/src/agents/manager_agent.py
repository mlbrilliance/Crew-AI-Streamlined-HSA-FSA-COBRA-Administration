from typing import Dict, List, Optional
from crewai import Agent
from datetime import datetime
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from .eligibility_agent import EligibilityAgent
import logging

# Load environment variables
load_dotenv()

class ManagerAgent:
    """
    Supervisor/Manager Agent that coordinates other specialized agents.
    
    This agent orchestrates the interaction between different specialized agents,
    maintains conversation context, and makes high-level decisions about which
    agents to engage for different types of queries.
    """
    
    def __init__(self) -> None:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=openai_api_key
        )
        
        # Initialize specialized agents
        self.eligibility_agent = EligibilityAgent()
        self.conversation_context = {}
        
        # Initialize base agent properties
        self.name = "Benefits Administration Manager"
        self.role = "Senior benefits administration coordinator and decision maker"
        self.goal = "Coordinate specialized agents and provide comprehensive benefits guidance"
        self.backstory = """You are an experienced benefits administration manager with 
        expertise in coordinating complex benefits scenarios. You excel at understanding 
        user needs and directing queries to the appropriate specialized agents."""
        self.verbose = True
        self.allow_delegation = True
    
    async def execute(self, task: str) -> str:
        """
        Execute a task using the manager's capabilities.
        
        Args:
            task: The task description or query to process.
            
        Returns:
            str: The result of executing the task.
        """
        try:
            result = await self.route_query(task)
            return str(result.get("response", "Unable to process the request."))
        except Exception as e:
            return f"Error processing request: {str(e)}"
    
    async def analyze_query(self, query: str) -> Dict[str, any]:
        """
        Analyze a user query and determine the appropriate agent(s) to handle it.
        
        Args:
            query: The user's question or request about benefits.
        
        Returns:
            Dict containing analysis results and recommended actions.
        """
        task = f"""As a Benefits Administration Manager, analyze this query and determine how to handle it:

Query: {query}

Analyze the query considering:
1. Query Type: What type of benefits question is this? (e.g., HSA eligibility, FSA limits, COBRA coverage)
2. Required Information: What additional information might be needed?
3. Relevant Regulations: Are there specific IRS or DOL regulations to consider?
4. Next Steps: What actions should be taken to address this query?

Format your response exactly as follows:
Query Type: [Specify the primary type of query - HSA, FSA, COBRA, etc.]
Required Information: [List any missing information needed]
Recommended Actions: [List specific steps to take]
Additional Considerations: [Note any regulatory or special considerations]
"""
        messages = [HumanMessage(content=task)]
        analysis = await self.llm.ainvoke(messages)
        return self._parse_analysis_response(analysis.content)
    
    async def route_query(self, query: str, context: Optional[Dict] = None) -> Dict[str, any]:
        """
        Route a query to the appropriate agent(s) and aggregate responses.
        
        Args:
            query: The user's question or request.
            context: Optional conversation context from previous interactions.
        
        Returns:
            Dict containing the aggregated response and any follow-up actions.
        """
        try:
            logger = logging.getLogger(__name__)
            logger.debug(f"Manager Agent received query: {query}")
            
            # Update conversation context
            if context:
                self.conversation_context.update(context)
                logger.debug(f"Updated conversation context: {self.conversation_context}")
            
            # Analyze the query
            logger.debug("Analyzing query...")
            analysis = await self.analyze_query(query)
            logger.debug(f"Query analysis result: {analysis}")
            
            # Route to appropriate agent based on analysis
            if self._is_eligibility_query(analysis):
                logger.info("Query identified as eligibility-related. Routing to EligibilityAgent...")
                response = await self.eligibility_agent.analyze_benefits_scenario(query)
                logger.debug(f"Received response from EligibilityAgent: {response}")
                formatted_response = self._format_response(response, analysis)
                logger.debug(f"Formatted final response: {formatted_response}")
                return formatted_response
            
            # Default handling if no specific routing is determined
            logger.info("No specific routing determined. Providing general guidance.")
            return {
                "response": {
                    "message": "I need more specific information about your benefits question to provide accurate guidance.",
                    "details": {
                        "missing_info": analysis.get("required_information", "Please provide more details about your situation."),
                        "considerations": analysis.get("additional_considerations", "")
                    }
                },
                "context": {
                    "query_type": analysis.get("query_type", "Unknown"),
                    "additional_info_needed": analysis.get("required_information", "")
                },
                "next_steps": [
                    "Please provide more details about your current benefits situation",
                    "Specify any particular concerns or constraints",
                    "Include relevant dates or deadlines"
                ]
            }
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return {
                "response": {
                    "message": "Error processing your request",
                    "details": str(e)
                },
                "context": {"error": str(e)},
                "next_steps": ["Please try again with more specific information"]
            }
    
    def _is_eligibility_query(self, analysis: Dict[str, any]) -> bool:
        """Determine if a query should be routed to the EligibilityAgent."""
        query_type = analysis.get("query_type", "").lower()
        return any(term in query_type for term in ["eligibility", "hsa", "fsa", "cobra", "health savings", "flexible spending"])
    
    def _parse_analysis_response(self, analysis: str) -> Dict[str, any]:
        """Parse the analysis response into structured data."""
        lines = analysis.split('\n')
        result = {
            "query_type": "",
            "required_information": "",
            "recommended_actions": "",
            "additional_considerations": "",
            "raw_analysis": analysis
        }
        
        current_section = ""
        for line in lines:
            line = line.strip()
            if line.startswith("Query Type:"):
                current_section = "query_type"
                result[current_section] = line.replace("Query Type:", "").strip()
            elif line.startswith("Required Information:"):
                current_section = "required_information"
                result[current_section] = line.replace("Required Information:", "").strip()
            elif line.startswith("Recommended Actions:"):
                current_section = "recommended_actions"
                result[current_section] = line.replace("Recommended Actions:", "").strip()
            elif line.startswith("Additional Considerations:"):
                current_section = "additional_considerations"
                result[current_section] = line.replace("Additional Considerations:", "").strip()
            elif line and current_section:
                result[current_section] += f"\n{line}"
        
        return result
    
    def _format_response(self, agent_response: Dict[str, any], analysis: Dict[str, any]) -> Dict[str, any]:
        """Format the final response with context and additional information."""
        # Ensure we have a valid response structure
        if not isinstance(agent_response, dict):
            response = {
                "message": str(agent_response),
                "details": {
                    "eligibility_status": "",
                    "recommendations": "",
                    "action_items": "",
                    "agent_interaction": "Manager Agent only - no specialized agent response"
                }
            }
        else:
            response = {
                "message": agent_response.get("message", ""),
                "details": {
                    "eligibility_status": agent_response.get("details", {}).get("eligibility_status", ""),
                    "recommendations": agent_response.get("details", {}).get("recommendations", ""),
                    "action_items": agent_response.get("details", {}).get("action_items", ""),
                    "agent_interaction": "Manager Agent routed to Eligibility Agent for detailed analysis"
                }
            }

        # Extract action items from both the analysis and agent response
        action_items = []
        
        # Add actions from the eligibility agent
        if response["details"]["action_items"]:
            actions = response["details"]["action_items"].split("\n")
            action_items.extend([action.strip() for action in actions if action.strip()])
        
        # Add actions from the manager's analysis
        if analysis.get("recommended_actions"):
            manager_actions = analysis["recommended_actions"].split("\n")
            action_items.extend([
                f"[Manager] {action.strip()}" 
                for action in manager_actions if action.strip()
            ])
        
        # Ensure we have at least some next steps
        if not action_items:
            action_items = [
                "[Manager] Review your benefits documentation",
                "[Manager] Consult with your HR department about specific policies",
                "[Manager] Consider scheduling a benefits consultation"
            ]

        return {
            "response": response,
            "context": {
                "query_type": analysis.get("query_type", ""),
                "additional_considerations": analysis.get("additional_considerations", ""),
                "processing_flow": "Manager Agent → Query Analysis → Eligibility Agent → Combined Response"
            },
            "next_steps": action_items
        } 