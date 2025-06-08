# NBA Game Predictor

A machine learning-powered application that predicts NBA game outcomes using historical data and real-time statistics.

## Project Structure

```
nba_predictor_app/
├── frontend/           # StreamLit UI
│   └── app.py
├── backend/           # FastAPI app
│   ├── main.py
│   ├── routes/
│   ├── models/       # Pydantic models
│   └── services/     # Calls to ChatGPT, NBA API
├── mcp_agents/       # Optional: MCP tool + agent definitions
│   ├── tools/
│   └── agents.yaml
├── database/         # Database related files
│   ├── db.py        # SQL connection logic
│   └── models.py    # SQLAlchemy models
├── .env             # Secrets (API keys, DB URL)
├── requirements.txt
└── README.md
```

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:

```
DATABASE_URL=your_database_url
NBA_API_KEY=your_nba_api_key
OPENAI_API_KEY=your_openai_api_key
```

4. Run the application:

Backend:

```bash
cd backend
uvicorn main:app --reload
```

Frontend:

```bash
cd frontend
streamlit run app.py
```

## Features

- Real-time NBA game predictions
- Historical game data analysis
- Team statistics visualization
- Integration with NBA API
- Machine learning model for predictions

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
