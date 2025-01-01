from typing import Dict, List, Any
import pytest
from datetime import datetime
from ..src.repositories.data_repository import DataRepository

@pytest.fixture
def data_repository():
    """Fixture to create a DataRepository instance."""
    return DataRepository()

@pytest.fixture
def sample_chat_messages():
    """Fixture to provide sample chat messages."""
    return [
        {
            "id": "1",
            "text": "Hello, I have a question about my HSA.",
            "sender": "user",
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": "2",
            "text": "I'd be happy to help you with your HSA question.",
            "sender": "assistant",
            "timestamp": datetime.now().isoformat()
        }
    ]

def test_get_chat_history_empty(data_repository):
    """Test getting chat history for an employee with no history."""
    # Test with a non-existent employee ID
    history = data_repository.get_chat_history("nonexistent_id")
    assert isinstance(history, list)
    assert len(history) == 0

def test_get_chat_history_with_data(data_repository):
    """Test getting chat history for an employee with existing history."""
    # Use a known test employee ID that exists in your Supabase database
    employee_id = "12345"  # This should match an ID in your mock_employees table
    
    history = data_repository.get_chat_history(employee_id)
    assert isinstance(history, dict)
    assert "messages" in history
    assert isinstance(history["messages"], list)
    assert len(history["messages"]) > 0
    
    # Verify message structure
    for message in history["messages"]:
        assert isinstance(message, dict)
        assert "role" in message or "sender" in message
        assert "content" in message or "text" in message
        assert "timestamp" in message

def test_save_chat_interaction(data_repository, sample_chat_messages):
    """Test saving chat messages to Supabase."""
    # Use a known test employee ID
    employee_id = "12345"
    
    # Save the messages
    success = data_repository.save_chat_interaction(employee_id, sample_chat_messages)
    assert success is True
    
    # Verify the messages were saved by retrieving them
    saved_history = data_repository.get_chat_history(employee_id)
    assert isinstance(saved_history, dict)
    assert "messages" in saved_history
    assert isinstance(saved_history["messages"], list)
    assert len(saved_history["messages"]) > 0
    
    # Verify the last message matches what we saved
    last_message = saved_history["messages"][-1]
    assert isinstance(last_message, dict)
    assert "timestamp" in last_message
    assert "role" in last_message or "sender" in last_message
    assert "content" in last_message or "text" in last_message 

def test_get_employee_risk_assessment(data_repository):
    """Test getting employee risk assessment data."""
    # Use a known test employee ID
    employee_id = "12345"
    
    # Get risk assessment
    assessment = data_repository.get_employee_risk_assessment(employee_id)
    
    # Verify structure
    assert isinstance(assessment, dict)
    assert "timestamp" in assessment
    assert "metrics" in assessment
    assert "risk_factors" in assessment
    assert "recommendations" in assessment
    
    # Verify metrics
    metrics = assessment["metrics"]
    assert isinstance(metrics, dict)
    
    # Verify risk factors
    risk_factors = assessment["risk_factors"]
    assert isinstance(risk_factors, list)
    
    # Verify recommendations
    recommendations = assessment["recommendations"]
    assert isinstance(recommendations, list)
    
    # If there are recommendations, verify their structure
    for rec in recommendations:
        assert isinstance(rec, dict)
        assert "category" in rec
        assert "message" in rec
        assert isinstance(rec["category"], str)
        assert isinstance(rec["message"], str) 