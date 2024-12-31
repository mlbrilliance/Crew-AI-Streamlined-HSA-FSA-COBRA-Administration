from typing import Dict, List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import logging

# Load environment variables
load_dotenv()

class EligibilityAgent:
    """
    AI-powered agent for analyzing benefits eligibility and providing personalized recommendations.
    
    This agent uses LangChain to analyze complex scenarios,
    evaluate multiple benefit options, and provide detailed recommendations based
    on individual circumstances.
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
        
        # Initialize base agent properties
        self.name = "Benefits Analysis Specialist"
        self.role = "Expert benefits analyst specializing in HSA, FSA, and COBRA eligibility"
        self.goal = "Analyze complex benefit scenarios and provide personalized recommendations"
        self.backstory = """You are an expert benefits analyst with deep knowledge of 
        healthcare benefits, tax implications, and federal regulations. You excel 
        at analyzing complex scenarios and providing actionable recommendations."""
        self.verbose = True
        self.allow_delegation = False
    
    async def execute(self, task: str) -> str:
        """
        Execute a task using the agent's capabilities.
        
        Args:
            task: The task description or scenario to analyze.
            
        Returns:
            str: The result of executing the task.
        """
        try:
            result = await self.analyze_benefits_scenario(task)
            return str(result)
        except Exception as e:
            return f"Error analyzing benefits scenario: {str(e)}"
    
    async def analyze_benefits_scenario(self, scenario: str) -> Dict[str, any]:
        """
        Analyze a complex benefits scenario described in natural language.
        
        Args:
            scenario: Natural language description of an individual's situation,
                     including their health needs, financial situation, and current benefits.
        
        Returns:
            Dict containing analysis results, recommendations, and explanations.
        """
        logger = logging.getLogger(__name__)
        logger.debug(f"EligibilityAgent analyzing scenario: {scenario}")
        
        task = f"""As a Benefits Analysis Specialist, analyze this scenario and provide detailed HSA/FSA/COBRA recommendations:

Scenario: {scenario}

Please analyze considering:
1. Eligibility Requirements:
   - HDHP requirements and limits
   - HSA/FSA contribution limits
   - Special considerations for new employees
2. Financial Optimization:
   - Tax advantages and savings strategies
   - Employer contribution coordination
   - Long-term benefits maximization
3. Compliance Requirements:
   - IRS regulations and limits
   - Required documentation
   - Important deadlines

Format your response exactly as follows:
Situation Analysis: [Detailed analysis of the current situation]
Eligibility Status: [Clear statement of eligibility and any requirements]
Recommendations: [Specific, actionable recommendations with amounts and deadlines]
Action Items: [Numbered list of specific steps to take]
"""
        logger.debug("Sending analysis request to LLM")
        messages = [HumanMessage(content=task)]
        analysis = await self.llm.ainvoke(messages)
        logger.debug(f"Received raw analysis from LLM: {analysis.content}")
        
        parsed_response = self._parse_analysis_response(analysis.content)
        logger.debug(f"Parsed analysis response: {parsed_response}")
        
        return parsed_response
    
    async def recommend_optimal_benefits(
        self,
        profile: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Provide personalized benefits recommendations based on individual profile.
        
        Args:
            profile: Dictionary containing:
                - age: int
                - income: float
                - health_conditions: List[str]
                - current_coverage: Dict
                - family_status: str
                - planned_medical_expenses: float
        
        Returns:
            Dict containing personalized recommendations and explanations.
        """
        task = self._create_recommendation_prompt(profile)
        messages = [HumanMessage(content=task)]
        recommendations = await self.llm.ainvoke(messages)
        return self._parse_recommendations_response(recommendations.content)
    
    def _create_recommendation_prompt(self, profile: Dict[str, any]) -> str:
        """Create a detailed prompt for benefits analysis."""
        return f"""As a benefits specialist, analyze this individual's profile and provide optimal recommendations:

Age: {profile.get('age')}
Income: ${profile.get('income'):,.2f}
Health Conditions: {', '.join(profile.get('health_conditions', []))}
Current Coverage: {profile.get('current_coverage')}
Family Status: {profile.get('family_status')}
Planned Medical Expenses: ${profile.get('planned_medical_expenses'):,.2f}

Provide comprehensive analysis including:
1. Optimal benefit selection strategy
2. HSA vs FSA recommendation with contribution amounts
3. Potential tax savings calculations
4. Risk analysis and coverage recommendations
5. Specific action items prioritized by importance
6. Long-term considerations and planning
"""
    
    def _parse_analysis_response(self, analysis: str) -> Dict[str, any]:
        """Parse the analysis response into structured data."""
        sections = analysis.split('\n\n')
        
        # Initialize default values
        situation = ""
        eligibility = ""
        recommendations = ""
        actions = ""
        
        # Parse each section
        for section in sections:
            if section.startswith("Situation Analysis:"):
                situation = section.replace("Situation Analysis:", "").strip()
            elif section.startswith("Eligibility Status:"):
                eligibility = section.replace("Eligibility Status:", "").strip()
            elif section.startswith("Recommendations:"):
                recommendations = section.replace("Recommendations:", "").strip()
            elif section.startswith("Action Items:"):
                actions = section.replace("Action Items:", "").strip()
        
        # Format response according to the API schema
        return {
            "message": situation,
            "details": {
                "eligibility_status": eligibility,
                "recommendations": recommendations,
                "action_items": actions,
                "source": "Eligibility Agent Analysis",
                "analysis_type": "HSA/FSA/COBRA Eligibility Assessment"
            }
        }
    
    def _parse_recommendations_response(self, recommendations: str) -> Dict[str, any]:
        """Parse recommendations into structured data."""
        return {
            "message": recommendations,
            "details": {
                "timestamp": datetime.now().isoformat(),
                "confidence_level": "high"  # This would be determined by analysis
            }
        } 