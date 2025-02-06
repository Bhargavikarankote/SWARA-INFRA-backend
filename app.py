# from flask import Flask, request, jsonify, send_file
# from flask_pymongo import PyMongo
# from gridfs import GridFS
# from bson import ObjectId
# from flask_cors import CORS
# import io
# import os

# app = Flask(__name__)

# # Enable CORS so React can make requests to Flask API
# CORS(app)

# # Configure MongoDB
# app.config["MONGO_URI"] = "mongodb://localhost:27017/imageDB"
# mongo = PyMongo(app)
# fs = GridFS(mongo.db)
# metadata_collection = mongo.db.metadata  # Metadata collection for images

# # Store image in MongoDB (POST)
# @app.route("/upload_image", methods=["POST"])
# def upload_image():
#     if "image" not in request.files or not all(k in request.form for k in ["status", "location", "square_feet"]):
#         return jsonify({"error": "Missing image or metadata fields"}), 400

#     image = request.files["image"]
#     status = request.form["status"]  # "Completed" or "Ongoing"
#     location = request.form["location"]
#     square_feet = request.form["square_feet"]

#     image_id = fs.put(image, filename=image.filename)  # Store image in GridFS

#     # Store metadata in MongoDB
#     metadata_collection.insert_one({
#         "image_id": image_id,
#         "status": status,
#         "location": location,
#         "square_feet": square_feet
#     })

#     return jsonify({"message": "Image uploaded successfully", "id": str(image_id)}), 201

# # Fetch images by status (GET)
# @app.route("/get_images/<status>", methods=["GET"])
# def get_images(status):
#     images = metadata_collection.find({"status": status})

#     image_list = []
#     for image in images:
#         img_data = fs.get(image["image_id"])  # Retrieve image data from GridFS
#         img_url = f"/get_image/{image['image_id']}"  # URL to fetch the image
        
#         image_list.append({
#             "id": str(image["image_id"]),
#             "url": img_url,
#             "location": image["location"],
#             "square_feet": image["square_feet"],
#             "status": image["status"]
#         })

#     if not image_list:
#         return jsonify({"message": "No images found"}), 404

#     return jsonify(image_list), 200

# # Fetch individual image by ID (GET)
# @app.route("/get_image/<image_id>", methods=["GET"])
# def get_image(image_id):
#     try:
#         image = fs.get(ObjectId(image_id))  # Retrieve the image from GridFS
#         return send_file(io.BytesIO(image.read()), mimetype="image/jpeg")  # Send image as response
#     except:
#         return jsonify({"error": "Image not found"}), 404

# if __name__ == "__main__":
#     app.run(debug=True)

# from flask import Flask, request, jsonify, send_file, url_for
# from flask_pymongo import PyMongo
# from gridfs import GridFS
# from bson import ObjectId
# from flask_cors import CORS
# import io
# import os

# app = Flask(__name__)

# # Enable CORS so React can make requests to Flask API
# CORS(app, resources={r"/*": {"origins": "*"}})

# # Configure MongoDB
# app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/imageDB")
# mongo = PyMongo(app)
# fs = GridFS(mongo.db)
# metadata_collection = mongo.db.metadata  # Metadata collection for images

# # Store image in MongoDB (POST)
# @app.route("/upload_image", methods=["POST"])
# def upload_image():
#     if "image" not in request.files or not all(k in request.form for k in ["status", "location", "square_feet"]):
#         return jsonify({"error": "Missing image or metadata fields"}), 400

#     image = request.files["image"]
#     status = request.form["status"]
#     location = request.form["location"]
#     square_feet = request.form["square_feet"]

#     image_id = fs.put(image, filename=image.filename)  # Store image in GridFS

#     # Store metadata in MongoDB
#     metadata_collection.insert_one({
#         "image_id": image_id,
#         "status": status,
#         "location": location,
#         "square_feet": square_feet
#     })

#     return jsonify({"message": "Image uploaded successfully", "id": str(image_id)}), 201

# # Fetch images by status (GET)
# @app.route("/get_images/<status>", methods=["GET"])
# def get_images(status):
#     images = metadata_collection.find({"status": status})

#     image_list = []
#     for image in images:
#         img_url = url_for("get_image", image_id=image["image_id"], _external=True)  # Generate full image URL

#         image_list.append({
#             "id": str(image["image_id"]),
#             "url": img_url,
#             "location": image["location"],
#             "square_feet": image["square_feet"],
#             "status": image["status"]
#         })

#     if not image_list:
#         return jsonify({"message": "No images found"}), 404

#     return jsonify(image_list), 200

# # Fetch individual image by ID (GET)
# @app.route("/get_image/<image_id>", methods=["GET"])
# def get_image(image_id):
#     try:
#         image = fs.get(ObjectId(image_id))  # Retrieve image from GridFS
#         return send_file(io.BytesIO(image.read()), mimetype=image.content_type)  # Return the image with correct mime type
#     except Exception as e:
#         return jsonify({"error": "Image not found"}), 404

# if __name__ == "__main__":
#     app.run(debug=True, port=6001)


from flask import Flask, request, jsonify, send_file
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from gridfs import GridFS
from bson import ObjectId
import io
import re

app = Flask(__name__)
CORS(app)

# Configure MongoDB for image storage and user authentication
app.config["MONGO_URI"] = "mongodb://localhost:27017/imageDB"
mongo = PyMongo(app)
fs = GridFS(mongo.db)
metadata_collection = mongo.db.metadata
users_collection = mongo.db.users  # Collection for user data

bcrypt = Bcrypt(app)

# Register route using form-data
@app.route('/register', methods=['POST'])
def register():
    name = request.form.get("name")
    mobile_number = request.form.get("mobile_number")
    email = request.form.get("email")
    password = request.form.get("password")

    if not all([name, mobile_number, email, password]):
        return jsonify({'message': 'All fields are required'}), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'message': 'Invalid email format'}), 400
    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters long'}), 400

    user_by_email = users_collection.find_one({"email": email})
    user_by_mobile = users_collection.find_one({"mobile_number": mobile_number})
    if user_by_email or user_by_mobile:
        return jsonify({'message': 'Email or Mobile number already exists'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = {
        "name": name,
        "mobile_number": mobile_number,
        "email": email,
        "password": hashed_password
    }
    users_collection.insert_one(new_user)

    return jsonify({'message': 'User registered successfully'}), 201

# Login route using form-data
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    if not all([email, password]):
        return jsonify({'message': 'Email and password are required'}), 400

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid password'}), 401

    return jsonify({'message': 'Login successful'}), 200

# Store image in MongoDB (POST) using form-data
@app.route("/upload_image", methods=["POST"])
def upload_image():
    if "image" not in request.files or not all(k in request.form for k in ["status", "location", "square_feet"]):
        return jsonify({"error": "Missing image or metadata fields"}), 400

    image = request.files["image"]
    status = request.form["status"]
    location = request.form["location"]
    square_feet = request.form["square_feet"]

    image_id = fs.put(image, filename=image.filename)
    metadata_collection.insert_one({
        "image_id": image_id,
        "status": status,
        "location": location,
        "square_feet": square_feet
    })

    return jsonify({"message": "Image uploaded successfully", "id": str(image_id)}), 201

# Fetch images by status (GET)
@app.route("/get_images/<status>", methods=["GET"])
def get_images(status):
    images = metadata_collection.find({"status": status})
    image_list = []
    for image in images:
        img_url = f"/get_image/{image['image_id']}"
        image_list.append({
            "id": str(image["image_id"]),
            "url": img_url,
            "location": image["location"],
            "square_feet": image["square_feet"],
            "status": image["status"]
        })

    if not image_list:
        return jsonify({"message": "No images found"}), 404
    return jsonify(image_list), 200

# Fetch individual image by ID (GET)
@app.route("/get_image/<image_id>", methods=["GET"])
def get_image(image_id):
    try:
        image = fs.get(ObjectId(image_id))
        return send_file(io.BytesIO(image.read()), mimetype="image/jpeg")
    except:
        return jsonify({"error": "Image not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5001)
