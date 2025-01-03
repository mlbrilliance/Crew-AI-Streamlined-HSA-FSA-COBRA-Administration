import os
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any
from dotenv import load_dotenv
from supabase import create_client, Client

def generate_sample_data() -> Dict[str, List[Dict[str, Any]]]:
    """Generate sample data for all tables."""
    current_date = datetime.now()
    
    employees = [
        {
            "employee_id": "EMP001",
            "name": "John Smith",
            "email": "john.smith@example.com",
            "dob": "1985-03-15",
            "hsa_eligible": True,
            "fsa_eligible": True,
            "cobra_status": "not_applicable"
        },
        {
            "employee_id": "EMP002",
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "dob": "1990-07-22",
            "hsa_eligible": False,
            "fsa_eligible": True,
            "cobra_status": "eligible"
        }
    ]
    
    dependents = [
        {
            "employee_id": "EMP001",
            "name": "Sarah Smith",
            "relationship": "spouse",
            "dob": "1987-11-30"
        },
        {
            "employee_id": "EMP001",
            "name": "Tommy Smith",
            "relationship": "child",
            "dob": "2015-04-10"
        }
    ]
    
    claims = [
        {
            "claim_id": "CLM001",
            "employee_id": "EMP001",
            "type": "medical",
            "description": "Annual physical examination",
            "amount": 150.00,
            "date": (current_date - timedelta(days=30)).strftime("%Y-%m-%d"),
            "status": "approved"
        },
        {
            "claim_id": "CLM002",
            "employee_id": "EMP002",
            "type": "dental",
            "description": "Routine cleaning",
            "amount": 75.00,
            "date": (current_date - timedelta(days=15)).strftime("%Y-%m-%d"),
            "status": "pending"
        }
    ]
    
    life_events = [
        {
            "event_id": "EVT001",
            "employee_id": "EMP001",
            "event_type": "marriage",
            "event_date": "2023-06-15",
            "dependent": "Sarah Smith"
        },
        {
            "event_id": "EVT002",
            "employee_id": "EMP001",
            "event_type": "birth",
            "event_date": "2015-04-10",
            "dependent": "Tommy Smith"
        }
    ]
    
    cobra_events = [
        {
            "employee_id": "EMP002",
            "event_type": "termination",
            "event_date": "2023-12-31",
            "cobra_start_date": "2024-01-01",
            "cobra_end_date": "2024-07-01"
        }
    ]
    
    wellness_data = [
        {
            "employee_id": "EMP001",
            "timestamp": (current_date - timedelta(days=7)).isoformat(),
            "metrics": {
                "stress_level": 4,
                "sleep_hours": 7.5,
                "sleep_quality": "good",
                "exercise_minutes": 45,
                "heart_rate": 72
            },
            "risk_factors": ["sedentary_lifestyle"],
            "data_source": "wellness_app",
            "consent_status": "approved"
        },
        {
            "employee_id": "EMP002",
            "timestamp": (current_date - timedelta(days=7)).isoformat(),
            "metrics": {
                "stress_level": 8,
                "sleep_hours": 5.5,
                "sleep_quality": "poor",
                "exercise_minutes": 15,
                "heart_rate": 85
            },
            "risk_factors": ["high_stress", "poor_sleep"],
            "data_source": "wellness_app",
            "consent_status": "approved"
        }
    ]
    
    chat_sessions = [
        {
            "employee_id": "EMP001",
            "started_at": (current_date - timedelta(days=1)).isoformat(),
            "ended_at": (current_date - timedelta(days=1, hours=23)).isoformat(),
            "status": "completed"
        }
    ]
    
    chat_history = [
        {
            "employee_id": "EMP001",
            "chat_history": json.dumps([
                {"role": "user", "content": "How do I check my HSA balance?"},
                {"role": "assistant", "content": "You can check your HSA balance by logging into the benefits portal..."}
            ]),
            "timestamp": (current_date - timedelta(days=1)).isoformat()
        }
    ]
    
    policy_documents = [
        {
            "policy_id": "POL001",
            "policy_name": "HSA Eligibility Guidelines",
            "category": "benefits",
            "policy_text": """
            Health Savings Account (HSA) Eligibility Guidelines:
            
            1. Must be enrolled in a High Deductible Health Plan (HDHP)
            2. Cannot be enrolled in Medicare
            3. Cannot be claimed as a dependent on someone else's tax return
            4. Cannot have other health coverage that pays for out-of-pocket expenses before the deductible is met
            
            Annual contribution limits apply as set by the IRS.
            """,
            "version": "1.0",
            "effective_date": "2024-01-01",
            "last_reviewed_date": "2023-12-15"
        }
    ]
    
    policy_versions = [
        {
            "policy_id": "POL001",
            "version": "1.0",
            "policy_text": """
            Health Savings Account (HSA) Eligibility Guidelines:
            
            1. Must be enrolled in a High Deductible Health Plan (HDHP)
            2. Cannot be enrolled in Medicare
            3. Cannot be claimed as a dependent on someone else's tax return
            4. Cannot have other health coverage that pays for out-of-pocket expenses before the deductible is met
            
            Annual contribution limits apply as set by the IRS.
            """,
            "changed_by": "Admin",
            "change_notes": "Initial version",
            "change_date": "2023-12-15T00:00:00Z"
        }
    ]
    
    return {
        "employees": employees,
        "dependents": dependents,
        "claims": claims,
        "life_events": life_events,
        "cobra_events": cobra_events,
        "wellness_data": wellness_data,
        "chat_sessions": chat_sessions,
        "chat_history": chat_history,
        "policy_documents": policy_documents,
        "policy_versions": policy_versions
    }

def seed_database():
    """Seed the database with sample data."""
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")
        
    print(f"Debug - Supabase URL: {supabase_url}")
    print(f"Debug - Service Role Key exists: {bool(supabase_key)}")
    print(f"Debug - Service Role Key length: {len(supabase_key) if supabase_key else 0}")
        
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Generate sample data
    data = generate_sample_data()
    
    try:
        # Insert data into each table
        for table, records in data.items():
            print(f"\nSeeding {table}...")
            for record in records:
                try:
                    supabase.table(table).insert(record).execute()
                    print(f"Successfully inserted record into {table}")
                except Exception as e:
                    print(f"Error inserting record into {table}: {str(e)}")
                    continue
                    
        print("\nDatabase seeding completed successfully")
        
    except Exception as e:
        print(f"Error seeding database: {str(e)}")
        raise

if __name__ == "__main__":
    seed_database() 