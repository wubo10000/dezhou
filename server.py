from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
from waitress import serve  # 生产环境服务器

app = Flask(__name__)
CORS(app)

# 数据库路径
DB_PATH = '/root/poker.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 创建游戏表
    c.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    
    # 创建玩家表
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            name TEXT NOT NULL,
            borrow_amount INTEGER NOT NULL,
            current_amount INTEGER NOT NULL,
            FOREIGN KEY (game_id) REFERENCES games (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db():
    return sqlite3.connect(DB_PATH)

@app.route('/games', methods=['GET'])
def get_games():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM games ORDER BY date DESC')
    games = []
    for row in c.fetchall():
        game = {
            'id': row[0],
            'name': row[1],
            'date': row[2],
            'players': []
        }
        # 获取该游戏的所有玩家
        c.execute('SELECT * FROM players WHERE game_id = ?', (game['id'],))
        for player_row in c.fetchall():
            game['players'].append({
                'name': player_row[2],
                'borrowAmount': player_row[3],
                'currentAmount': player_row[4]
            })
        games.append(game)
    conn.close()
    return jsonify(games)

@app.route('/games', methods=['POST'])
def create_game():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO games (id, name, date) VALUES (?, ?, ?)',
              (data['id'], data['name'], data['date']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/games/<game_id>', methods=['PUT'])
def update_game(game_id):
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE games SET name = ? WHERE id = ?',
              (data['name'], game_id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/games/<game_id>', methods=['DELETE'])
def delete_game(game_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM players WHERE game_id = ?', (game_id,))
    c.execute('DELETE FROM games WHERE id = ?', (game_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/games/<game_id>/players', methods=['GET'])
def get_players(game_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM players WHERE game_id = ?', (game_id,))
    players = []
    for row in c.fetchall():
        players.append({
            'name': row[2],
            'borrowAmount': row[3],
            'currentAmount': row[4]
        })
    conn.close()
    return jsonify(players)

@app.route('/games/<game_id>/players', methods=['POST'])
def add_player(game_id):
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO players (game_id, name, borrow_amount, current_amount) VALUES (?, ?, ?, ?)',
              (game_id, data['name'], data['borrowAmount'], data['currentAmount']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/games/<game_id>/players/<player_name>', methods=['PUT'])
def update_player(game_id, player_name):
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE players SET borrow_amount = ?, current_amount = ? WHERE game_id = ? AND name = ?',
              (data['borrowAmount'], data['currentAmount'], game_id, player_name))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/games/<game_id>/players/<player_name>', methods=['DELETE'])
def delete_player(game_id, player_name):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM players WHERE game_id = ? AND name = ?',
              (game_id, player_name))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

# 必须添加这个路由作��健康检查
@app.route('/')
def home():
    return 'Poker Score API is running!'

# 初始化数据库
init_db()

if __name__ == '__main__':
    init_db()
    # 使用 waitress 替代 Flask 开发服务器
    serve(app, host='0.0.0.0', port=5000)