import os
from dotenv import load_dotenv
from supabase import create_client, Client

def init_database():
    """Initialize the database with required tables if they don't exist."""
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")
        
    print(f"Debug - Supabase URL: {supabase_url}")
    print(f"Debug - Service Role Key exists: {bool(supabase_key)}")
    print(f"Debug - Service Role Key length: {len(supabase_key) if supabase_key else 0}")
        
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Create tables using raw SQL
    tables = [
        """
        create table if not exists mock_employees (
            employee_id text primary key,
            name text not null,
            email text unique,
            dob date,
            hsa_eligible boolean default false,
            fsa_eligible boolean default false,
            cobra_status text default 'not_applicable',
            created_at timestamp with time zone default timezone('utc'::text, now()),
            updated_at timestamp with time zone default timezone('utc'::text, now())
        );
        """,
        """
        create table if not exists mock_employee_dependents (
            id uuid primary key default gen_random_uuid(),
            employee_id text references mock_employees(employee_id),
            name text not null,
            relationship text not null,
            dob date,
            created_at timestamp with time zone default timezone('utc'::text, now()),
            updated_at timestamp with time zone default timezone('utc'::text, now())
        );
        """,
        """
        create table if not exists mock_claims (
            claim_id text primary key,
            employee_id text references mock_employees(employee_id),
            type text not null,
            description text,
            amount decimal(10,2),
            date date not null,
            status text default 'pending',
            created_at timestamp with time zone default timezone('utc'::text, now()),
            updated_at timestamp with time zone default timezone('utc'::text, now())
        );
        """,
        """
        create table if not exists mock_life_events (
            event_id text primary key,
            employee_id text references mock_employees(employee_id),
            event_type text not null,
            event_date date not null,
            dependent text,
            created_at timestamp with time zone default timezone('utc'::text, now()),
            updated_at timestamp with time zone default timezone('utc'::text, now())
        );
        """,
        """
        create table if not exists mock_cobra_events (
            id uuid primary key default gen_random_uuid(),
            employee_id text references mock_employees(employee_id),
            event_type text not null,
            event_date date not null,
            cobra_start_date date,
            cobra_end_date date,
            created_at timestamp with time zone default timezone('utc'::text, now()),
            updated_at timestamp with time zone default timezone('utc'::text, now())
        );
        """,
        """
        create table if not exists mock_wellness_data (
            id uuid primary key default gen_random_uuid(),
            employee_id text references mock_employees(employee_id),
            timestamp timestamp with time zone not null,
            metrics jsonb,
            risk_factors text[],
            data_source text not null,
            consent_status text default 'pending',
            created_at timestamp with time zone default timezone('utc'::text, now()),
            updated_at timestamp with time zone default timezone('utc'::text, now())
        );
        """,
        """
        create table if not exists mock_chat_sessions (
            id uuid primary key default gen_random_uuid(),
            employee_id text references mock_employees(employee_id),
            started_at timestamp with time zone not null,
            ended_at timestamp with time zone,
            status text default 'active',
            created_at timestamp with time zone default timezone('utc'::text, now()),
            updated_at timestamp with time zone default timezone('utc'::text, now())
        );
        """,
        """
        create table if not exists mock_chat_history (
            id uuid primary key default gen_random_uuid(),
            employee_id text references mock_employees(employee_id),
            chat_history jsonb not null,
            timestamp timestamp with time zone not null,
            created_at timestamp with time zone default timezone('utc'::text, now()),
            updated_at timestamp with time zone default timezone('utc'::text, now())
        );
        """,
        """
        create table if not exists mock_policy_documents (
            policy_id text primary key,
            policy_name text not null,
            category text not null,
            policy_text text not null,
            version text not null,
            effective_date date not null,
            last_reviewed_date date,
            created_at timestamp with time zone default timezone('utc'::text, now()),
            updated_at timestamp with time zone default timezone('utc'::text, now()),
            search_vector tsvector generated always as (to_tsvector('english', policy_text)) stored
        );
        """,
        """
        create table if not exists mock_policy_document_versions (
            id uuid primary key default gen_random_uuid(),
            policy_id text references mock_policy_documents(policy_id),
            version text not null,
            policy_text text not null,
            changed_by text,
            change_notes text,
            change_date timestamp with time zone not null
        );
        """
    ]
    
    # Create views
    views = [
        """
        create or replace view active_policies as
        select 
            policy_id,
            policy_name,
            category,
            version,
            effective_date,
            last_reviewed_date
        from mock_policy_documents
        where effective_date <= current_date
        and (select count(*) from mock_policy_document_versions v 
             where v.policy_id = mock_policy_documents.policy_id 
             and v.change_date > mock_policy_documents.updated_at) = 0;
        """,
        """
        create or replace view high_stress_employees as
        select 
            employee_id,
            timestamp,
            (metrics->>'stress_level')::numeric as stress_score
        from mock_wellness_data
        where metrics->>'stress_level' is not null
        and (metrics->>'stress_level')::numeric > 7
        and timestamp >= current_date - interval '30 days';
        """,
        """
        create or replace view sleep_quality_summary as
        select 
            employee_id,
            avg((metrics->>'sleep_hours')::numeric) as avg_sleep_hours,
            mode() within group (order by metrics->>'sleep_quality') as typical_sleep_quality
        from mock_wellness_data
        where metrics->>'sleep_hours' is not null
        and metrics->>'sleep_quality' is not null
        and timestamp >= current_date - interval '30 days'
        group by employee_id;
        """
    ]
    
    # Create RLS policies
    policies = [
        """
        alter table mock_employees enable row level security;
        create policy "Enable read access for authenticated users"
        on mock_employees for select
        using (auth.role() = 'authenticated');
        
        create policy "Enable insert for service role"
        on mock_employees for insert
        with check (auth.role() = 'service_role');
        """,
        """
        alter table mock_wellness_data enable row level security;
        create policy "Enable read access for authenticated users"
        on mock_wellness_data for select
        using (auth.role() = 'authenticated');
        
        create policy "Enable insert for service role"
        on mock_wellness_data for insert
        with check (auth.role() = 'service_role');
        """
    ]
    
    try:
        # Create tables
        for table_sql in tables:
            try:
                supabase.postgrest.rpc('run_sql', {'sql': table_sql}).execute()
            except Exception as e:
                print(f"Error creating table: {str(e)}")
                continue
            
        # Create views
        for view_sql in views:
            try:
                supabase.postgrest.rpc('run_sql', {'sql': view_sql}).execute()
            except Exception as e:
                print(f"Error creating view: {str(e)}")
                continue
                
        # Apply RLS policies
        for policy_sql in policies:
            try:
                supabase.postgrest.rpc('run_sql', {'sql': policy_sql}).execute()
            except Exception as e:
                print(f"Error creating policy: {str(e)}")
                continue
            
        print("Database initialization completed successfully")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_database() 