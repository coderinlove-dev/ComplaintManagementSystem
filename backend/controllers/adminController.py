# controllers/adminController.py
from flask import request, jsonify
from config.db import get_connection

# Helper function to run queries
def query_db(query, params=None, commit=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or [])
    if commit:
        conn.commit()
        cursor.close()
        return None
    rows = cursor.fetchall()
    cursor.close()
    return rows


# Dashboard stats for admin cards
def getDashboardStats():
    try:
        usersRes = query_db("SELECT COUNT(*) AS totalUsers FROM users")
        complaintsRes = query_db("SELECT COUNT(*) AS totalComplaints FROM complaints")
        solvedRes = query_db("SELECT COUNT(*) AS solvedComplaints FROM complaints WHERE status = 'Solved'")
        todayRes = query_db("""
            SELECT COUNT(*) AS newComplaints FROM complaints
            WHERE DATE(created_at) = CURDATE()
        """)

        return jsonify({
            "totalUsers": usersRes[0]["totalUsers"],
            "totalComplaints": complaintsRes[0]["totalComplaints"],
            "solvedComplaints": solvedRes[0]["solvedComplaints"],
            "newComplaints": todayRes[0]["newComplaints"]
        })
    except Exception as err:
        return jsonify({"message": "Error fetching dashboard stats", "error": str(err)}), 500

# Recent 10 complaints for table
def getRecentComplaints():
    try:
        rows = query_db("""
            SELECT c.id, u.first_name, u.last_name, c.subject, c.created_at, c.status
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            ORDER BY c.created_at DESC
            LIMIT 10
        """)
        complaints = [{
            "number": idx + 1,
            "user": f"{row['first_name']} {row['last_name']}",
            "subject": row["subject"],
            "date": row["created_at"],
            "status": row["status"],
            "id": row["id"]
        } for idx, row in enumerate(rows)]
        return jsonify(complaints)
    except Exception as err:
        return jsonify({"message": "Error fetching recent complaints", "error": str(err)}), 500

# Get full info for a single complaint
def getComplaintDetails(id):
    try:
        rows = query_db("""
            SELECT c.id, u.first_name, u.last_name, c.subject, c.type, c.description, c.status, c.created_at, c.updated_at
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            WHERE c.id = %s
        """, (id,))
        if not rows:
            return jsonify({"message": "Complaint not found"}), 404
        row = rows[0]
        return jsonify({
            "id": row["id"],
            "user": f"{row['first_name']} {row['last_name']}",
            "subject": row["subject"],
            "type": row["type"],
            "description": row["description"],
            "status": row["status"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        })
    except Exception as err:
        return jsonify({"message": "Error fetching complaint details", "error": str(err)}), 500

def getStatistics():
    try:
        complaintsRes = query_db("SELECT COUNT(*) AS totalComplaints FROM complaints")
        pendingRes = query_db("SELECT COUNT(*) AS pending FROM complaints WHERE status='Pending'")
        inProgressRes = query_db("SELECT COUNT(*) AS inProgress FROM complaints WHERE status='In Progress'")
        solvedRes = query_db("SELECT COUNT(*) AS solved FROM complaints WHERE status='Solved'")
        rejectedRes = query_db("SELECT COUNT(*) AS rejected FROM complaints WHERE status='Rejected'")
        unassignedRes = query_db("SELECT COUNT(*) AS unassigned FROM complaints WHERE assigned_to IS NULL")
        avgResolutionRes = query_db("""
            SELECT AVG(DATEDIFF(updated_at, created_at)) AS avgResolutionDays
            FROM complaints
            WHERE status='Solved'
        """)
        byType = query_db("SELECT type, COUNT(*) AS count FROM complaints GROUP BY type")
        byRole = query_db("""
            SELECT r.name AS role, COUNT(*) AS count
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            JOIN roles r ON u.role_id = r.id
            GROUP BY r.name
        """)
        return jsonify({
            "totalComplaints": complaintsRes[0]["totalComplaints"] if complaintsRes else 0,
            "pending": pendingRes[0]["pending"] if pendingRes else 0,
            "inProgress": inProgressRes[0]["inProgress"] if inProgressRes else 0,
            "solved": solvedRes[0]["solved"] if solvedRes else 0,
            "rejected": rejectedRes[0]["rejected"] if rejectedRes else 0,
            "unassigned": unassignedRes[0]["unassigned"] if unassignedRes else 0,
            "avgResolutionDays": round(avgResolutionRes[0]["avgResolutionDays"], 2) if avgResolutionRes and avgResolutionRes[0]["avgResolutionDays"] else 0,
            "byType": [{"type": r["type"], "count": r["count"]} for r in byType],
            "byRole": [{"role": r["role"], "count": r["count"]} for r in byRole]
        })
    except Exception as err:
        return jsonify({"message": "Error fetching statistics", "error": str(err)}), 500


# Get all users
def getAllUsers():
    try:
        search = request.args.get("search", "")
        role = request.args.get("role", "")
        sql = """
            SELECT 
                u.id,
                CONCAT(COALESCE(u.first_name,''),' ',COALESCE(u.last_name,'')) AS name,
                u.email,
                r.name AS role,
                CASE
                    WHEN LOWER(r.name) = 'staff' THEN COALESCE(u.staff_status,'Pending')
                    ELSE 'N/A'
                END AS status
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE 1=1
        """
        params = []
        if search:
            sql += " AND (u.first_name LIKE %s OR u.last_name LIKE %s OR u.email LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        if role:
            sql += " AND LOWER(r.name) = %s"
            params.append(role.lower())
        sql += " ORDER BY u.id ASC"
        users = query_db(sql, params)
        return jsonify(users)
    except Exception as err:
        return jsonify({"message": "Server error", "error": str(err)}), 500

def getLongestOpenComplaints():
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)
        search = request.args.get("search", "")
        status = request.args.get("status", "")
        role = request.args.get("role", "")

        sql = """
            SELECT c.id, c.subject, c.status, c.created_at, c.assigned_to,
                   u.first_name, u.last_name, r.name AS user_role,
                   a.first_name AS assigned_first, a.last_name AS assigned_last
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            JOIN roles r ON u.role_id = r.id
            LEFT JOIN users a ON c.assigned_to = a.id
            WHERE c.status != 'Solved'
        """
        params = []

        if search:
            sql += " AND (c.subject LIKE %s OR u.first_name LIKE %s OR u.last_name LIKE %s OR c.id LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])
        if status:
            sql += " AND c.status = %s"
            params.append(status)
        if role:
            sql += " AND LOWER(r.name) = %s"
            params.append(role.lower())

        sql += " ORDER BY c.created_at ASC LIMIT 15"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()

        from datetime import datetime
        now = datetime.now()
        data = []
        for i, r in enumerate(rows):
            from datetime import datetime
            created = r["created_at"]
            if isinstance(created, str):
             created = datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
            days_open = round((now - created).total_seconds() / (60 * 60 * 24))

            data.append({
                "idx": i + 1,
                "subject": r["subject"],
                "status": r["status"],
                "user": f"{r['first_name']} {r['last_name']}",
                "role": r["user_role"],
                "daysOpen": days_open,
                "assignedTo": f"{r['assigned_first']} {r['assigned_last']}" if r['assigned_to'] else ""
            })

        return jsonify(data)
    except Exception as err:
        return jsonify({"message": "Error fetching longest open complaints", "error": str(err)}), 500


def getRecentlyClosedComplaints():
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)
        
        sql = """
            SELECT c.subject, u.first_name, u.last_name, r.name AS user_role, c.updated_at,
                   a.first_name AS assigned_first, a.last_name AS assigned_last
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            JOIN roles r ON u.role_id = r.id
            LEFT JOIN users a ON c.assigned_to = a.id
            WHERE c.status = 'Solved'
            ORDER BY c.updated_at DESC
            LIMIT 10
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        
        data = []
        for i, r in enumerate(rows):
            assigned_to = f"{r['assigned_first']} {r['assigned_last']}" if r['assigned_first'] else ""
            data.append({
                "idx": i + 1,
                "subject": r["subject"],
                "user": f"{r['first_name']} {r['last_name']}",
                "role": r["user_role"],
                "closed": r["updated_at"],
                "assignedTo": assigned_to
            })
        return jsonify(data)
    except Exception as err:
        return jsonify({"message": "Error fetching closed complaints", "error": str(err)}), 500


def getStaffAssignmentStats():
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)
        
        sql = """
            SELECT u.id, CONCAT(u.first_name, ' ', u.last_name) AS staff, COUNT(c.id) AS assigned
            FROM users u
            JOIN roles r ON u.role_id = r.id
            LEFT JOIN complaints c ON u.id = c.assigned_to
            WHERE LOWER(r.name) = 'staff'
            GROUP BY u.id
            ORDER BY assigned DESC, staff ASC
            LIMIT 20
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        
        data = [{"idx": i + 1, "staff": r["staff"], "assigned": r["assigned"]} for i, r in enumerate(rows)]
        return jsonify(data)
    except Exception as err:
        return jsonify({"message": "Error fetching staff assignment stats", "error": str(err)}), 500


# Update staff status
def updateStaffStatus(id, data):
    try:
        status = data.get("status") if data else None

        if status not in ["Pending", "Rejected", "Authorized"]:
            return jsonify({"message": "Invalid or missing status"}), 400

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET staff_status = %s WHERE id = %s",
            (status, id)
        )
        conn.commit()
        affected = cursor.rowcount
        cursor.close()

        if affected == 0:
            return jsonify({"message": "Staff not found"}), 404

        return jsonify({"message": "Status updated", "id": id, "status": status})

    except Exception as err:
        return jsonify({
            "message": "Error updating status",
            "error": str(err)
        }), 500


# Delete user
def deleteUser(id):
    try:
        result = query_db("DELETE FROM users WHERE id = %s", (id,))
        if result == []:
            return jsonify({"message": "User not found"}), 404
        return jsonify({"message": "User deleted", "id": id})
    except Exception as err:
        return jsonify({"message": "Error deleting user", "error": str(err)}), 500

# Fetch complaints (with search/filter)
def getComplaints():
    try:
        search = request.args.get("search","")
        role = request.args.get("role","")
        type_ = request.args.get("type","")
        status = request.args.get("status","")
        sql = """
            SELECT c.id, c.subject, c.type, c.status, c.description,
                   c.created_at, c.updated_at, c.assigned_to,
                   u.first_name, u.last_name, r.name AS user_role,
                   au.first_name AS assigned_first, au.last_name AS assigned_last
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            JOIN roles r ON u.role_id = r.id
            LEFT JOIN users au ON c.assigned_to = au.id
            WHERE 1=1
        """
        params = []
        if search:
            sql += " AND (u.first_name LIKE %s OR u.last_name LIKE %s OR c.subject LIKE %s OR c.id LIKE %s)"
            params.extend([f"%{search}%"]*4)
        if role:
            sql += " AND LOWER(r.name) = %s"
            params.append(role.lower())
        if type_:
            sql += " AND c.type = %s"
            params.append(type_)
        if status:
            sql += " AND c.status = %s"
            params.append(status)
        sql += " ORDER BY c.created_at DESC"
        rows = query_db(sql, params)
        complaints = [{
            "id": r["id"],
            "user": f"{r['first_name']} {r['last_name']}",
            "role": r["user_role"],
            "type": r["type"],
            "subject": r["subject"],
            "status": r["status"],
            "submitted": r["created_at"],
            "updated": r["updated_at"],
            "assignedTo": f"{r['assigned_first']} {r['assigned_last']}" if r['assigned_to'] else ""
        } for r in rows]
        return jsonify(complaints)
    except Exception as err:
        return jsonify({"message": "Error fetching complaints", "error": str(err)}), 500

# Get complaint by ID
def getComplaintById(id):
    try:
        rows = query_db("""
            SELECT c.*, u.first_name, u.last_name, r.name AS user_role,
                   au.first_name AS assigned_first, au.last_name AS assigned_last
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            JOIN roles r ON u.role_id = r.id
            LEFT JOIN users au ON c.assigned_to = au.id
            WHERE c.id = %s
        """, (id,))
        if not rows:
            return jsonify({"message": "Complaint not found"}), 404
        c = rows[0]
        comments = query_db("""
            SELECT ac.id, ac.comment, ac.created_at, a.first_name, a.last_name
            FROM admin_comments ac
            JOIN users a ON ac.admin_id = a.id
            WHERE ac.complaint_id = %s
            ORDER BY ac.created_at ASC
        """, (id,))
        return jsonify({
            "id": c["id"],
            "user": f"{c['first_name']} {c['last_name']}",
            "role": c["user_role"],
            "subject": c["subject"],
            "description": c["description"],
            "type": c["type"],
            "status": c["status"],
            "submitted": c["created_at"],
            "updated": c["updated_at"],
            "assignedTo": f"{c['assigned_first']} {c['assigned_last']}" if c['assigned_to'] else "",
            "comments": [{"id": co["id"], "user": f"{co['first_name']} {co['last_name']}", "date": co["created_at"], "msg": co["comment"]} for co in comments]
        })
    except Exception as err:
        return jsonify({"message": "Error fetching complaint", "error": str(err)}), 500

# Update complaint status
def updateComplaintStatus(id, data):
    try:
        status = data.get("status") if data else None
        if status not in ["Pending", "Solved", "Unsolved"]:
            return jsonify({"message": "Invalid or missing status"}), 400

        result = query_db(
            "UPDATE complaints SET status=%s, updated_at=NOW() WHERE id=%s",
            (status, id),
            commit=True  
        )

        if result == 0:
            return jsonify({"message": "Complaint not found"}), 404

        return jsonify({"message": "Status updated", "id": id, "status": status})
    except Exception as err:
        return jsonify({"message": "Error updating status", "error": str(err)}), 500



# Assign complaint to staff
def assignComplaint(id, data):
    try:
        staff_id = data.get("staff_id") if data else None
        if not staff_id:
            return jsonify({"message": "Missing staff_id"}), 400

        result = query_db(
            "UPDATE complaints SET assigned_to=%s, updated_at=NOW() WHERE id=%s",
            (staff_id, id),
            commit=True
        )

        if result == 0:
            return jsonify({"message": "Complaint not found"}), 404

        return jsonify({"message": "Assigned", "id": id, "staff_id": staff_id})
    except Exception as err:
        return jsonify({"message": "Error assigning complaint", "error": str(err)}), 500


# Add admin comment
def addAdminComment(id):
    try:
        comment = request.json.get("comment")
        adminId = getattr(request, "user", {}).get("id")
        if not comment or not comment.strip():
            return jsonify({"message": "Empty comment"}), 400
        if not adminId:
            return jsonify({"message": "Unauthorized: Admin ID missing"}), 401
        query_db("INSERT INTO admin_comments (complaint_id, admin_id, comment, created_at) VALUES (%s,%s,%s,NOW())",
                 (id, adminId, comment))
        return jsonify({"message": "Comment added"})
    except Exception as err:
        return jsonify({"message": "Error adding comment", "error": str(err)}), 500

# Delete complaint
def deleteComplaint(id):
    try:
        result = query_db(
            "DELETE FROM complaints WHERE id=%s",
            (id,),
            commit=True  
        )

        if result == 0: 
            return jsonify({"message": "Complaint not found"}), 404

        return jsonify({"message": "Complaint deleted", "id": id}), 200
    except Exception as err:
        return jsonify({"message": "Error deleting complaint", "error": str(err)}), 500


# Get authorized staff list
def getAuthorizedStaff():
    try:
        rows = query_db("""
            SELECT u.id, CONCAT(u.first_name,' ',u.last_name) AS name
            FROM users u
            JOIN roles r ON u.role_id=r.id
            WHERE LOWER(r.name)='staff' AND u.staff_status='Authorized'
            ORDER BY u.first_name
        """)
        return jsonify(rows)
    except Exception as err:
        return jsonify({"message": "Error fetching staff list", "error": str(err)}), 500
