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
from werkzeug.utils import secure_filename
from http.server import BaseHTTPRequestHandler

app = Flask(__name__)



@app.after_request
def apply_caching(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.route('/api/<path:path>', methods=['OPTIONS'])
def options(path):
    return ('', 204, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    })



mongo_client = MongoClient('mongo')
db = mongo_client["love-sosa"]
user_collection = db['users']
post_collection = db['posts']

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# backend needs to check that passwords are the same do not trust the frontend


@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    confirm_pass = data.get('confirmPassword')

    check_username = user_collection.find_one({'username': username})
    if check_username:
        return jsonify({'error': 'Username taken'}), 400

    if password != confirm_pass:
        return jsonify({'error': 'Passwords do not match'}), 409

    salt = bcrypt.gensalt()
    hashed_pass = bcrypt.hashpw(password.encode(), salt)
    default_image_url = "https://via.placeholder.com/150"  #default profile image

    user_collection.insert_one({
        'username': username,
        'password': hashed_pass,
        'profile_image': default_image_url,
        'token': ''
    })

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

    user = getUserFromToken(auth_token, user_collection)
    if user:
        return jsonify({'username': user['username'], 'profileImage': user['profile_image']}), 200
    else:
        return jsonify({'error': 'Invalid or expired token'}), 401
    

@app.route('/api/editprofile', methods=['POST'])
def edit_profile():
    auth_token = request.cookies.get('authToken')
    user = getUserFromToken(auth_token, user_collection)

    if not user:
        return jsonify({'error': 'Invalid or expired token'}), 401

    file = request.files['profileImage']
    if file and allowed_file(file.filename):  # Ensure it's a valid image file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Update the user's profile image URL in the database
        new_image_url = f"/uploads/{filename}"  # URL path to access the image
        user_collection.update_one({'username': user['username']}, {'$set': {'profile_image': new_image_url}})

        return jsonify({'message': 'Profile image updated successfully'}), 200
    else:
        return jsonify({'error': 'No image provided or invalid file format'}), 400

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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
        'author_profile_image': user['profile_image'], 
        'content': content,
        'created_at': datetime.datetime.now(),
        "like_count": 0,
        "user_liked": [],
        "post_id": str(uuid.uuid4()),
        "comments": [] 
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

    # unlike the post if already liked
    if username in post.get("user_liked", []):
        post_collection.update_one({"post_id": post_id}, {"$pull": {"user_liked": username}, "$inc": {"like_count": -1}})
        return jsonify({'message': 'Post unliked successfully'}), 200
    
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





#returns the user document 
def getUserFromToken(auth_token, database):
    if auth_token is not None:    
        hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
        found_user = database.find_one({"token": hashed_token})
        return found_user
    return None