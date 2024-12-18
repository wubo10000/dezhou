from flask import Flask, request, jsonify
import pymongo
import os
from datetime import datetime

# 使用腾讯云提供的环境变量
MONGODB_URI = os.environ.get('MONGODB_URI')
client = pymongo.MongoClient(MONGODB_URI)
db = client['poker']
games = db['games']
players = db['players']

def main_handler(event, context):
    path = event['path']
    method = event['httpMethod']
    
    if path == '/games' and method == 'GET':
        result = list(games.find({}, {'_id': 0}).sort('date', -1))
        return {'statusCode': 200, 'body': result}
    
    elif path == '/games' and method == 'POST':
        data = event['body']
        games.insert_one(data)
        return {'statusCode': 200, 'body': {'status': 'success'}}
    
    elif path.startswith('/games/') and method == 'PUT':
        game_id = path.split('/')[-1]
        data = event['body']
        games.update_one({'id': game_id}, {'$set': {'name': data['name']}})
        return {'statusCode': 200, 'body': {'status': 'success'}}
    
    elif path.startswith('/games/') and method == 'DELETE':
        game_id = path.split('/')[-1]
        players.delete_many({'game_id': game_id})
        games.delete_one({'id': game_id})
        return {'statusCode': 200, 'body': {'status': 'success'}}
    
    elif path.endswith('/players') and method == 'GET':
        game_id = path.split('/')[-2]
        result = list(players.find({'game_id': game_id}, {'_id': 0}))
        return {'statusCode': 200, 'body': result}
    
    elif path.endswith('/players') and method == 'POST':
        game_id = path.split('/')[-2]
        data = event['body']
        data['game_id'] = game_id
        players.insert_one(data)
        return {'statusCode': 200, 'body': {'status': 'success'}}
    
    elif '/players/' in path and method == 'PUT':
        game_id = path.split('/')[-3]
        player_name = path.split('/')[-1]
        data = event['body']
        players.update_one(
            {'game_id': game_id, 'name': player_name},
            {'$set': {
                'borrowAmount': data['borrowAmount'],
                'currentAmount': data['currentAmount']
            }}
        )
        return {'statusCode': 200, 'body': {'status': 'success'}}
    
    elif '/players/' in path and method == 'DELETE':
        game_id = path.split('/')[-3]
        player_name = path.split('/')[-1]
        players.delete_one({'game_id': game_id, 'name': player_name})
        return {'statusCode': 200, 'body': {'status': 'success'}}
    
    return {'statusCode': 404, 'body': {'error': 'Not found'}} 