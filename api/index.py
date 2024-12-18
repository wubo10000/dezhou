from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 使用文件系统存储数据
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
GAMES_FILE = os.path.join(DATA_DIR, 'games.json')
PLAYERS_FILE = os.path.join(DATA_DIR, 'players.json')

def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(GAMES_FILE):
        with open(GAMES_FILE, 'w') as f:
            json.dump([], f)
    if not os.path.exists(PLAYERS_FILE):
        with open(PLAYERS_FILE, 'w') as f:
            json.dump([], f)

def read_games():
    with open(GAMES_FILE, 'r') as f:
        return json.load(f)

def write_games(games):
    with open(GAMES_FILE, 'w') as f:
        json.dump(games, f)

def read_players():
    with open(PLAYERS_FILE, 'r') as f:
        return json.load(f)

def write_players(players):
    with open(PLAYERS_FILE, 'w') as f:
        json.dump(players, f)

@app.route('/api/games', methods=['GET'])
def get_games():
    games = read_games()
    return jsonify(games)

@app.route('/api/games', methods=['POST'])
def create_game():
    data = request.json
    games = read_games()
    games.append(data)
    write_games(games)
    return jsonify({'status': 'success'})

@app.route('/api/games/<game_id>', methods=['PUT'])
def update_game(game_id):
    data = request.json
    games = read_games()
    for game in games:
        if game['id'] == game_id:
            game['name'] = data['name']
            break
    write_games(games)
    return jsonify({'status': 'success'})

@app.route('/api/games/<game_id>', methods=['DELETE'])
def delete_game(game_id):
    games = read_games()
    players = read_players()
    games = [g for g in games if g['id'] != game_id]
    players = [p for p in players if p['game_id'] != game_id]
    write_games(games)
    write_players(players)
    return jsonify({'status': 'success'})

@app.route('/api/games/<game_id>/players', methods=['GET'])
def get_players(game_id):
    players = read_players()
    game_players = [p for p in players if p['game_id'] == game_id]
    return jsonify(game_players)

@app.route('/api/games/<game_id>/players', methods=['POST'])
def add_player(game_id):
    data = request.json
    players = read_players()
    data['game_id'] = game_id
    players.append(data)
    write_players(players)
    return jsonify({'status': 'success'})

@app.route('/api/games/<game_id>/players/<player_name>', methods=['PUT'])
def update_player(game_id, player_name):
    data = request.json
    players = read_players()
    for player in players:
        if player['game_id'] == game_id and player['name'] == player_name:
            player['borrowAmount'] = data['borrowAmount']
            player['currentAmount'] = data['currentAmount']
            break
    write_players(players)
    return jsonify({'status': 'success'})

@app.route('/api/games/<game_id>/players/<player_name>', methods=['DELETE'])
def delete_player(game_id, player_name):
    players = read_players()
    players = [p for p in players if not (p['game_id'] == game_id and p['name'] == player_name)]
    write_players(players)
    return jsonify({'status': 'success'})

ensure_data_files() 