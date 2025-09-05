# middleware/authmiddleware.py
import os
import jwt
from functools import wraps
from flask import request, jsonify, g

JWT_SECRET = os.getenv("JWT_SECRET", "your_default_secret")

def authenticate_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        token = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Unauthorized"}), 401

        try:
            user = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=["HS256"],
                leeway=300  
            )
            g.user = user
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 403

        return f(*args, **kwargs)
    return decorated_function
