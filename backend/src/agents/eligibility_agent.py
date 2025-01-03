"""
Eligibility Agent Module

Specialized agent for analyzing benefits eligibility and providing personalized recommendations.

Developer:
- Name: Nick Sudh
- Website: mlbrilliance.com
- GitHub: https://github.com/mlbrilliance
- Twitter: https://x.com/mlbrilliance
- BlueSky: https://bsky.app/profile/mlbrilliance.com
"""

from typing import Dict, Any, List, Optional
from crewai import Agent
from ..repositories.data_repository import DataRepository
from .wellness_agent import WellnessAgent
import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from pydantic import PrivateAttr

class EligibilityAgent(Agent):
    """Agent responsible for analyzing benefits eligibility and providing recommendations."""
    
    _wellness_agent: WellnessAgent = PrivateAttr()
    _data_repo: DataRepository = PrivateAttr()
    
    def __init__(self):
        """Initialize the EligibilityAgent."""
        # Load environment variables
        load_dotenv(find_dotenv())
        
        # Get API key and print debug info
        openai_api_key = os.getenv("OPENAI_API_KEY")
        print(f"Debug - API Key exists: {bool(openai_api_key)}")
        print(f"Debug - API Key length: {len(openai_api_key) if openai_api_key else 0}")
        print(f"Debug - Current working directory: {os.getcwd()}")
        print(f"Debug - Environment variables: {dict(os.environ)}")
        
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        super().__init__(
            role='Benefits Eligibility Specialist',
            goal='Analyze employee benefits eligibility and provide accurate recommendations',
            backstory="""You are an expert in employee benefits, particularly HSA, FSA, and COBRA.
            You analyze employee situations and provide detailed recommendations based on their eligibility
            and current circumstances. You always provide structured responses with clear sections for
            eligibility status, recommendations, and action items.""",
            allow_delegation=False,
            llm=ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0,
                api_key=openai_api_key
            )
        )
        
        # Initialize private attributes
        self._wellness_agent = WellnessAgent()
        self._data_repo = DataRepository()

    async def analyze_benefits_scenario(self, employee_id: str, query: str) -> Dict[str, Any]:
        """
        Analyze a benefits scenario for an employee and provide recommendations.
        
        Args:
            employee_id: The ID of the employee.
            query: The specific benefits query or scenario to analyze.
            
        Returns:
            Dict[str, Any]: Analysis results including eligibility status and recommendations.
        """
        try:
            # Get current benefits status
            benefits_status = self._data_repo.get_employee_benefits_status(employee_id)
            
            # Get employee profile
            profile = self._data_repo.get_employee_profile(employee_id)
            if not profile:
                return self._format_empty_response("Employee not found")
            
            # Get wellness data using WellnessAgent
            wellness_analysis = await self._wellness_agent.get_wellness_analysis(employee_id)
            risk_assessment = wellness_analysis["wellness_data"]
            
            # Search for relevant policies
            relevant_policies = self._data_repo.get_relevant_policies(query)
            
            # Analyze the scenario
            analysis = await self._analyze_scenario(
                query=query,
                profile=profile,
                benefits_status=benefits_status,
                risk_assessment=risk_assessment,
                relevant_policies=relevant_policies
            )
            
            return analysis
            
        except Exception as e:
            print(f"Error in analyze_benefits_scenario: {str(e)}")
            return self._format_empty_response(f"Error analyzing benefits scenario: {str(e)}")

    async def _analyze_scenario(
        self,
        query: str,
        profile: Dict[str, Any],
        benefits_status: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        relevant_policies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform detailed analysis of the benefits scenario.
        
        Args:
            query: The specific benefits query or scenario to analyze.
            profile: Comprehensive employee profile data.
            benefits_status: Current benefits eligibility status.
            risk_assessment: Health risk assessment data.
            relevant_policies: List of relevant policy documents.
            
        Returns:
            Dict[str, Any]: Detailed analysis results.
        """
        # Extract employee data
        employee = profile.get("employee", {})
        dob = employee.get("dob")
        age = self._calculate_age(dob) if dob else "N/A"
        dependents = profile.get("dependents", [])
        claims = profile.get("claims", [])
        life_events = profile.get("life_events", [])
        
        # Get health metrics from risk assessment
        metrics = risk_assessment.get("metrics", {})
        
        # Execute the analysis using the agent's capabilities
        result = await self.execute(
            task=f"""
            Analyze the following benefits scenario and provide detailed recommendations:
            
            Query: {query}
            
            Employee Profile:
            - Name: {employee.get('name')}
            - Age: {age} years old
            - Email: {employee.get('email')}
            - Dependents: {len(dependents)} registered
            - Recent Claims: {len(claims)}
            - Life Events: {len(life_events)}
            
            Health Profile:
            - Stress Level: {metrics.get('stress_level', 'N/A')}/10
            - Sleep Hours: {metrics.get('sleep_hours', 'N/A')} hours/night
            - Exercise: {metrics.get('exercise_minutes', 'N/A')} minutes/day
            - Daily Steps: {metrics.get('daily_steps', 'N/A')} steps
            - Heart Rate: {metrics.get('heart_rate', 'N/A')} bpm
            - Risk Factors: {', '.join(str(factor) for factor in risk_assessment.get('risk_factors', [])) if risk_assessment.get('risk_factors', []) else 'None identified'}
            - Health Recommendations: {', '.join(str(r) for r in risk_assessment.get('recommendations', [])) if risk_assessment.get('recommendations', []) else 'None available'}
            
            Current Benefits Status:
            - HSA Eligible: {benefits_status.get('hsa_eligible')}
            - FSA Eligible: {benefits_status.get('fsa_eligible')}
            - COBRA Status: {benefits_status.get('cobra_status')}
            
            Policy Details:
            {relevant_policies[0]["policy_text"] if relevant_policies else "No specific policy details available."}
            
            Based on this comprehensive information, provide a detailed analysis with the following sections:

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
            """
        )
        
        # Parse and structure the analysis result
        return self._format_response(result)

    def _create_analysis_context(
        self,
        query: str,
        profile: Dict[str, Any],
        benefits_status: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        relevant_policies: List[Dict[str, Any]]
    ) -> str:
        """
        Create a formatted context string for analysis.
        
        Args:
            query: The specific benefits query or scenario to analyze.
            profile: Comprehensive employee profile data.
            benefits_status: Current benefits eligibility status.
            risk_assessment: Health risk assessment data.
            relevant_policies: List of relevant policy documents.
            
        Returns:
            str: Formatted context string.
        """
        employee = profile.get("employee", {})
        dependents = profile.get("dependents", [])
        claims = profile.get("claims", [])
        life_events = profile.get("life_events", [])
        
        context = f"""
        Employee Information:
        - Name: {employee.get('name')}
        - Email: {employee.get('email')}
        - DOB: {employee.get('dob')}
        
        Current Benefits Status:
        - HSA Eligible: {benefits_status.get('hsa_eligible', False)}
        - FSA Eligible: {benefits_status.get('fsa_eligible', False)}
        - COBRA Status: {benefits_status.get('cobra_status', 'not_applicable')}
        
        Dependents:
{self._format_dependents(dependents)}

        Recent Claims:
        {self._format_claims(claims)}

        Life Events:
{self._format_life_events(life_events)}
        
        Health Risk Assessment:
        {self._format_risk_assessment(risk_assessment)}
        
        Relevant Policies:
        {self._format_policies(relevant_policies)}
        """

        return context

    def _format_dependents(self, dependents: List[Dict[str, Any]]) -> str:
        """Format dependents information."""
        if not dependents:
            return "No dependents"
            
        return "\n".join([
            f"- {dep.get('name')} ({dep.get('relationship')}), DOB: {dep.get('dob')}"
            for dep in dependents
        ])

    def _format_claims(self, claims: List[Dict[str, Any]]) -> str:
        """Format claims information."""
        if not claims:
            return "No recent claims"
            
        return "\n".join([
            f"- {claim.get('date')}: {claim.get('type')} - {claim.get('description')} (${claim.get('amount', 0):.2f})"
            for claim in claims
        ])

    def _format_life_events(self, events: List[Dict[str, Any]]) -> str:
        """Format life events information."""
        if not events:
            return "No life events"
            
        return "\n".join([
            f"- {event.get('event_date')}: {event.get('event_type')} - {event.get('dependent', 'N/A')}"
            for event in events
        ])

    def _format_risk_assessment(self, assessment: Dict[str, Any]) -> str:
        """Format risk assessment information."""
        if not assessment:
            return "No health risk assessment available"
            
        metrics = assessment.get("metrics", {})
        risk_factors = assessment.get("risk_factors", [])
        recommendations = assessment.get("recommendations", [])
        
        return f"""
        Metrics:
        - Stress Level: {metrics.get('stress_level', 'N/A')}
        - Sleep Hours: {metrics.get('sleep_hours', 'N/A')}
        - Exercise Minutes: {metrics.get('exercise_minutes', 'N/A')}
        - Daily Steps: {metrics.get('daily_steps', 'N/A')}
        - Heart Rate: {metrics.get('heart_rate', 'N/A')}
        
        Risk Factors: {', '.join(risk_factors) if risk_factors else 'None identified'}
        
        Recommendations: {', '.join(recommendations) if recommendations else 'None available'}
        """

    def _format_policies(self, policies: List[Dict[str, Any]]) -> str:
        """Format policy information."""
        if not policies:
            return "No relevant policies found"
            
        return "\n".join([
            f"- {policy.get('policy_name')} (Version {policy.get('version')})"
            for policy in policies
        ])

    def _format_response(self, analysis_result: str) -> Dict[str, Any]:
        """
        Format the analysis result into a structured response.
        
        Args:
            analysis_result: Raw analysis result from the agent.
            
        Returns:
            Dict[str, Any]: Structured analysis response.
        """
        # Extract key components from the analysis result
        lines = analysis_result.strip().split("\n")
        
        eligibility_status = ""
        recommendations = []
        action_items = []
        policy_considerations = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "eligibility status" in line.lower():
                current_section = "eligibility"
                continue
            elif "recommendations" in line.lower():
                current_section = "recommendations"
                continue
            elif "action items" in line.lower():
                current_section = "actions"
                continue
            elif "policy considerations" in line.lower():
                current_section = "policies"
                continue
                
            if current_section == "eligibility":
                eligibility_status += line + " "
            elif current_section == "recommendations":
                if line.startswith("-"):
                    recommendations.append(line[1:].strip())
            elif current_section == "actions":
                if line.startswith("-"):
                    action_items.append(line[1:].strip())
            elif current_section == "policies":
                if line.startswith("-"):
                    policy_considerations.append(line[1:].strip())

        return {
            "eligibility_status": eligibility_status.strip(),
            "recommendations": recommendations,
            "action_items": action_items,
            "policy_considerations": policy_considerations
        }

    def _format_empty_response(self, message: str) -> Dict[str, Any]:
        """Format an empty response with the given message."""
        return {
            "eligibility_status": message,
            "recommendations": [],
            "action_items": [],
            "policy_considerations": []
        }

    def _calculate_age(self, dob: str) -> int:
        """Calculate age from date of birth."""
        from datetime import datetime
        try:
            birth_date = datetime.strptime(dob, "%Y-%m-%d")
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age
        except (ValueError, TypeError):
            return 0 