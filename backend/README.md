# Benefits Analysis Backend

This is the backend service for the Benefits Analysis system, which uses Google's Gemini AI to provide intelligent benefits analysis and recommendations.

## Setup

1. Create a Python virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
.\venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory with your configuration:
```env
GOOGLE_API_KEY=your_google_api_key_here
HOST=0.0.0.0
PORT=8000
DEBUG=True
ENVIRONMENT=development
```

## Running the Server

Start the FastAPI server:
```bash
uvicorn src.main:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

- `GET /`: Health check endpoint
- `POST /benefits/analyze`: Analyze a benefits scenario
- `POST /benefits/recommend`: Get personalized benefits recommendations

## Testing

Run the tests using pytest:
```bash
pytest
```

## Project Structure

```
backend/
├── src/
│   ├── agents/
│   │   └── eligibility_agent.py
│   └── main.py
├── tests/
│   └── test_eligibility_agent.py
├── config/
├── .env
├── requirements.txt
└── README.md
```

## Development

- All Python code is typed and includes docstrings
- Tests are written using pytest
- Environment variables are managed using python-dotenv
- API documentation is available at http://localhost:8000/docs 