from flask import Flask, render_template, redirect, url_for, session, request
from app_routes import admin, auth, case
from services.db_service import init_db, get_db_connection
import os
import re
from services.blob_service import blob_service_client, create_container

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default-secret-key")

UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "./uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
init_db(app)

# Ensure the default case exists
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT container_name FROM Cases WHERE container_name = 'default-case'")
if not cursor.fetchone():
    create_container("default-case")
    cursor.execute(
        "INSERT INTO Cases (name, container_name, secret) VALUES (?, ?, ?)",
        ("Default Case", "default-case", "0000-0000-0000-0000"),
    )
    conn.commit()

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
        return render_template('upload.html', message="Invalid or missing secret key. Format: xxxx-xxxx-xxxx-xxxx", message_type="error")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT container_name FROM Cases WHERE secret = ?", (secret,))
    result = cursor.fetchone()
    if not result:
        return render_template('upload.html', message="Invalid secret key. No matching case found.", message_type="error")

    container_name = result[0]

    if 'files' not in request.files:
        return render_template('upload.html', message="No files part", message_type="error")
    files = request.files.getlist('files')
    if not files or all(file.filename == '' for file in files):
        return render_template('upload.html', message="No selected files", message_type="error")

    try:
        container_client = blob_service_client.get_container_client(container_name)
        for file in files:
            blob_client = container_client.get_blob_client(file.filename)
            if blob_client.exists():
                existing_blob = blob_client.get_blob_properties()
                if existing_blob.size == file.content_length:
                    blob_client.upload_blob(file, overwrite=True)
                else:
                    base_name, extension = os.path.splitext(file.filename)
                    counter = 1
                    while blob_client.exists():
                        new_filename = f"{base_name}_{counter}{extension}"
                        blob_client = container_client.get_blob_client(new_filename)
                        counter += 1
                    blob_client.upload_blob(file)
            else:
                blob_client.upload_blob(file)
        return render_template('upload.html', message="Files uploaded successfully", message_type="success")
    except Exception as e:
        return render_template('upload.html', message=f"Error uploading files: {e}", message_type="error")

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)