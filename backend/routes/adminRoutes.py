# routes/adminRoutes.py
from flask import Blueprint, request, jsonify
from middleware.authMiddleware import authenticate_token
from controllers.adminController import (
    getDashboardStats,
    getRecentComplaints,
    getComplaints,
    getComplaintById,
    updateComplaintStatus,
    assignComplaint,
    addAdminComment,
    deleteComplaint,
    getAllUsers,
    updateStaffStatus,
    deleteUser,
    getAuthorizedStaff,
    getStatistics,
    getLongestOpenComplaints,
    getRecentlyClosedComplaints,
    getStaffAssignmentStats
)

admin_bp = Blueprint("admin_bp", __name__)

# --- Dashboard stats for cards ---
@admin_bp.route("/dashboard-stats", methods=["GET"])
@authenticate_token
def dashboard_stats():
    return getDashboardStats()

# --- Recent complaints for table ---
@admin_bp.route("/recent-complaints", methods=["GET"])
@authenticate_token
def recent_complaints():
    return getRecentComplaints()

# --- Complaints ---
@admin_bp.route("/complaints", methods=["GET"])
@authenticate_token
def complaints():
    return getComplaints()

@admin_bp.route("/complaints/<int:id>", methods=["GET"])
@authenticate_token
def complaint_by_id(id):
    return getComplaintById(id)

@admin_bp.route("/complaints/<int:id>/status", methods=["PATCH"])
@authenticate_token
def complaint_status(id):
    data = request.get_json()
    return updateComplaintStatus(id, data)

@admin_bp.route("/complaints/<int:id>/assign", methods=["PATCH"])
@authenticate_token
def complaint_assign(id):
    data = request.get_json()
    return assignComplaint(id, data)

@admin_bp.route("/complaints/<int:id>/comment", methods=["POST"])
@authenticate_token
def complaint_comment(id):
    data = request.get_json()
    return addAdminComment(id, data)

@admin_bp.route("/complaints/<int:id>", methods=["DELETE"])
@authenticate_token
def complaint_delete(id):
    return deleteComplaint(id)

# --- Users ---
@admin_bp.route("/users", methods=["GET"])
@authenticate_token
def users():
    return getAllUsers()

@admin_bp.route("/users/<int:id>/status", methods=["PATCH"])
@authenticate_token
def user_status(id):
    data = request.get_json()
    return updateStaffStatus(id, data)

@admin_bp.route("/users/<int:id>", methods=["DELETE"])
@authenticate_token
def user_delete(id):
    return deleteUser(id)

# --- Staff for assignment dropdown ---
@admin_bp.route("/authorized-staff", methods=["GET"])
@authenticate_token
def authorized_staff():
    return getAuthorizedStaff()

# --- Statistics ---
@admin_bp.route("/statistics", methods=["GET"])
@authenticate_token
def statistics():
    return getStatistics()

@admin_bp.route("/statistics/longest-open", methods=["GET"])
@authenticate_token
def longest_open():
    return getLongestOpenComplaints()

@admin_bp.route("/statistics/recently-closed", methods=["GET"])
@authenticate_token
def recently_closed():
    return getRecentlyClosedComplaints()

@admin_bp.route("/statistics/staff-assignment", methods=["GET"])
@authenticate_token
def staff_assignment():
    return getStaffAssignmentStats()
