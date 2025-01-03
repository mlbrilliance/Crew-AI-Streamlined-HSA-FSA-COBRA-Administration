"""Test module for WellnessAgent."""

import pytest
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

if True:  # TYPE_CHECKING
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

from ..src.agents.wellness_agent import WellnessAgent
from ..src.repositories.data_repository import DataRepository


@pytest.fixture
def mock_data_repo(mocker: "MockerFixture") -> MagicMock:
    """Create a mock DataRepository."""
    mock = MagicMock(spec=DataRepository)
    mock.get_employee_risk_assessment.return_value = {
        "metrics": {
            "heart_rate": "75",
            "sleep_hours": "7",
            "exercise_minutes": "30",
            "daily_steps": "8000",
            "stress_level": "4"
        },
        "risk_factors": ["Sedentary lifestyle"],
        "recommendations": ["Increase daily activity"]
    }
    return mock


@pytest.fixture
def wellness_agent(mocker: "MockerFixture", mock_data_repo: MagicMock) -> WellnessAgent:
    """Create a WellnessAgent instance with mocked dependencies."""
    # Mock environment variables
    mocker.patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    
    # Mock ChatOpenAI
    mocker.patch("src.agents.wellness_agent.ChatOpenAI")
    
    # Create agent and set mocked data_repo
    agent = WellnessAgent()
    agent._data_repo = mock_data_repo
    
    return agent


@pytest.mark.asyncio
async def test_get_wellness_analysis_success(
    wellness_agent: WellnessAgent,
    mock_data_repo: MagicMock
) -> None:
    """Test successful wellness analysis retrieval."""
    # Arrange
    employee_id = "test-employee"
    
    # Act
    result = await wellness_agent.get_wellness_analysis(employee_id)
    
    # Assert
    assert isinstance(result, dict)
    assert "wellness_data" in result
    assert "debug_info" in result
    
    wellness_data = result["wellness_data"]
    assert "metrics" in wellness_data
    assert "risk_factors" in wellness_data
    assert "recommendations" in wellness_data
    
    metrics = wellness_data["metrics"]
    assert metrics["heart_rate"] == "75"
    assert metrics["sleep_hours"] == "7"
    assert metrics["exercise_minutes"] == "30"
    assert metrics["daily_steps"] == "8000"
    assert metrics["stress_level"] == "4"
    
    assert wellness_data["risk_factors"] == ["Sedentary lifestyle"]
    assert len(wellness_data["recommendations"]) > 0


@pytest.mark.asyncio
async def test_get_wellness_analysis_no_data(
    wellness_agent: WellnessAgent,
    mock_data_repo: MagicMock
) -> None:
    """Test wellness analysis when no data is available."""
    # Arrange
    employee_id = "test-employee"
    mock_data_repo.get_employee_risk_assessment.return_value = None
    
    # Act
    result = await wellness_agent.get_wellness_analysis(employee_id)
    
    # Assert
    assert isinstance(result, dict)
    assert "wellness_data" in result
    
    wellness_data = result["wellness_data"]
    assert wellness_data["metrics"]["heart_rate"] == "N/A"
    assert wellness_data["metrics"]["sleep_hours"] == "N/A"
    assert wellness_data["metrics"]["exercise_minutes"] == "N/A"
    assert wellness_data["metrics"]["daily_steps"] == "N/A"
    assert wellness_data["metrics"]["stress_level"] == "N/A"
    assert wellness_data["risk_factors"] == []
    assert wellness_data["recommendations"] == []


def test_format_risk_assessment_with_data(wellness_agent: WellnessAgent) -> None:
    """Test risk assessment formatting with valid data."""
    # Arrange
    assessment_data = {
        "metrics": {
            "heart_rate": "80",
            "sleep_hours": "6",
            "exercise_minutes": "20",
            "daily_steps": "5000",
            "stress_level": "7"
        },
        "risk_factors": ["High stress", "Low activity"],
        "recommendations": []
    }
    
    # Act
    result = wellness_agent._format_risk_assessment(assessment_data)
    
    # Assert
    assert isinstance(result, dict)
    assert "metrics" in result
    assert "risk_factors" in result
    assert "recommendations" in result
    
    # Check metrics
    metrics = result["metrics"]
    assert metrics["heart_rate"] == "80"
    assert metrics["sleep_hours"] == "6"
    assert metrics["exercise_minutes"] == "20"
    assert metrics["daily_steps"] == "5000"
    assert metrics["stress_level"] == "7"
    
    # Check recommendations generation
    recommendations = result["recommendations"]
    assert len(recommendations) > 0
    assert any("sleep" in r.lower() for r in recommendations)
    assert any("exercise" in r.lower() for r in recommendations)
    assert any("stress" in r.lower() for r in recommendations)


def test_format_risk_assessment_empty_data(wellness_agent: WellnessAgent) -> None:
    """Test risk assessment formatting with empty data."""
    # Arrange
    assessment_data = {}
    
    # Act
    result = wellness_agent._format_risk_assessment(assessment_data)
    
    # Assert
    assert isinstance(result, dict)
    assert result["metrics"]["heart_rate"] == "N/A"
    assert result["metrics"]["sleep_hours"] == "N/A"
    assert result["metrics"]["exercise_minutes"] == "N/A"
    assert result["metrics"]["daily_steps"] == "N/A"
    assert result["metrics"]["stress_level"] == "N/A"
    assert result["risk_factors"] == []
    assert len(result["recommendations"]) == 1
    assert "wellness check-up" in result["recommendations"][0].lower()


def test_generate_health_recommendations(wellness_agent: WellnessAgent) -> None:
    """Test health recommendations generation."""
    # Arrange
    metrics = {
        "heart_rate": "85",
        "sleep_hours": "5",
        "exercise_minutes": "15",
        "daily_steps": "4000",
        "stress_level": "8"
    }
    risk_factors = ["High blood pressure", "Obesity"]
    
    # Act
    recommendations = wellness_agent._generate_health_recommendations(metrics, risk_factors)
    
    # Assert
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    
    # Check for specific recommendations based on metrics
    assert any("heart rate" in r.lower() for r in recommendations)
    assert any("sleep" in r.lower() for r in recommendations)
    assert any("exercise" in r.lower() for r in recommendations)
    assert any("steps" in r.lower() for r in recommendations)
    assert any("stress" in r.lower() for r in recommendations)
    
    # Check for risk factor related recommendation
    assert any("risk factors" in r.lower() for r in recommendations) 