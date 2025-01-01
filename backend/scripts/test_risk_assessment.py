import os
import json
from dotenv import load_dotenv
from src.repositories.data_repository import DataRepository

def test_risk_assessment():
    """Test the get_employee_risk_assessment method."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize repository
        repo = DataRepository()
        
        # Test for employee 12345 (Fitbit user with sleep deficiency)
        print("\nTesting risk assessment for employee 12345:")
        assessment_12345 = repo.get_employee_risk_assessment('12345')
        print("\nEmployee 12345 (Fitbit User):")
        print(f"Timestamp: {assessment_12345.get('timestamp')}")
        print(f"Metrics: {json.dumps(assessment_12345.get('metrics'), indent=2)}")
        print(f"Risk Factors: {assessment_12345.get('risk_factors')}")
        print(f"Recommendations: {json.dumps(assessment_12345.get('recommendations'), indent=2)}")
        
        # Test for employee 67890 (Apple Watch user with high stress)
        print("\nTesting risk assessment for employee 67890:")
        assessment_67890 = repo.get_employee_risk_assessment('67890')
        print("\nEmployee 67890 (Apple Watch User):")
        print(f"Timestamp: {assessment_67890.get('timestamp')}")
        print(f"Metrics: {json.dumps(assessment_67890.get('metrics'), indent=2)}")
        print(f"Risk Factors: {assessment_67890.get('risk_factors')}")
        print(f"Recommendations: {json.dumps(assessment_67890.get('recommendations'), indent=2)}")
        
        # Test for employee 13579 (Samsung Health user with good metrics)
        print("\nTesting risk assessment for employee 13579:")
        assessment_13579 = repo.get_employee_risk_assessment('13579')
        print("\nEmployee 13579 (Samsung Health User):")
        print(f"Timestamp: {assessment_13579.get('timestamp')}")
        print(f"Metrics: {json.dumps(assessment_13579.get('metrics'), indent=2)}")
        print(f"Risk Factors: {assessment_13579.get('risk_factors')}")
        print(f"Recommendations: {json.dumps(assessment_13579.get('recommendations'), indent=2)}")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    test_risk_assessment() 