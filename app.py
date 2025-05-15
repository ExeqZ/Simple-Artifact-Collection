from flask import Flask, render_template, redirect, url_for, session, request
from app_routes import admin, auth, case
from services.db_service import init_db, get_db_connection
import os
import re
from services.blob_service import blob_service_client

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default-secret-key")

UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "./uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
init_db(app)

# Register Blueprints
app.register_blueprint(admin.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(case.bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    secret = request.form.get('secret')
    if not secret or not re.match(r"^\d{4}-\d{4}-\d{4}-\d{4}$", secret):
        return "Invalid or missing secret key. Format: xxxx-xxxx-xxxx-xxxx", 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT container_name FROM Cases WHERE secret = ?", (secret,))
    result = cursor.fetchone()
    if not result:
        return "Invalid secret key. No matching case found.", 404

    container_name = result[0]

    if 'files' not in request.files:
        return "No files part", 400
    files = request.files.getlist('files')
    if not files or all(file.filename == '' for file in files):
        return "No selected files", 400

    try:
        container_client = blob_service_client.get_container_client(container_name)
        for file in files:
            blob_client = container_client.get_blob_client(file.filename)
            blob_client.upload_blob(file)
        return "Files uploaded successfully", 200
    except Exception as e:
        return f"Error uploading files: {e}", 500

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)