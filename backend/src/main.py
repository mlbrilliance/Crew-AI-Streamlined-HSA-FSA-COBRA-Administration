from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agents.manager_agent import ManagerAgent
from .agents.eligibility_agent import EligibilityAgent
import os
from dotenv import load_dotenv, find_dotenv
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(find_dotenv())

# Get API key and print debug info
openai_api_key = os.getenv("OPENAI_API_KEY")
print(f"Debug - Main - API Key exists: {bool(openai_api_key)}")
print(f"Debug - Main - API Key length: {len(openai_api_key) if openai_api_key else 0}")
print(f"Debug - Main - Current working directory: {os.getcwd()}")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

app = FastAPI(
    title="Benefits Administration AI",
    description="AI-powered benefits administration assistant",
    version="1.0.0"
)

class BenefitsQuery(BaseModel):
    """Model for benefits query requests."""
    employee_id: str
    query: str

class AnalyzeRequest(BaseModel):
    """Request model for analysis endpoint."""
    employee_id: str
    query: str

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint returning service information."""
    return {
        "service": "Benefits Administration AI",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/manager/analyze")
async def analyze_with_manager(query: BenefitsQuery) -> Dict[str, Any]:
    """
    Analyze a benefits query using the Manager Agent.
    
    Args:
        query: The benefits query containing employee ID and question.
        
    Returns:
        Dict[str, Any]: Analysis results and recommendations.
    """
    try:
        logger.debug("Creating ManagerAgent instance")
        manager = ManagerAgent()
        
        logger.debug(f"Analyzing query for employee {query.employee_id}: {query.query}")
        result = await manager.analyze_query(
            employee_id=query.employee_id,
            query=query.query
        )
        logger.debug(f"Analysis result: {result}")
        
        return result
    except Exception as e:
        logger.error(f"Error analyzing query: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing query: {str(e)}"
        )

@app.post("/benefits/analyze")
async def analyze_benefits(query: BenefitsQuery) -> Dict[str, Any]:
    """
    Analyze benefits eligibility using the Eligibility Agent.
    
    Args:
        query: The benefits query containing employee ID and question.
        
    Returns:
        Dict[str, Any]: Eligibility analysis results.
    """
    try:
        agent = EligibilityAgent()
        result = await agent.analyze_benefits_scenario(
            employee_id=query.employee_id,
            query=query.query
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing benefits: {str(e)}"
        ) 