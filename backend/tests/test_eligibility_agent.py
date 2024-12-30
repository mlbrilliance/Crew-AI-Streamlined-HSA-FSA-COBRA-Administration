import pytest
from agents.eligibility_agent import EligibilityAgent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture
def agent():
    """Fixture to provide an EligibilityAgent instance."""
    return EligibilityAgent()

@pytest.mark.asyncio
async def test_analyze_benefits_scenario(agent):
    """Test analyzing a benefits scenario."""
    scenario = """
    Employee is 35 years old, married with 2 children.
    Currently enrolled in a high-deductible health plan (HDHP) with $3000 deductible.
    Annual income: $75,000
    Expected medical expenses: $2000 for the year
    No Medicare enrollment
    Interested in HSA vs FSA options
    """
    
    result = await agent.analyze_benefits_scenario(scenario)
    
    assert isinstance(result, dict)
    assert "situation_analysis" in result
    assert "eligibility_status" in result
    assert "recommendations" in result
    assert "action_items" in result
    assert len(result["raw_analysis"]) > 0 