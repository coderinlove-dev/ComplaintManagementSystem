# staffController.py
from flask import request, jsonify, g
from config.db import get_connection


# Get the current staff user's profile (for sidebar/navbar)
def getProfile():
    try:
        staff_id = g.user.get("id") if g.user else None
        if not staff_id:
            return jsonify({"message": "Unauthorized, no staff ID"}), 401

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT first_name, last_name FROM users WHERE id = %s",
            (staff_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            return jsonify({"message": "Staff not found"}), 404

        return jsonify({
            "name": f"{row['first_name']} {row['last_name']}"
        })

    except Exception as err:
        return jsonify({
            "message": "Error fetching staff profile",
            "error": str(err)
        }), 500


# Dashboard statistics and chart data for staff dashboard
def getComplaintStats():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Total complaints
        cursor.execute("SELECT COUNT(*) AS total FROM complaints")
        total = cursor.fetchone()["total"]

        # Unsolved complaints
        cursor.execute("SELECT COUNT(*) AS unsolved FROM complaints WHERE status = 'Unsolved'")
        unsolved = cursor.fetchone()["unsolved"]

        # Solved complaints
        cursor.execute("SELECT COUNT(*) AS solved FROM complaints WHERE status = 'Solved'")
        solved = cursor.fetchone()["solved"]

        # Pending complaints
        cursor.execute("SELECT COUNT(*) AS pending FROM complaints WHERE status = 'Pending'")
        pending = cursor.fetchone()["pending"]

        # Complaints grouped by type
        cursor.execute("""
            SELECT type,
                   SUM(status = 'Unsolved') AS unsolved,
                   SUM(status = 'Pending') AS pending,
                   SUM(status = 'Solved') AS solved,
                   COUNT(*) AS total
            FROM complaints
            GROUP BY type
        """)
        by_type = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "total": total,
            "unsolved": unsolved,
            "pending": pending,
            "solved": solved,
            "byType": by_type
        })

    except Exception as err:
        return jsonify({
            "message": "Error fetching statistics",
            "error": str(err)
        }), 500


# List/search/filter all complaints (for allcomplaints.html)
def allComplaints():
    try:
        staff_id = g.user.get("id") if g.user else None
        if not staff_id:
            return jsonify({"message": "Unauthorized"}), 401

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        search = request.args.get("search", "")
        complaint_type = request.args.get("type", "")

        sql = """
            SELECT c.id, c.subject, c.type, c.description, c.status,
                   c.created_at, c.user_id, u.first_name, u.last_name
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            WHERE 1=1
        """
        params = []

        if search:
            sql += """
                AND (u.first_name LIKE %s OR
                     u.last_name  LIKE %s OR
                     c.subject    LIKE %s OR
                     c.type       LIKE %s)
            """
            search_pattern = f"%{search}%"
            params.extend([search_pattern]*4)

        if complaint_type:
            sql += " AND c.type = %s"
            params.append(complaint_type)

        sql += " ORDER BY c.created_at DESC"

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        complaints = [
            {
                "id": row["id"],
                "user": f"{row['first_name']} {row['last_name']}",
                "subject": row["subject"],
                "type": row["type"],
                "issued": row["created_at"],
                "desc": row["description"],
                "status": row["status"]
            } for row in rows
        ]

        return jsonify(complaints)

    except Exception as err:
        return jsonify({
            "message": "Error fetching complaints",
            "error": str(err)
        }), 500


# Update/change complaint status (Pending, Solved, Unsolved)
def updateComplaintStatus(id, data):
    try:
        staff_id = g.user.get("id") if g.user else None
        if not staff_id:
            return jsonify({"message": "Unauthorized"}), 401

        status = data.get("status") if data else None
        if status not in ["Pending", "Solved", "Unsolved"]:
            return jsonify({"message": "Invalid or missing status"}), 400

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE complaints SET status = %s WHERE id = %s",
            (status, id)
        )
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()

        if affected == 0:
            return jsonify({"message": "Complaint not found"}), 404

        return jsonify({"message": "Status updated", "id": id, "status": status})

    except Exception as err:
        return jsonify({
            "message": "Error updating status",
            "error": str(err)
        }), 500


# All solved complaints (for staffsolvedcomplaint.html)
def getAllSolvedComplaints():
    try:
        staff_id = g.user.get("id") if g.user else None
        if not staff_id:
            return jsonify({"message": "Unauthorized"}), 401

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT c.id, u.first_name, u.last_name,
                   c.subject, c.type, c.description,
                   c.status, c.created_at, c.updated_at
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            WHERE c.status = 'Solved'
            ORDER BY c.updated_at DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        complaints = [
            {
                "id": row["id"],
                "user": f"{row['first_name']} {row['last_name']}",
                "subject": row["subject"],
                "type": row["type"],
                "issuedDate": row["created_at"],
                "solvedDate": row["updated_at"],
                "description": row["description"],
                "status": row["status"]
            } for row in rows
        ]

        return jsonify(complaints)

    except Exception as err:
        return jsonify({
            "message": "Error fetching solved complaints",
            "error": str(err)
        }), 500
