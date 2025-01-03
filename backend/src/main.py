"""
Benefits Administration Backend

A FastAPI backend service for the Benefits Administration system, powered by CrewAI and OpenAI.

Developer:
- Name: Nick Sudh
- Website: mlbrilliance.com
- GitHub: https://github.com/mlbrilliance
- Twitter: https://x.com/mlbrilliance
- BlueSky: https://bsky.app/profile/mlbrilliance.com
"""

from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .agents.manager_agent import ManagerAgent
from .agents.eligibility_agent import EligibilityAgent
import os
from dotenv import load_dotenv, find_dotenv
import traceback
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables with explicit path
backend_dir = Path(__file__).resolve().parent.parent
env_path = backend_dir / '.env'

print(f"Debug - Looking for .env file at: {env_path}")
print(f"Debug - File exists: {env_path.exists()}")

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=env_path)

# Get API key and print debug info
openai_api_key = os.getenv("OPENAI_API_KEY")
print(f"Debug - Main - API Key exists: {bool(openai_api_key)}")
print(f"Debug - Main - API Key length: {len(openai_api_key) if openai_api_key else 0}")
print(f"Debug - Main - Current working directory: {os.getcwd()}")
print(f"Debug - Main - Environment variables loaded: {list(os.environ.keys())}")

if not openai_api_key:
    print("Error: OPENAI_API_KEY not found in environment variables")
    print(f"Debug - Contents of .env file (if exists):")
    if env_path.exists():
        with open(env_path) as f:
            print(f.read())
    raise ValueError("OPENAI_API_KEY environment variable is not set")

app = FastAPI(
    title="Benefits Administration AI",
    description="AI-powered benefits administration assistant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class BenefitsQuery(BaseModel):
    """Model for benefits query requests."""
    employee_id: str
    query: str

class AnalyzeRequest(BaseModel):
    """Request model for analysis endpoint."""
    employee_id: str
    query: str

class DebugEntry(BaseModel):
    """Model for debug information entries."""
    agent: str
    timestamp: str
    action: Optional[str] = None
    thought: Optional[str] = None
    reasoning: Optional[str] = None
    result: Optional[str] = None

class ResponseDetails(BaseModel):
    recommendations: List[str] = []
    action_items: List[str] = []

class ResponseMessage(BaseModel):
    message: str
    details: ResponseDetails

class AnalyzeResponse(BaseModel):
    response: ResponseMessage
    next_steps: List[str] = []
    debug_info: List[DebugEntry] = []

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint returning service information."""
    return {
        "service": "Benefits Administration AI",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/manager/analyze", response_model=AnalyzeResponse)
async def analyze_with_manager(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze a benefits query using the Manager Agent.
    
    Args:
        request: AnalyzeRequest containing employee_id and query
        
    Returns:
        AnalyzeResponse containing the structured response with message, details, and next steps
    """
    try:
        logger.debug("Creating ManagerAgent instance")
        manager = ManagerAgent()
        
        logger.debug(f"Analyzing query for employee {request.employee_id}: {request.query}")
        result = await manager.analyze_query(
            employee_id=request.employee_id,
            query=request.query
        )
        logger.debug(f"Analysis result: {result}")
        
        # Return the result directly - it already has the correct structure
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