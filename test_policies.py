import sys
import traceback
from src.repositories.data_repository import DataRepository

def test_policies():
    try:
        repo = DataRepository()
        
        print("\nTesting FSA policies search:")
        fsa_policies = repo.get_relevant_policies("FSA reimbursement")
        print("FSA policies found:", fsa_policies)
        
        print("\nTesting HSA policies search:")
        hsa_policies = repo.get_relevant_policies("HSA eligibility")
        print("HSA policies found:", hsa_policies)
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print("Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_policies() 