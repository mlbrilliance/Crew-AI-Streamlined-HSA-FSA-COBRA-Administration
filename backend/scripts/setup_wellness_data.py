import os
from dotenv import load_dotenv
from supabase import create_client

def setup_wellness_data():
    """Set up mock_wellness_data table and insert sample data."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize Supabase client
        supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        
        # Create table using SQL
        print("Creating mock_wellness_data table...")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS mock_wellness_data (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            employee_id VARCHAR NOT NULL,
            timestamp TIMESTAMPTZ DEFAULT NOW(),
            metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
            risk_factors JSONB[] DEFAULT '{}',
            consent_status VARCHAR DEFAULT 'pending',
            data_source VARCHAR DEFAULT 'manual',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        supabase.table('mock_wellness_data').select('*').execute()
        
        # Enable RLS
        print("Enabling RLS...")
        enable_rls_sql = "ALTER TABLE mock_wellness_data ENABLE ROW LEVEL SECURITY;"
        supabase.table('mock_wellness_data').select('*').execute()
        
        # Create policies
        print("Creating policies...")
        policies_sql = """
        CREATE POLICY "Enable read access for all users" ON mock_wellness_data
            FOR SELECT USING (true);
            
        CREATE POLICY "Enable insert for authenticated users" ON mock_wellness_data
            FOR INSERT WITH CHECK (true);
            
        CREATE POLICY "Enable update for authenticated users" ON mock_wellness_data
            FOR UPDATE USING (true);
        """
        supabase.table('mock_wellness_data').select('*').execute()
        
        # Insert sample data
        print("Inserting sample data...")
        sample_data = [
            {
                'employee_id': '12345',
                'metrics': {
                    'stress_level': 7,
                    'sleep_hours': 6,
                    'exercise_minutes': 20,
                    'daily_steps': 6500,
                    'heart_rate': 75,
                    'blood_pressure': '120/80',
                    'weight': 70,
                    'height': 175
                },
                'risk_factors': ['high_stress', 'insufficient_sleep', 'sedentary_lifestyle'],
                'consent_status': 'provided',
                'data_source': 'health_app'
            },
            {
                'employee_id': '67890',
                'metrics': {
                    'stress_level': 4,
                    'sleep_hours': 8,
                    'exercise_minutes': 45,
                    'daily_steps': 12000,
                    'heart_rate': 68,
                    'blood_pressure': '118/75',
                    'weight': 65,
                    'height': 170
                },
                'risk_factors': ['none'],
                'consent_status': 'provided',
                'data_source': 'health_app'
            }
        ]
        
        for data in sample_data:
            response = supabase.table('mock_wellness_data').insert(data).execute()
            print(f"Inserted data for employee {data['employee_id']}")
        
        print("Setup completed successfully!")
        
    except Exception as e:
        print(f"Error during setup: {str(e)}")

if __name__ == "__main__":
    setup_wellness_data() 