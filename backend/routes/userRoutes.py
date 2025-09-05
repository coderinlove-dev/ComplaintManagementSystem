# routes/userRoutes.py
from flask import Blueprint
from controllers.userController import get_user_profile
from middleware.authMiddleware import authenticate_token

user_bp = Blueprint("user_bp", __name__)

# --- Get logged-in user profile ---
@user_bp.route("/me", methods=["GET"])
@authenticate_token
def me():
    return get_user_profile()
