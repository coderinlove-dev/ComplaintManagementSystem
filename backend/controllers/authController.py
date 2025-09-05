import os
import bcrypt
import jwt
from flask import request, jsonify
from datetime import datetime, timedelta
from config.db import get_connection 

JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret")

# ========== REGISTER USER OR STAFF ==========
def registerUser():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")
        roll_number = data.get("roll_number")
        branch = data.get("branch")

        name = f"{first_name} {last_name}"

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Find role_id (case-insensitive)
        cursor.execute("SELECT id FROM roles WHERE LOWER(name) = %s", (role.lower(),))
        role_row = cursor.fetchone()
        if not role_row:
            return jsonify({"message": "Invalid role specified."}), 400
        role_id = role_row["id"]

        # Check duplicate email
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"message": "Email already registered. Please log in."}), 409

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Staff needs approval, users auto-approved
        is_approved = False if role.lower() == "staff" else True

        # Insert new user
        cursor.execute(
            """
            INSERT INTO users 
                (name, first_name, last_name, email, password, role_id, is_approved, roll_number, branch)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (name, first_name, last_name, email, hashed_password, role_id, is_approved, roll_number, branch)
        )
        conn.commit()
        new_user_id = cursor.lastrowid

        if role.lower() == "staff":
            return jsonify({"message": "Staff registration submitted! Await admin approval."}), 201

        elif role.lower() == "user":
            # Generate JWT
            token = jwt.encode(
                {"id": new_user_id, "role": role, "exp": datetime.utcnow() + timedelta(days=1)},
                JWT_SECRET,
                algorithm="HS256"
            )
            user_profile = {
                "id": new_user_id,
                "email": email,
                "role": role,
                "first_name": first_name,
                "last_name": last_name,
                "roll_number": roll_number,
                "branch": branch
            }
            return jsonify({
                "message": "Registration successful!",
                "token": token,
                "user": user_profile
            }), 201

        else:
            return jsonify({"message": "Invalid role specified."}), 400

    except Exception as e:
        return jsonify({"message": "Registration failed.", "error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ========== LOGIN USER, STAFF, OR ADMIN ==========
def loginUser():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT users.*, roles.name as role 
            FROM users 
            JOIN roles ON users.role_id = roles.id 
            WHERE email = %s
            """,
            (email,)
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "No account with this email. Please register."}), 404

        # 🚨 Check staff status
        if user["role"].lower() == "staff":
            if user["staff_status"] == "Pending":
                return jsonify({"message": "Staff account is pending admin approval."}), 403
            elif user["staff_status"] == "Rejected":
                return jsonify({"message": "Your staff account was rejected by admin."}), 403

        # Verify password
        if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            return jsonify({"message": "Incorrect password."}), 401

        # Generate Access & Refresh Tokens
        access_token = jwt.encode(
            {"id": user["id"], "role": user["role"], "exp": datetime.utcnow() + timedelta(minutes=30)},
            JWT_SECRET,
            algorithm="HS256"
        )

        refresh_token = jwt.encode(
            {"id": user["id"], "role": user["role"], "exp": datetime.utcnow() + timedelta(days=7)},
            JWT_SECRET,
            algorithm="HS256"
        )

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "role": user["role"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "roll_number": user["roll_number"],
                "branch": user["branch"],
                "staff_status": user["staff_status"]  # include staff status in response
            }
        }), 200

    except Exception as e:
        return jsonify({"message": "Login failed", "error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
