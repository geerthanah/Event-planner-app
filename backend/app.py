from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv("JWT_SECRET", "devsecret")

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client['event_planner']
users = db.users
events = db.events

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                current_user = users.find_one({'_id': ObjectId(data['id'])})
                if not current_user:
                    return jsonify({'msg': 'User not found'}), 401
            except:
                return jsonify({'msg': 'Invalid token'}), 401
        else:
            return jsonify({'msg': 'Token missing'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    if users.find_one({'username': data['username']}):
        return jsonify({'msg': 'User already exists'}), 400
    hashed_pw = generate_password_hash(data['password'])
    result = users.insert_one({'username': data['username'], 'password': hashed_pw})
    token = jwt.encode({
        'id': str(result.inserted_id), 
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'])
    return jsonify({'token': token})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = users.find_one({'username': data['username']})
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'msg': 'Invalid credentials'}), 400
    token = jwt.encode({
        'id': str(user['_id']), 
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'])
    return jsonify({'token': token})

@app.route('/api/events', methods=['GET'])
@token_required
def get_events(current_user):
    user_events = events.find({'userId': str(current_user['_id'])})
    return jsonify([{
        '_id': str(e['_id']),
        'title': e['title'],
        'description': e['description'],
        'date': e['date']
    } for e in user_events])

@app.route('/api/events', methods=['POST'])
@token_required
def add_event(current_user):
    data = request.json
    new_event = {
        'title': data['title'],
        'description': data.get('description', ''),
        'date': data['date'],
        'userId': str(current_user['_id'])
    }
    result = events.insert_one(new_event)
    return jsonify({'_id': str(result.inserted_id)})

@app.route('/api/events/<id>', methods=['PUT'])
@token_required
def update_event(current_user, id):
    data = request.json
    events.update_one(
        {'_id': ObjectId(id), 'userId': str(current_user['_id'])},
        {"$set": data}
    )
    return jsonify({'msg': 'Updated'})

@app.route('/api/events/<id>', methods=['DELETE'])
@token_required
def delete_event(current_user, id):
    events.delete_one({'_id': ObjectId(id), 'userId': str(current_user['_id'])})
    return jsonify({'msg': 'Deleted'})

if __name__ == '__main__':
    app.run(debug=True)
