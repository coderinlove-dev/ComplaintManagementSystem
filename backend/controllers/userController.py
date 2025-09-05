# controllers/usercontroller.py
from flask import jsonify, g
from config.db import get_connection

def get_user_profile():
    try:
        user_id = g.user["id"]  
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """
            SELECT name AS username, email, first_name, last_name, college, roll_number, branch 
            FROM users 
            WHERE id = %s
            """,
            (user_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        
        if not row:
            return jsonify({"message": "No user found"}), 404

        return jsonify(row)
    except Exception as err:
        return jsonify({"message": "Error loading profile", "error": str(err)}), 500
