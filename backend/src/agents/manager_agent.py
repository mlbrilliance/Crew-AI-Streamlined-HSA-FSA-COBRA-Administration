from typing import Dict, Any, List, Optional
from crewai import Agent, Task, Crew
from .eligibility_agent import EligibilityAgent
from ..repositories.data_repository import DataRepository
import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI

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
            role='Benefits Manager',
            goal='Coordinate and manage benefits analysis tasks',
            backstory="""You are a senior benefits manager with expertise in coordinating
            complex benefits scenarios. You work with specialized agents to provide
            comprehensive benefits analysis and recommendations. You ensure all responses
            are well-structured and include clear eligibility status, recommendations,
            and action items.""",
            allow_delegation=True,
            llm=ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0,
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
        # Create data repository instance
        data_repo = DataRepository()
        
        # Get employee context and additional data
        context = data_repo.get_chat_context(employee_id)
        if not context.get("employee"):
            return self._format_empty_response("Employee not found")
            
        # Get comprehensive employee profile
        profile = data_repo.get_employee_profile(employee_id)
        employee = profile.get("employee", {})
        dob = employee.get("dob")
        age = self._calculate_age(dob) if dob else "N/A"
        dependents = profile.get("dependents", [])
        claims = profile.get("claims", [])
        life_events = profile.get("life_events", [])
            
        # Get health risk assessment
        risk_assessment = data_repo.get_employee_risk_assessment(employee_id)
        health_metrics = risk_assessment.get("metrics", {})
        risk_factors = risk_assessment.get("risk_factors", [])
        consent_status = risk_assessment.get("consent_status", "not_provided")
        
        # Get relevant policies
        policies = data_repo.get_relevant_policies(query)
        policy_details = policies[0]["policy_text"] if policies else "No specific policy details available."
        
        # Create analysis task
        analysis_task = Task(
            description=f"""
            Analyze the following benefits query and provide comprehensive recommendations:
            
            Query: {query}
            
            Employee Profile:
            - Name: {employee.get('name')}
            - Age: {age} years old
            - Email: {employee.get('email')}
            - Dependents: {len(dependents)} registered
            - Recent Claims: {len(claims)}
            - Life Events: {len(life_events)}
            
            Current Benefits Status:
            - HSA Eligible: {context['benefits_status'].get('hsa_eligible')}
            - FSA Eligible: {context['benefits_status'].get('fsa_eligible')}
            - COBRA Status: {context['benefits_status'].get('cobra_status')}
            
            Health Profile:
            - Stress Level: {health_metrics.get('stress_level', 'N/A')}/10
            - Sleep Hours: {health_metrics.get('sleep_hours', 'N/A')} hours/night
            - Exercise: {health_metrics.get('exercise_minutes', 'N/A')} minutes/day
            - Heart Rate: {health_metrics.get('heart_rate', 'N/A')} bpm
            - Risk Factors: {', '.join(risk_factors) if risk_factors else 'None identified'}
            - Health Data Consent: {consent_status}
            
            Policy Details:
            {policy_details}
            
            Previous Chat History:
            {self._format_chat_history(context['chat_history'])}
            
            Please provide a comprehensive analysis with the following sections:
            
            Eligibility Status:
            [Provide current eligibility status, citing specific policy requirements that are met, including age and dependent considerations]
            
            Health Profile Impact:
            [Analyze how the employee's health metrics and risk factors influence HSA benefits utilization]
            
            Recommendations:
            - [List specific recommendations, incorporating all health metrics]
            - [Include contribution strategies based on age and dependent status]
            - [Reference specific policy guidelines and IRS limits]
            - [Include wellness program integration suggestions]
            
            Action Items:
            - [List specific actions with deadlines]
            - [Include documentation requirements from policy]
            - [Specify health data consent requirements if needed]
            - [Detail wellness program enrollment steps if applicable]
            
            Make sure to reference specific details from all available data points in your response.
            Highlight any areas where additional information might be beneficial.
            """,
            agent=self.eligibility_agent
        )
        
        # Create crew for analysis
        crew = Crew(
            agents=[self.agent, self.eligibility_agent],
            tasks=[analysis_task]
        )
        
        try:
            # Execute analysis
            result = crew.kickoff()
            
            # Save chat interaction
            data_repo.save_chat_interaction(
                employee_id=employee_id,
                messages=[
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": result}
                ]
            )
            
            # Format and return response
            return self._format_response(result)
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            return self._format_empty_response(f"Error during analysis: {str(e)}")
            
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
    
    def _format_chat_history(self, history: List[Dict[str, Any]]) -> str:
        """
        Format chat history for context.
        
        Args:
            history: List of chat history records.
            
        Returns:
            str: Formatted chat history string.
        """
        if not history:
            return "No previous chat history"
            
        formatted_history = []
        for record in history[-3:]:  # Only use last 3 interactions
            chat_data = record.get("chat_history", [])
            if isinstance(chat_data, str):
                try:
                    import json
                    chat_data = json.loads(chat_data)
                except:
                    chat_data = []
                    
            for message in chat_data:
                formatted_history.append(
                    f"{message.get('role', 'unknown').title()}: {message.get('content', '')}"
                )
                
        return "\n".join(formatted_history)
    
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
            Dict[str, Any]: Empty response structure.
        """
        return {
            "message": message,
            "details": {
                "eligibility_status": "",
                "recommendations": [],
                "action_items": []
            }
        } 