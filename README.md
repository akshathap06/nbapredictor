# NBA Player Statistics Analyzer

An interactive web application that allows users to search for NBA players, view their statistics, and ask questions about their performance using AI-powered analysis.

## Features

- Search for NBA players by name
- View detailed player statistics with visual progress bars
- Interactive season selection
- AI-powered analysis of player statistics using ChatGPT
- Real-time data from NBA API

## Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/nbapredictor.git
cd nbapredictor
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   Create a `.env` file in the root directory and add your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

4. Run the application:

```bash
# Start the FastAPI server
cd nba_predictor_app/mcp_agents
python server.py

# In a new terminal, start the Streamlit app
streamlit run nba_predictor_app/app.py
```

## Usage

1. Enter a player's first and last name in the search fields
2. Select a season from the dropdown menu
3. View the player's statistics with visual progress bars
4. Ask questions about the player's performance in the text input field
5. Get AI-powered analysis of the statistics

## Technologies Used

- Python
- Streamlit
- FastAPI
- NBA API
- OpenAI GPT-4
- Pandas

## Contributing

Feel free to submit issues and enhancement requests!
