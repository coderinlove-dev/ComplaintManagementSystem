# routes/complaintRoutes.py
from flask import Blueprint, request
from controllers.complaintController import (
    addComplaint,
    getUserUnsolvedComplaints,
    getUserSolvedComplaints
)
from middleware.authMiddleware import authenticate_token

complaint_bp = Blueprint("complaint_bp", __name__)

# --- Add new complaint (with file upload) ---
@complaint_bp.route("", methods=["POST"])
@authenticate_token
def create_complaint():
    file = request.files.get("attachment") 
    data = request.form.to_dict()          
    return addComplaint()

# --- Get unsolved complaints for user ---
@complaint_bp.route("/unsolved", methods=["GET"])
@authenticate_token
def unsolved_complaints():
    return getUserUnsolvedComplaints()

# --- Get solved complaints for user ---
@complaint_bp.route("/solved", methods=["GET"])
@authenticate_token
def solved_complaints():
    return getUserSolvedComplaints()
