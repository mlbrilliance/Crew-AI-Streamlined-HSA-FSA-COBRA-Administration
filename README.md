# HSA/FSA/COBRA Administration System

An AI-powered benefits administration system using CrewAI agents for intelligent analysis and recommendations.

## Agent Hierarchy and Responsibilities

### 1. Supervisor Agent (Manager)
The orchestrator of the entire agent ecosystem with the following responsibilities:
- Acts as the coordinator between all specialized agents
- Determines which agent(s) to engage based on user queries
- Maintains conversation context and history
- Aggregates and synthesizes responses from multiple agents
- Makes final decisions when agents have conflicting recommendations
- Manages database interactions through a unified interface
- Prioritizes tasks and manages workflow between agents

### 2. Eligibility Agent
Specializes in benefits eligibility analysis with these key functions:
- Analyzes individual eligibility for HSA/FSA/COBRA
- Queries Supabase for:
  - Employee status and history
  - Current benefit enrollments
  - Previous eligibility determinations
- Provides personalized recommendations
- Updates eligibility status in database

### 3. Compliance Agent
Ensures regulatory compliance and proper documentation:
- Monitors regulatory requirements
- Validates benefit setups against IRS/DOL rules
- Queries Supabase for:
  - Compliance history
  - Documentation status
  - Required notifications/deadlines
- Flags potential compliance issues
- Maintains audit trails in database

### 4. QA Agent
Ensures quality and consistency across all recommendations:
- Reviews recommendations from other agents
- Validates data consistency
- Performs fact-checking against:
  - Current regulations
  - Company policies
  - Historical decisions in Supabase
- Identifies potential errors or inconsistencies
- Maintains quality metrics in database

## Implementation Status

- ✅ Eligibility Agent: Implemented and functional
- 🔄 Compliance Agent: Planned for next phase
- 🔄 Supervisor Agent: In planning
- 🔄 QA Agent: In planning

## Database Integration

The system integrates with Supabase for:
- Real-time data synchronization
- Conversation history tracking
- Agent decision logging
- Performance metrics
- Audit trail maintenance
- Caching frequently accessed data

## Frontend Integration

The NextJS frontend provides:
- Interactive chat interface
- Real-time status updates
- Visual representation of agent activities
- Detailed explanation of decisions
- User feedback collection
- Progress tracking for complex queries
