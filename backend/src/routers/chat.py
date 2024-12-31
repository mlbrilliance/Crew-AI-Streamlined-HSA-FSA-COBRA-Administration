from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime
from ..agents.manager_agent import ManagerAgent
import logging

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory store for conversation history
conversation_store = {}

class ChatMessage(BaseModel):
    """Model for chat messages."""
    employer_id: str
    message: str
    context: Optional[Dict] = None
    timestamp: Optional[datetime] = None

class ChatResponse(BaseModel):
    """Model for chat responses."""
    message: str
    details: Optional[Dict] = None
    suggestions: List[str] = []
    timestamp: datetime = datetime.now()

def get_conversation_history(employer_id: str, employee_id: Optional[str] = None) -> List[Dict]:
    """Get conversation history for a specific employer/employee."""
    key = f"{employer_id}:{employee_id}" if employee_id else employer_id
    return conversation_store.get(key, [])

def update_conversation_history(employer_id: str, message: Dict, employee_id: Optional[str] = None):
    """Update conversation history with new message."""
    key = f"{employer_id}:{employee_id}" if employee_id else employer_id
    if key not in conversation_store:
        conversation_store[key] = []
    conversation_store[key].append(message)
    # Keep last 10 messages for context
    conversation_store[key] = conversation_store[key][-10:]

@router.post("/message", response_model=ChatResponse)
async def process_chat_message(message: ChatMessage):
    """
    Process a chat message and return an agent-generated response.
    
    Args:
        message: ChatMessage containing the user's message and context
        
    Returns:
        ChatResponse containing the agent's response and suggestions
    """
    try:
        logger = logging.getLogger(__name__)
        logger.info(f"Processing chat message from employer ID {message.employer_id}")
        
        # Initialize the manager agent
        manager = ManagerAgent()
        
        # Add employer context to the message
        context = message.context or {}
        context.update({
            "employer_id": message.employer_id,
            "timestamp": message.timestamp or datetime.now()
        })
        
        # Get conversation history
        employee_id = context.get("employee_id")
        history = get_conversation_history(message.employer_id, employee_id)
        context["conversation_history"] = history
        
        # Route the query through the manager agent
        result = await manager.route_query(message.message, context)
        
        # Update conversation history with the new message and response
        update_conversation_history(
            message.employer_id,
            {
                "timestamp": context["timestamp"],
                "user_message": message.message,
                "agent_response": result,
                "context": context
            },
            employee_id
        )
        
        # Format the response for chat
        name = context.get("name", "there")
        response_message = f"Hi {name}! Thank you for your question. Let me help you with that.\n\n"
        response_message += result["response"]["message"] + "\n"

        if result["response"]["details"].get("eligibility_status"):
            response_message += f"\nBased on your situation:\n{result['response']['details']['eligibility_status']}\n"
        
        if result["response"]["details"].get("recommendations"):
            response_message += f"\nHere are my recommendations for you:\n{result['response']['details']['recommendations']}\n"
        
        # Add citations and sources
        sources = []
        if result["context"].get("additional_considerations"):
            response_message += f"\nImportant Considerations:\n{result['context']['additional_considerations']}\n"
            sources.append("IRS Guidelines")
        
        if result["response"]["details"].get("source"):
            sources.append(result["response"]["details"]["source"])
        
        if sources:
            response_message += f"\nSources: {', '.join(sources)}"
        
        response_message += "\n\nIs there anything else you'd like to know about your benefits?"
        
        return ChatResponse(
            message=response_message,
            details={
                "source": result["response"]["details"].get("source", "AI Assistant"),
                "analysis_type": result["response"]["details"].get("analysis_type", "General Query"),
                "processing_flow": result["context"].get("processing_flow", "Direct Response"),
                "conversation_id": f"{message.employer_id}:{employee_id}" if employee_id else message.employer_id
            },
            suggestions=[step for step in result["next_steps"] if step.strip()]
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing your message: {str(e)}"
        ) 