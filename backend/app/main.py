from flask import Flask, request, jsonify
from flask_cors import CORS
import pymongo
import bcrypt
from pymongo import MongoClient
import secrets
import hashlib

app = Flask(__name__)
CORS(app)  # allow CORS

mongo_client = MongoClient('mongo')
db = mongo_client["cse312"]
user_collection = db['users']

# backend needs to check that passwords are the same do not trust the frontend


@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    # check passwords are good and match

    username = data.get('username')
    password = data.get('password')
    confirm_pass = data.get('confirmPassword')

    if (password != confirm_pass):
        return jsonify({'error': 'Passwords do not match'}), 409

    pass_to_bytes = password.encode()
    salt = bcrypt.gensalt()
    hashed_pass = bcrypt.hashpw(pass_to_bytes, salt)
    # form entry
    entry = {'username': username,
             'password': hashed_pass, 'token': ''}

    user_collection.insert_one(entry)

    return jsonify({'message': 'User created successfully'}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    # check passwords are good and match

    username = data.get('username')
    password = data.get('password')

    found_user = user_collection.find_one(
        {'username': username})

    # if the user exists in the database
    if found_user:
        stored_hash = found_user.get('password')
        pass_to_bytes = password.encode()

        validated = bcrypt.checkpw(pass_to_bytes, stored_hash)

        # salted hash of the password  matches one in database
        if validated:  # generate token, store the hash of it in the db, set the actual token as a cookie
            user_token = secrets.token_urlsafe(32)

            print("user token: " + user_token)
            print("validated")

            hashfunc = hashlib.sha256()
            hashfunc.update(user_token.encode())
            hashed_token = hashfunc.hexdigest()

            user_collection.update_one(
                {"username": username},
                {"$set": {"token": hashed_token}}
            )
            return jsonify({'message': 'User logged in successfully', 'token': user_token}), 201
        else:
            return jsonify({'error': 'Authentication failed'}), 409
    else:
        return jsonify({'error': 'User not found'}), 409


if __name__ == '__main__':
    app.run(debug=True)
