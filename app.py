from flask import Flask
import requests

app = Flask(__name__)

LICHESS_BASE_URI="https://lichess.org/api"

@app.route('/')
def index():
    return "Welcome to the Chess Rankings App"

@app.route('/top-50')
def print_top_50_classical_players():
    url = f"{LICHESS_BASE_URI}/player/top/50/classical"
    response = requests.get(url)
    players = response.json()

    top_50_players = [player['username'] for player in players['users']]
    return top_50_players

if __name__ == '__main__':
    app.run(debug=True)

