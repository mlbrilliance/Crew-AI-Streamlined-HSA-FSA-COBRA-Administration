from fastapi.testclient import TestClient
from typing import TYPE_CHECKING, Dict

from src.main import app

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

client = TestClient(app)

def test_read_root() -> None:
    """
    Test the root endpoint of the API.
    
    This test verifies that:
    1. The endpoint returns a 200 status code
    2. The response contains the expected welcome message
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the HSA/FSA/COBRA Administration API"}

def test_check_hsa_eligibility_eligible() -> None:
    """
    Test HSA eligibility check with valid criteria.
    
    This test verifies that:
    1. The endpoint accepts eligibility criteria
    2. Returns correct eligibility status for valid case
    """
    criteria: Dict[str, bool] = {
        "has_high_deductible_plan": True,
        "enrolled_in_medicare": False,
        "other_coverage": False
    }
    
    response = client.post("/hsa/check-eligibility", json=criteria)
    assert response.status_code == 200
    
    result = response.json()
    assert result["eligible"] is True
    assert result["explanation"] == "Eligible for HSA"

def test_check_hsa_eligibility_ineligible() -> None:
    """
    Test HSA eligibility check with invalid criteria.
    
    This test verifies that:
    1. The endpoint accepts eligibility criteria
    2. Returns correct eligibility status for invalid case
    """
    criteria: Dict[str, bool] = {
        "has_high_deductible_plan": True,
        "enrolled_in_medicare": True,
        "other_coverage": False
    }
    
    response = client.post("/hsa/check-eligibility", json=criteria)
    assert response.status_code == 200
    
    result = response.json()
    assert result["eligible"] is False
    assert result["explanation"] == "Not eligible due to coverage criteria" 