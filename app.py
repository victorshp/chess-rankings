from flask import Flask
import requests
import csv
from datetime import datetime, timedelta
from typing import Dict, Optional, List

app = Flask(__name__)

LICHESS_BASE_URI = "https://lichess.org/api"

def fetch_lichess_data(endpoint: str) -> dict:
    url = f"{LICHESS_BASE_URI}/{endpoint}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_top_players(count: int = 50) -> List[str]:
    data = fetch_lichess_data(f"player/top/{count}/classical")
    return [player['username'] for player in data['users']]

def get_rating_history(username: str) -> Optional[Dict[str, int]]:
    data = fetch_lichess_data(f"user/{username}/rating-history")
    classical_data = next((hist for hist in data if hist['name'] == 'Classical'), None)
    
    if not classical_data:
        return None

    today = datetime.now().date()
    history = {}
    for point in classical_data['points']:
        date = datetime(year=point[0], month=point[1] + 1, day=point[2]).date()
        if (today - date).days <= 30:
            history[date.strftime('%Y-%m-%d')] = point[3]

    for i in range(30):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        if date not in history:
            prev_date = (today - timedelta(days=i+1)).strftime('%Y-%m-%d')
            history[date] = history.get(prev_date, history[list(history.keys())[0]])

    return history

def format_rating_history(history: Dict[str, int]) -> Dict[str, int]:
    today = datetime.now().date()
    formatted_history = {}
    for i in range(29, -1, -1):
        date = today - timedelta(days=i)
        date_str = f"today-{i}" if i > 0 else "today"
        formatted_history[date_str] = history.get(date.strftime('%Y-%m-%d'), history[list(history.keys())[-1]])
    return formatted_history

def generate_rating_csv_for_top_50_classical_players() -> None:
    top_50_players = get_top_players(50)
    today = datetime.now().date()
    date_headers = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)]
    headers = ['username'] + date_headers
    
    print("Starting to generate CSV...")
    with open('top_50_classical_players_ratings.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        for player in top_50_players:
            history = get_rating_history(player)
            if history:
                row = [player]
                for date in date_headers:
                    row.append(history.get(date, ''))
                writer.writerow(row)
            else:
                print(f"No rating history found for {player}")
    
    print("CSV file 'top_50_classical_players_ratings.csv' has been generated.")

@app.route('/')
def index():
    return "Welcome to the Chess Rankings App"

@app.route('/top-50')
def print_top_50_classical_players():
    top_50_players = get_top_players(50)
    print(f"{top_50_players}")
    return top_50_players

@app.route('/top-player-rating-history')
def top_player_rating_history():
    top_player = get_top_players(1)[0]
    history = get_rating_history(top_player)
    
    if not history:
        return {"error": f"No rating history found for {top_player}"}, 404
    
    formatted_history = format_rating_history(history)
    print(f"{top_player}, {formatted_history}")
    return [f"{top_player}, {formatted_history}"]

@app.route('/generate-csv')
def generate_csv():
    generate_rating_csv_for_top_50_classical_players()
    return "CSV file has been generated. Check the server's root directory for 'top_50_classical_players_ratings.csv'."

if __name__ == '__main__':
    app.run(debug=True)
