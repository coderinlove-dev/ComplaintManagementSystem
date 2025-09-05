from flask import Blueprint, request
from controllers.staffController import (
    getProfile,
    getComplaintStats,
    allComplaints,
    updateComplaintStatus,
    getAllSolvedComplaints
)
from middleware.authMiddleware import authenticate_token

staff_bp = Blueprint("staff_bp", __name__)

# --- Staff profile (for sidebar/header) ---
@staff_bp.route("/profile", methods=["GET"])
@authenticate_token
def profile():
    return getProfile()

# --- Stats (numbers, for dashboard + chart) ---
@staff_bp.route("/complaints/stats", methods=["GET"])
@authenticate_token
def complaint_stats():
    return getComplaintStats()

# --- List all complaints (with search/filter query params) ---
@staff_bp.route("/complaints", methods=["GET"])
@authenticate_token
def complaints():
    return allComplaints()

# --- Update complaint status ---
@staff_bp.route("/complaints/<int:id>/status", methods=["POST"])
@authenticate_token
def complaint_status(id):
    data = request.get_json()
    return updateComplaintStatus(id, data)

# --- All solved complaints for table ---
@staff_bp.route("/complaints/solved", methods=["GET"])
@authenticate_token
def solved_complaints():
    return getAllSolvedComplaints()
