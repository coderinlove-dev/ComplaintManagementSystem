# controllers/complaint_controller.py
from flask import request, jsonify, g
from config.db import get_connection

# ========== ADD NEW COMPLAINT ==========
def addComplaint():
    try:
        user_id = g.user["id"]
        subject = request.form.get("subject")
        type_ = request.form.get("type")
        description = request.form.get("description")
        attachment = None

        if "file" in request.files:
            file = request.files["file"]
            attachment = file.filename
            file.save(f"uploads/{attachment}") 

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO complaints (user_id, subject, type, description, attachment, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user_id, subject, type_, description, attachment, "Unsolved")
        )
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Complaint submitted successfully!"}), 201

    except Exception as e:
        return jsonify({"message": "Could not submit complaint", "error": str(e)}), 500


# ========== GET USER'S UNSOLVED COMPLAINTS ==========
def getUserUnsolvedComplaints():
    try:
        user_id = g.user["id"]

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT c.id, u.first_name, u.last_name, c.subject, c.type, c.description, c.status, c.created_at
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            WHERE c.user_id = %s AND c.status = 'Unsolved'
            ORDER BY c.created_at DESC
            """,
            (user_id,)
        )
        rows = cursor.fetchall()

        complaints = [
            {
                "id": row["id"],
                "user": f"{row['first_name']} {row['last_name']}",
                "subject": row["subject"],
                "type": row["type"],
                "issued_date": row["created_at"],
                "description": row["description"],
                "status": row["status"]
            }
            for row in rows
        ]

        cursor.close()
        conn.close()

        return jsonify(complaints), 200

    except Exception as e:
        return jsonify({"message": "Unable to fetch complaints", "error": str(e)}), 500


# ========== GET USER'S SOLVED COMPLAINTS ==========
def getUserSolvedComplaints():
    try:
        user_id = g.user["id"]

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT c.id, u.first_name, u.last_name, c.subject, c.type, c.description, c.status, c.created_at
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            WHERE c.user_id = %s AND c.status = 'Solved'
            ORDER BY c.created_at DESC
            """,
            (user_id,)
        )
        rows = cursor.fetchall()

        complaints = [
            {
                "id": row["id"],
                "user": f"{row['first_name']} {row['last_name']}",
                "subject": row["subject"],
                "type": row["type"],
                "issued_date": row["created_at"],
                "description": row["description"],
                "status": row["status"]
            }
            for row in rows
        ]

        cursor.close()
        conn.close()

        return jsonify(complaints), 200

    except Exception as e:
        return jsonify({"message": "Unable to fetch solved complaints", "error": str(e)}), 500
