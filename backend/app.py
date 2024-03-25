from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import pymongo
import bcrypt
from pymongo import MongoClient
import secrets
import hashlib
import os
import datetime
import uuid

app = Flask(__name__, static_folder='static')

CORS(app)


@app.after_request
def apply_caching(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


# serve static files (CSS, JS, images)
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


mongo_client = MongoClient('mongo')
db = mongo_client["love-sosa"]
user_collection = db['users']
post_collection = db['posts']


# backend needs to check that passwords are the same do not trust the frontend


@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    # check passwords are good and match

    username = data.get('username')
    password = data.get('password')
    confirm_pass = data.get('confirmPassword')


    # check if username is taken
    check_username = user_collection.find_one(
        {'username': username}
    )

    if check_username:
        return jsonify({'error': 'Username taken'}), 400

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


@app.route('/api/logout', methods=['POST'])
def logout():
    auth_token = request.cookies.get('authToken')

    if auth_token is None:
        return jsonify({'error': 'No auth token provided.'}), 400

    # hash the auth token in the cookie
    hashfunc = hashlib.sha256()
    hashfunc.update(auth_token.encode())
    hashed_auth = hashfunc.hexdigest()

    found_token = user_collection.find_one(
        {'token': hashed_auth})

    if found_token:
        user_collection.update_one(
            {"token": hashed_auth},
            {"$set": {"token": ""}}
        )
        response = jsonify({'message': 'User logged out successfully'})
        # Clear the authToken cookie
        response.set_cookie(
            'authToken',
            '',
            expires=0,
            secure=True,
            httponly=True,
        )
        return response, 200
    else:
        return jsonify({'error': 'Invalid or expired token'}), 401


# validate user on page load
@app.route('/api/validate_token', methods=['GET'])
def validate_token():
    auth_token = request.cookies.get('authToken')

    if auth_token is None:
        return jsonify({'error': 'No auth token provided.'}), 400

    found_user = getUserFromToken(auth_token, user_collection)

    if found_user:
        return jsonify({'username': found_user['username']}), 200
    else:
        return jsonify({'error': 'Invalid or expired token'}), 401


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
            response = jsonify({'message': 'User logged in successfully'})
            response.set_cookie('authToken', user_token, httponly=True,
                                secure=True, max_age=3600)

            return response, 201
        else:
            return jsonify({'error': 'Authentication failed'}), 409
    else:
        return jsonify({'error': 'User not found'}), 409

@app.route('/api/posts', methods=['POST'])
def create_post():
    auth_token = request.cookies.get('authToken')
    if not auth_token:
        return jsonify({'error': 'No auth token provided.'}), 400

    user = getUserFromToken(auth_token, user_collection)

    if not user:
        return jsonify({'error': 'Invalid or expired token'}), 401

    data = request.get_json()
    content = data.get('content')   

    if not content:
        return jsonify({'error': 'Content is required'}), 400

    post = {
        'author': user['username'],
        'content': content,
        'created_at': datetime.datetime.now(),
        "like_count": 0,
        "user_liked": [],
        "post_id": str(uuid.uuid4()),
        "comments": []      # list of dict = {"user": user["username"], "comment": comment}
    }
    post_collection.insert_one(post)

    return jsonify({'message': 'Post created successfully'}), 201


@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = list(post_collection.find({}, {'_id': 0}))
    return jsonify(posts), 200


@app.route('/api/posts/<post_id>/like', methods=['POST'])
def like_post(post_id):
    auth_token = request.cookies.get('authToken')
    if not auth_token:
        return jsonify({'error': 'No auth token provided.'}), 400

    user = getUserFromToken(auth_token, user_collection)
    if not user:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    username = user["username"]

    post = post_collection.find_one({"post_id": str(post_id)})
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    #author cant like their own post
    if post["author"] == username:
        return jsonify({'error': 'Authors cannot like their own posts'}), 403

    # user cant like the post twice
    if username in post.get("user_liked", []):
        return jsonify({'error': 'You have already liked this post'}), 409
    
    # increment the post like_count
    post_collection.update_one(
        {"post_id": post_id},
        {"$addToSet": {"user_liked": username}, "$inc": {"like_count": 1}}
    )

    return jsonify({'message': 'Post liked successfully'}), 200



@app.route('/api/posts/<post_id>/comment', methods=['POST'])
def comment_post(post_id):
    auth_token = request.cookies.get('authToken')
    if not auth_token:
        return jsonify({'error': 'No auth token provided.'}), 400

    user = getUserFromToken(auth_token, user_collection)
    if not user:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    username = user["username"]

    post = post_collection.find_one({"post_id": str(post_id)})
    if not post:
        return jsonify({'error': 'Post not found'}), 404
        
    data = request.get_json()
    comment = data.get("comment")
    if not comment:
        return jsonify({'error': "comment can't be empty"}), 400
    
    # add the comment to the doc
    post_collection.update_one(
        {"post_id": post_id},
        {"$push": {"comments": {"user": user["username"], "comment": comment}}}
    )

    return jsonify({'message': 'Comment successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  




#returns the user document 
def getUserFromToken(auth_token, database):
    if auth_token is not None:    
        hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
        found_user = database.find_one({"token": hashed_token})
        return found_user
    return None
