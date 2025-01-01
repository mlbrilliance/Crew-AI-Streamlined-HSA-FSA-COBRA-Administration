import pytest
from src.repositories.data_repository import DataRepository

def test_get_relevant_policies():
    """Test the get_relevant_policies method."""
    repo = DataRepository()
    
    # Test FSA policy search
    fsa_policies = repo.get_relevant_policies("FSA reimbursement")
    assert len(fsa_policies) > 0, "Should find FSA policies"
    assert any("FSA" in policy["policy_name"] for policy in fsa_policies)
    
    # Test HSA policy search
    hsa_policies = repo.get_relevant_policies("HSA eligibility")
    assert len(hsa_policies) > 0, "Should find HSA policies"
    assert any("HSA" in policy["policy_name"] for policy in hsa_policies)
    
    # Test empty search
    empty_policies = repo.get_relevant_policies("")
    assert len(empty_policies) == 0, "Empty search should return no policies" 

def test_get_employee_risk_assessment():
    """Test the get_employee_risk_assessment method."""
    repo = DataRepository()
    
    # Test successful case with all metrics
    assessment = repo.get_employee_risk_assessment("12345")
    assert assessment is not None, "Should return an assessment"
    assert "timestamp" in assessment, "Should include timestamp"
    assert "metrics" in assessment, "Should include metrics"
    assert "risk_factors" in assessment, "Should include risk factors"
    assert "recommendations" in assessment, "Should include recommendations"
    assert "consent_status" in assessment, "Should include consent status"
    assert "data_source" in assessment, "Should include data source"
    
    # Verify metrics are properly extracted
    metrics = assessment["metrics"]
    assert isinstance(metrics, dict), "Metrics should be a dictionary"
    assert "stress_level" in metrics, "Should include stress level"
    assert "sleep_hours" in metrics, "Should include sleep hours"
    assert "exercise_minutes" in metrics, "Should include exercise minutes"
    assert "daily_steps" in metrics, "Should include daily steps"
    
    # Verify recommendations are generated based on metrics
    recommendations = assessment["recommendations"]
    assert isinstance(recommendations, list), "Recommendations should be a list"
    
    # Test stress level recommendations
    if metrics.get("stress_level", 0) > 6:
        assert any("stress" in r.lower() for r in recommendations), \
            "Should recommend stress management for high stress"
    
    # Test sleep recommendations
    if metrics.get("sleep_hours", 0) < 7:
        assert any("sleep" in r.lower() for r in recommendations), \
            "Should recommend more sleep for low sleep hours"
    
    # Test exercise recommendations
    if metrics.get("exercise_minutes", 0) < 30:
        assert any("exercise" in r.lower() for r in recommendations), \
            "Should recommend more exercise for low activity"
    
    # Test steps recommendations
    if metrics.get("daily_steps", 0) < 8000:
        assert any("steps" in r.lower() for r in recommendations), \
            "Should recommend more steps for low step count"
    
    # Test case with non-existent employee
    empty_assessment = repo.get_employee_risk_assessment("nonexistent")
    assert empty_assessment["metrics"] == {}, "Should return empty metrics for non-existent employee"
    assert empty_assessment["risk_factors"] == [], "Should return empty risk factors for non-existent employee"
    assert empty_assessment["recommendations"] == [], "Should return empty recommendations for non-existent employee"
    assert empty_assessment["consent_status"] == "pending", "Should return pending consent status for non-existent employee"
    assert empty_assessment["data_source"] == "none", "Should return none as data source for non-existent employee" 