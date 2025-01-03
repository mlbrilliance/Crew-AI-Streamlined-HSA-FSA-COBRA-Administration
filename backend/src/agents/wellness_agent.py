"""
Wellness Agent Module

Specialized agent for handling wellness data retrieval, analysis, and health metrics processing.

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
from datetime import datetime
from pydantic import PrivateAttr


class WellnessAgent(Agent):
    """Agent responsible for wellness data analysis and health metrics processing."""
    
    _data_repo: DataRepository = PrivateAttr()
    
    def __init__(self):
        """Initialize the WellnessAgent."""
        # Load environment variables
        load_dotenv(find_dotenv())
        
        # Get API key and print debug info
        openai_api_key = os.getenv("OPENAI_API_KEY")
        print(f"Debug - Wellness Agent - API Key exists: {bool(openai_api_key)}")
        print(f"Debug - Wellness Agent - API Key length: {len(openai_api_key) if openai_api_key else 0}")
        print(f"Debug - Wellness Agent - Current working directory: {os.getcwd()}")
        
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        super().__init__(
            role='Wellness Specialist',
            goal='Analyze employee wellness data and provide health-aware recommendations',
            backstory="""You are an expert in employee wellness and health metrics analysis.
            You analyze employee health data to provide insights that inform benefits decisions
            and recommendations. You always ensure privacy and data protection while delivering
            actionable health insights.""",
            allow_delegation=False,
            llm=ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0,
                api_key=openai_api_key
            )
        )
        
        # Initialize data repository as a private attribute
        self._data_repo = DataRepository()

    def get_wellness_analysis(self, employee_id: str) -> Dict[str, Any]:
        """
        Retrieve and analyze employee wellness data.
        
        Args:
            employee_id: The ID of the employee.
            
        Returns:
            Dict[str, Any]: Analyzed wellness data including metrics and recommendations.
        """
        # Get wellness data
        wellness_data = self._data_repo.get_employee_risk_assessment(employee_id)
        if not wellness_data:
            return {
                "wellness_data": self._create_empty_wellness_data(),
                "debug_info": {
                    "agent": "Wellness Agent",
                    "timestamp": datetime.now().isoformat(),
                    "action": "Wellness Analysis",
                    "thought": "No wellness data available",
                    "reasoning": "Need to provide default response",
                    "result": "No risk factors identified"
                }
            }
            
        # Process and format the wellness data
        formatted_data = self._format_risk_assessment(wellness_data)
        
        # Add debug information
        debug_info = [{
            "agent": "Wellness Agent",
            "timestamp": datetime.now().isoformat(),
            "action": "Wellness Analysis",
            "thought": "Processing wellness metrics and risk factors",
            "reasoning": "Need to provide health context for benefits decisions",
            "result": f"Risk Factors: {len(wellness_data.get('risk_factors', []))} identified"
        }]
        
        return {
            "wellness_data": formatted_data,
            "debug_info": debug_info
        }

    def _create_empty_wellness_data(self) -> Dict[str, Any]:
        """Create empty wellness data structure."""
        return {
            "metrics": {
                "heart_rate": "N/A",
                "sleep_hours": "N/A",
                "exercise_minutes": "N/A",
                "daily_steps": "N/A",
                "stress_level": "N/A"
            },
            "risk_factors": [],
            "recommendations": []
        }

    def _format_risk_assessment(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format risk assessment information.
        
        Args:
            assessment: Raw assessment data.
            
        Returns:
            Dict[str, Any]: Formatted assessment data.
        """
        if not assessment or not assessment.get("metrics"):
            empty_data = self._create_empty_wellness_data()
            empty_data["recommendations"] = ["Consider scheduling a wellness check-up to establish your baseline health metrics."]
            return empty_data
            
        metrics = assessment.get("metrics", {})
        risk_factors = assessment.get("risk_factors", [])
        existing_recommendations = assessment.get("recommendations", [])
        
        # Generate health recommendations based on metrics and risk factors
        generated_recommendations = self._generate_health_recommendations(metrics, risk_factors)
        
        # Combine existing and generated recommendations, removing duplicates
        all_recommendations = list(set(existing_recommendations + generated_recommendations))
        
        return {
            "metrics": {
                "heart_rate": metrics.get("heart_rate", "N/A"),
                "sleep_hours": metrics.get("sleep_hours", "N/A"),
                "exercise_minutes": metrics.get("exercise_minutes", "N/A"),
                "daily_steps": metrics.get("daily_steps", "N/A"),
                "stress_level": metrics.get("stress_level", "N/A")
            },
            "risk_factors": risk_factors,
            "recommendations": all_recommendations
        }

    def _generate_health_recommendations(
        self,
        metrics: Dict[str, Any],
        risk_factors: List[str]
    ) -> List[str]:
        """
        Generate health recommendations based on metrics and risk factors.
        
        Args:
            metrics: Health metrics data.
            risk_factors: List of identified risk factors.
            
        Returns:
            List[str]: List of health recommendations.
        """
        recommendations = []
        
        try:
            # Convert metrics to integers for comparison, using 0 as default
            heart_rate = int(metrics.get("heart_rate", 0))
            sleep_hours = int(metrics.get("sleep_hours", 0))
            exercise_minutes = int(metrics.get("exercise_minutes", 0))
            daily_steps = int(metrics.get("daily_steps", 0))
            stress_level = int(metrics.get("stress_level", 0))
            
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
            recommendations.append(
                "Consider scheduling a wellness check-up to establish your baseline health metrics."
            )
            
        # Add recommendations based on risk factors
        if risk_factors:
            recommendations.append(
                "Discuss identified health risk factors with your healthcare provider during your next visit."
            )
            
        return recommendations or ["Schedule a wellness check-up to establish your baseline health metrics."] 