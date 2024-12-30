from typing import Dict, List, Optional
from crewai import Agent
from datetime import datetime
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

# Load environment variables
load_dotenv()

class EligibilityAgent(Agent):
    """
    AI-powered agent for analyzing benefits eligibility and providing personalized recommendations.
    
    This agent uses CrewAI to analyze complex scenarios,
    evaluate multiple benefit options, and provide detailed recommendations based
    on individual circumstances.
    """
    
    def __init__(self) -> None:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=openai_api_key
        )
            
        super().__init__(
            name="Benefits Analysis Specialist",
            role="Expert benefits analyst specializing in HSA, FSA, and COBRA eligibility",
            goal="Analyze complex benefit scenarios and provide personalized recommendations",
            backstory="""You are an expert benefits analyst with deep knowledge of 
            healthcare benefits, tax implications, and federal regulations. You excel 
            at analyzing complex scenarios and providing actionable recommendations.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        self.llm = llm
    
    async def analyze_benefits_scenario(self, scenario: str) -> Dict[str, any]:
        """
        Analyze a complex benefits scenario described in natural language.
        
        Args:
            scenario: Natural language description of an individual's situation,
                     including their health needs, financial situation, and current benefits.
        
        Returns:
            Dict containing analysis results, recommendations, and explanations.
        """
        task = f"""Analyze this benefits scenario and provide detailed recommendations:
{scenario}

Consider:
1. HSA/FSA eligibility and optimal contribution strategies
2. Tax implications and savings opportunities
3. Potential risks or coverage gaps
4. Alternative benefit options
5. Specific action items

Format your response as:
- Situation Analysis
- Eligibility Status
- Recommendations
- Action Items
"""
        messages = [HumanMessage(content=task)]
        analysis = await self.llm.ainvoke(messages)
        return self._parse_analysis_response(analysis.content)
    
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
        
        return {
            "situation_analysis": sections[0] if len(sections) > 0 else "",
            "eligibility_status": sections[1] if len(sections) > 1 else "",
            "recommendations": sections[2] if len(sections) > 2 else "",
            "action_items": sections[3] if len(sections) > 3 else "",
            "raw_analysis": analysis
        }
    
    def _parse_recommendations_response(self, recommendations: str) -> Dict[str, any]:
        """Parse recommendations into structured data."""
        return {
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
            "confidence_level": "high"  # This would be determined by analysis
        } 