# routes/authRoutes.py
from flask import Blueprint, request, jsonify
from controllers.authController import loginUser, registerUser
import jwt, os
from datetime import datetime, timedelta

auth_bp = Blueprint("auth_bp", __name__)

JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret")

# --- Register endpoint ---
@auth_bp.route("/register", methods=["POST"])
def register():
    return registerUser()

# --- Login endpoint ---
@auth_bp.route("/login", methods=["POST"])
def login():
    return loginUser()

# --- Refresh token endpoint ---
@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    try:
        data = request.get_json()
        refresh_token = data.get("refresh_token")
        if not refresh_token:
            return jsonify({"message": "Refresh token missing"}), 400

        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=["HS256"])
        new_access_token = jwt.encode(
            {"id": payload["id"], "role": payload["role"], "exp": datetime.utcnow() + timedelta(minutes=30)},
            JWT_SECRET,
            algorithm="HS256"
        )

        return jsonify({"access_token": new_access_token}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Refresh token expired, please login again"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid refresh token"}), 401
