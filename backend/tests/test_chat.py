import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from src.main import app

client = TestClient(app)

def test_chat_message_processing():
    """Test that chat messages are properly processed by the agents."""
    message = {
        "employer_id": "EMP123",
        "message": "I'm starting a new job next month and need to understand my HSA eligibility. I have a family HDHP plan with a $3000 deductible and $6000 out-of-pocket maximum. My employer offers a $1000 HSA contribution. What are my contribution limits and how should I optimize my HSA?",
        "context": {
            "employee_status": "new hire",
            "plan_type": "family HDHP",
            "deductible": 3000,
            "out_of_pocket_max": 6000,
            "employer_contribution": 1000
        },
        "timestamp": datetime.now().isoformat()
    }
    
    response = client.post("/chat/message", json=message)
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "details" in data
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)
    
    # Verify agent interaction
    assert "source" in data["details"]
    assert "analysis_type" in data["details"]
    assert "processing_flow" in data["details"]
    
    # Verify response content
    assert "HSA" in data["message"]
    assert "eligibility" in data["message"].lower()
    assert len(data["suggestions"]) > 0 