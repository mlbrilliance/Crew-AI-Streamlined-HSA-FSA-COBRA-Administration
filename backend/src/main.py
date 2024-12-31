from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
from src.agents.eligibility_agent import EligibilityAgent
from src.routers import manager
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Verify OpenAI API key is loaded
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.error("OPENAI_API_KEY not found in environment variables")
    raise ValueError("OPENAI_API_KEY environment variable is not set")
else:
    logger.info("OPENAI_API_KEY loaded successfully")

app = FastAPI(
    title="Benefits Administration AI API",
    description="AI-powered benefits administration and analysis API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
try:
    eligibility_agent = EligibilityAgent()
    logger.info("EligibilityAgent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize EligibilityAgent: {str(e)}")
    raise

# Include routers
app.include_router(manager.router)

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