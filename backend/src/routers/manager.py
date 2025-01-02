from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List, Union
from ..agents.manager_agent import ManagerAgent

router = APIRouter(prefix="/manager", tags=["manager"])

class QueryRequest(BaseModel):
    """Request model for query analysis and routing."""
    query: str
    context: Optional[Dict] = None

class ResponseDetails(BaseModel):
    """Model for detailed response information."""
    eligibility_status: Optional[str] = None
    recommendations: Optional[str] = None
    action_items: Optional[str] = None
    timestamp: Optional[str] = None
    confidence_level: Optional[str] = None

class ResponseContent(BaseModel):
    """Model for the response content."""
    message: str
    details: Optional[Union[ResponseDetails, Dict, str]] = None

class DebugEntry(BaseModel):
    """Model for agent debug information."""
    agent: str
    timestamp: str
    action: Optional[str] = None
    thought: Optional[str] = None
    reasoning: Optional[str] = None
    result: Optional[str] = None

class QueryResponse(BaseModel):
    """Response model for analyzed and routed queries."""
    response: ResponseContent
    context: Optional[Dict] = None
    next_steps: List[str]
    debug_info: Optional[List[DebugEntry]] = None

@router.post("/analyze", response_model=QueryResponse)
async def analyze_and_route_query(request: QueryRequest) -> QueryResponse:
    """
    Analyze and route a benefits-related query to appropriate agents.
    
    Args:
        request: QueryRequest containing the query and optional context.
        
    Returns:
        QueryResponse containing the processed response and next steps.
    """
    try:
        manager = ManagerAgent()
        result = await manager.route_query(request.query, request.context)
        
        # Ensure next_steps is a list
        if isinstance(result.get("next_steps"), str):
            result["next_steps"] = [result["next_steps"]]
        elif not result.get("next_steps"):
            result["next_steps"] = ["Please provide more information about your benefits scenario"]
            
        return QueryResponse(**result)
            
    except Exception as e:
        error_response = {
            "response": {
                "message": "Error processing request",
                "details": str(e)
            },
            "context": {"error": str(e)},
            "next_steps": ["Please try again with more specific information"],
            "debug_info": []
        }
        return QueryResponse(**error_response) 