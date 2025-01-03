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
- **Eligibility Agent**: Analyzes benefits eligibility and provides recommendations
- **Wellness Agent**: Analyzes health metrics and risk factors
- **Policy Agent**: Researches and applies relevant policy guidelines

### Data Management
- Employee profile management with comprehensive data handling
- Benefits eligibility tracking with error handling
- Wellness metrics monitoring with string-based data consistency
- Policy database integration
- Chat history persistence with Supabase
- Life event tracking and recommendations

### API Endpoints
- `GET /`: Health check endpoint
- `POST /manager/analyze`: Main endpoint for benefits analysis
- `GET /employee/{employee_id}/profile`: Get employee profile
- `GET /employee/{employee_id}/benefits`: Get benefits status
- `GET /employee/{employee_id}/wellness`: Get wellness data
- `GET /employee/{employee_id}/life-events`: Get life event recommendations

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
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# LLM Configuration
MODEL_NAME=gpt-4
TEMPERATURE=0
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
│   │   ├── eligibility_agent.py
│   │   ├── wellness_agent.py
│   │   └── policy_agent.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── supabase.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── data_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── database_service.py
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

### Data Handling
- All metrics data is stored as strings for consistency
- Risk factors and recommendations are stored as lists of strings
- Proper error handling with safe default values
- Comprehensive logging for debugging

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
The application uses Python's built-in logging module with enhanced debugging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Debug Mode
Set `DEBUG=True` in `.env` for detailed error messages and enhanced logging.

### Error Handling
- All database operations have proper error handling
- Safe default values are provided for all data types
- Comprehensive error logging with context
- Type conversion safety checks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License. 