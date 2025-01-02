# Benefits Administration Backend

The backend service for the Benefits Administration system, powered by CrewAI and OpenAI for intelligent benefits analysis and recommendations.

## Developer
- **Name**: Nick Sudh
- **Website**: [mlbrilliance.com](http://www.mlbrilliance.com)
- **GitHub**: [@mlbrilliance](https://github.com/mlbrilliance)
- **Twitter**: [@mlbrilliance](https://x.com/mlbrilliance)
- **BlueSky**: [@mlbrilliance](https://bsky.app/profile/mlbrilliance.com)

## Features

### Multi-Agent System
- **Manager Agent**: Orchestrates the entire conversation flow and coordinates other agents
- **Query Analyzer**: Classifies and interprets user questions
- **Context Agent**: Manages employee profiles and historical data
- **Policy Agent**: Researches and applies relevant policy guidelines
- **Wellness Agent**: Analyzes health metrics and risk factors
- **Benefits Expert**: Generates personalized recommendations
- **Response Analyzer**: Ensures quality and completeness of responses

### Data Management
- Employee profile management
- Benefits eligibility tracking
- Wellness metrics monitoring
- Policy database integration
- Chat history persistence

### API Endpoints
- `GET /`: Health check endpoint
- `POST /manager/analyze`: Main endpoint for benefits analysis
- `POST /benefits/analyze`: Legacy endpoint for basic benefits analysis

## Dependencies

### Core Dependencies
- `fastapi`: Web framework for building APIs
- `crewai`: Multi-agent orchestration framework
- `openai`: OpenAI GPT integration
- `supabase`: Database and authentication
- `python-dotenv`: Environment variable management
- `uvicorn`: ASGI server
- `pydantic`: Data validation

### Development Dependencies
- `pytest`: Testing framework
- `black`: Code formatting
- `ruff`: Linting
- `mypy`: Type checking

## Setup

1. Create a Python virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
.\venv\Scripts\activate

# Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```env
# Required
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Optional
HOST=0.0.0.0
PORT=8000
DEBUG=True
ENVIRONMENT=development
```

## Running the Server

### Development
```bash
uvicorn src.main:app --reload
```

### Production
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

## Project Structure

```
backend/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── manager_agent.py
│   │   └── eligibility_agent.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── data_repository.py
│   ├── services/
│   │   └── __init__.py
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_manager_agent.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Development Guidelines

### Code Style
- All Python code must be typed
- Use docstrings for all functions and classes
- Follow PEP 8 style guide
- Use black for code formatting
- Use ruff for linting
- Use mypy for type checking

### Testing
Run tests using pytest:
```bash
pytest
```

With coverage:
```bash
pytest --cov=src tests/
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Debugging

### Logging
The application uses Python's built-in logging module:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Debug Mode
Set `DEBUG=True` in `.env` for detailed error messages.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License. 