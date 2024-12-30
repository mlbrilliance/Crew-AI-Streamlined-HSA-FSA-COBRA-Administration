from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from src.agents.eligibility_agent import EligibilityAgent
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize the agent
try:
    eligibility_agent = EligibilityAgent()
    logger.info("EligibilityAgent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize EligibilityAgent: {str(e)}")
    raise

class BenefitsScenario(BaseModel):
    scenario: str

@app.post("/benefits/analyze")
async def analyze_benefits(scenario: BenefitsScenario):
    """
    Analyze a benefits scenario and provide recommendations.
    """
    try:
        logger.debug(f"Analyzing benefits scenario: {scenario.scenario}")
        analysis = await eligibility_agent.analyze_benefits_scenario(scenario.scenario)
        logger.debug(f"Analysis completed successfully: {analysis}")
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing benefits scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy"} 