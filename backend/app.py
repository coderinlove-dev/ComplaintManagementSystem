# app.py

import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="public")
CORS(app)  # Enable CORS

# ====================
# ROUTES IMPORTS
# ====================
from routes.userRoutes import user_bp
from routes.complaintRoutes import complaint_bp
from routes.staffRoutes import staff_bp
from routes.adminRoutes import admin_bp
from routes.authRoutes import auth_bp

# ====================
# REGISTER BLUEPRINTS
# ====================
app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(complaint_bp, url_prefix="/api/complaints")
app.register_blueprint(staff_bp, url_prefix="/api/staff")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(auth_bp, url_prefix="/api/auth")

# ====================
# STATIC FILES
# ====================
@app.route('/')
def serve_index():
    return app.send_static_file('landingpage.html')  # Main page

@app.route('/<path:path>')
def serve_pages(path):
    return send_from_directory(app.static_folder, path)

# ====================
# RUN SERVER
# ====================
if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT, debug=True)
