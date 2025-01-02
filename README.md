# HSA/FSA/COBRA Administration System

An AI-powered benefits administration system using CrewAI agents for intelligent analysis and recommendations. The system provides real-time, personalized guidance on benefits-related queries through a sophisticated multi-agent architecture.

## Features

### Interactive Chat Interface
- Real-time conversational interface for benefits inquiries
- Personalized responses based on employee profile and context
- Visual agent activity tracking through "CrewAI Agents Activity" popup
- Detailed explanation of agent thought processes and decision-making

### Agent System Architecture

#### 1. Manager Agent (Supervisor)
- Orchestrates the entire conversation flow
- Coordinates specialized sub-agents
- Manages context and employee profiles
- Provides final, synthesized responses

#### 2. Specialized Agents
- **Query Analyzer**: Classifies and interprets user questions
- **Context Agent**: Manages employee profiles and historical data
- **Policy Agent**: Researches and applies relevant policy guidelines
- **Wellness Agent**: Analyzes health metrics and risk factors
- **Benefits Expert**: Generates personalized recommendations
- **Response Analyzer**: Ensures quality and completeness of responses

### Data Integration
- Real-time employee profile access
- Benefits eligibility tracking
- Wellness metrics monitoring
- Policy database integration
- Chat history persistence

### Analytics and Monitoring
- Agent activity visualization
- Decision-making process transparency
- Real-time debug information
- Response quality tracking

## Technical Stack

### Frontend
- Next.js with TypeScript
- Tailwind CSS for styling
- React state management
- WebSocket for real-time updates

### Backend
- FastAPI for API endpoints
- CrewAI for agent orchestration
- OpenAI GPT for natural language processing
- Supabase for data persistence

## Setup Instructions

### Prerequisites
- Node.js 18+ for frontend
- Python 3.10+ for backend
- OpenAI API key
- Supabase account and credentials

### Frontend Setup
1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local`:
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_key
```

4. Start the development server:
```bash
npm run dev
```

### Backend Setup
1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Unix/MacOS
.\venv\Scripts\activate   # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env`:
```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

5. Start the backend server:
```bash
uvicorn src.main:app --reload
```

## Usage

1. Access the application at `http://localhost:3000`
2. Log in with employee credentials
3. Start asking benefits-related questions
4. Click the "Users" icon to view agent activity

## Features in Development

- ✅ Basic chat interface
- ✅ Agent activity visualization
- ✅ Employee profile integration
- ✅ Policy-based responses
- ✅ Wellness metrics integration
- 🔄 Multi-agent collaboration
- 🔄 Advanced analytics dashboard
- 🔄 Document upload/processing
- 🔄 Mobile responsive design

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
