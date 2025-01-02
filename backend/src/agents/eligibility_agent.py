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
import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI

class EligibilityAgent(Agent):
    """Agent responsible for analyzing benefits eligibility and providing recommendations."""
    
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
    
    async def analyze_benefits_scenario(self, employee_id: str, query: str) -> Dict[str, Any]:
        """
        Analyze a benefits scenario for an employee and provide recommendations.
        
        Args:
            employee_id: The ID of the employee.
            query: The specific benefits query or scenario to analyze.
            
        Returns:
            Dict[str, Any]: Analysis results including eligibility status and recommendations.
        """
        # Create data repository instance
        data_repo = DataRepository()
        
        # Gather comprehensive employee data
        profile = data_repo.get_employee_profile(employee_id)
        if not profile:
            return self._format_empty_response("Employee not found")
            
        # Get current benefits status
        benefits_status = data_repo.get_employee_benefits_status(employee_id)
        
        # Get health risk assessment if available
        risk_assessment = data_repo.get_employee_risk_assessment(employee_id)
        
        # Search for relevant policies
        relevant_policies = data_repo.get_relevant_policies(query)
        
        # Analyze the scenario
        analysis = await self._analyze_scenario(
            query=query,
            profile=profile,
            benefits_status=benefits_status,
            risk_assessment=risk_assessment,
            relevant_policies=relevant_policies
        )
        
        return analysis
    
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
        
        # Get health metrics
        health_metrics = risk_assessment.get("metrics", {})
        stress_level = health_metrics.get("stress_level", "N/A")
        sleep_hours = health_metrics.get("sleep_hours", "N/A")
        exercise_minutes = health_metrics.get("exercise_minutes", "N/A")
        heart_rate = health_metrics.get("heart_rate", "N/A")
        risk_factors = risk_assessment.get("risk_factors", [])
        consent_status = risk_assessment.get("consent_status", "not_provided")
        
        # Get policy details
        policy_details = relevant_policies[0]["policy_text"] if relevant_policies else "No specific policy details available."
        
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
            - Stress Level: {stress_level}/10
            - Sleep Hours: {sleep_hours} hours/night
            - Exercise: {exercise_minutes} minutes/day
            - Heart Rate: {heart_rate} bpm
            - Risk Factors: {', '.join(risk_factors) if risk_factors else 'None identified'}
            - Health Data Consent: {consent_status}
            
            Current Benefits Status:
            - HSA Eligible: {benefits_status.get('hsa_eligible')}
            - FSA Eligible: {benefits_status.get('fsa_eligible')}
            - COBRA Status: {benefits_status.get('cobra_status')}
            
            Policy Details:
            {policy_details}
            
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
        
        return f"""
        Metrics:
        - Stress Level: {metrics.get('stress_level', 'N/A')}
        - Sleep Hours: {metrics.get('sleep_hours', 'N/A')}
        - Exercise Minutes: {metrics.get('exercise_minutes', 'N/A')}
        - Heart Rate: {metrics.get('heart_rate', 'N/A')}
        
        Risk Factors: {', '.join(risk_factors) if risk_factors else 'None identified'}
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
        """
        Format an empty response with an error message.
        
        Args:
            message: Error message to include.
            
        Returns:
            Dict[str, Any]: Empty response structure.
        """
        return {
            "eligibility_status": message,
            "recommendations": [],
            "action_items": [],
            "policy_considerations": []
        } 