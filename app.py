from flask import Flask, render_template, redirect, url_for, session, request
from app_routes import admin, auth, case
from services.db_service import init_db, get_db_connection
import os
import re
from services.blob_service import blob_service_client, create_container
import hashlib
import json
from datetime import datetime
import zipfile
import io

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default-secret-key")

UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "./uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
init_db(app)

# Ensure the default case exists
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT container_name FROM Cases WHERE container_name = 'uploads'")
if not cursor.fetchone():
    create_container("uploads")
    cursor.execute(
        "INSERT INTO Cases (name, container_name, secret) VALUES (?, ?, ?)",
        ("default", "uploads", "0000-0000-0000-0000"),
    )
    conn.commit()

# Register Blueprints
app.register_blueprint(admin.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(case.bp)

def load_blobinventory(container_client):
    inventory_client = container_client.get_blob_client('.blobinventory')
    if inventory_client.exists():
        content = inventory_client.download_blob().readall()
        try:
            return json.loads(content.decode('utf-8'))
        except Exception:
            return []
    return []

def save_blobinventory(container_client, inventory):
    inventory_client = container_client.get_blob_client('.blobinventory')
    inventory_bytes = json.dumps(inventory, indent=2).encode('utf-8')
    inventory_client.upload_blob(inventory_bytes, overwrite=True)

def update_blobinventory_on_upload(container_client, file, file_hash):
    inventory = load_blobinventory(container_client)
    # Remove any existing entry for this file name
    inventory = [entry for entry in inventory if entry['name'] != file.filename]
    # Add new entry
    entry = {
        "name": file.filename,
        "size": file.content_length,
        "upload_date": datetime.utcnow().isoformat() + "Z",
        "hash": file_hash
    }
    inventory.append(entry)
    save_blobinventory(container_client, inventory)

def update_blobinventory_on_delete(container_client, filename):
    inventory = load_blobinventory(container_client)
    inventory = [entry for entry in inventory if entry['name'] != filename]
    save_blobinventory(container_client, inventory)

def compress_and_secure_file(file, password="infected"):
    """Compress and secure the file with a password."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_info = zipfile.ZipInfo(file.filename)
        zip_file.writestr(zip_info, file.read(), compress_type=zipfile.ZIP_DEFLATED)
        zip_file.setpassword(password.encode())
    zip_buffer.seek(0)
    return zip_buffer

def is_compressed_with_password(file, password="infected"):
    """Check if the file is a ZIP file secured with the given password."""
    try:
        with zipfile.ZipFile(file) as zip_file:
            # Test if the file can be opened with the password
            zip_file.setpassword(password.encode())
            zip_file.testzip()  # Will raise an exception if the password is incorrect
        return True
    except (zipfile.BadZipFile, RuntimeError, zipfile.LargeZipFile):
        return False

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
        inventory = load_blobinventory(container_client)
        for file in files:
            file.seek(0)
            file_bytes = file.read()
            file_hash = hashlib.sha256(file_bytes).hexdigest()
            file.seek(0)  # Reset file pointer for further processing

            # Check for hash match in inventory before compression
            match = next((entry for entry in inventory if entry['hash'] == file_hash), None)
            if match:
                # Double check hash with actual blob content
                blob_client = container_client.get_blob_client(match['name'])
                if blob_client.exists():
                    existing_blob_bytes = blob_client.download_blob().readall()
                    existing_blob_hash = hashlib.sha256(existing_blob_bytes).hexdigest()
                    if existing_blob_hash == file_hash:
                        blob_client.upload_blob(file, overwrite=True)
                        update_blobinventory_on_upload(container_client, file, file_hash)
                        continue  # File uploaded/overwritten, go to next file

            # Compress and secure the file if no match is found
            if is_compressed_with_password(file):
                compressed_file = file  # Use the file as-is
            else:
                compressed_file = compress_and_secure_file(file)

            # Handle name collision and upload the file
            blob_client = container_client.get_blob_client(file.filename + ".zip")
            if blob_client.exists():
                base_name, extension = os.path.splitext(file.filename)
                counter = 1
                new_filename = f"{base_name}_{counter}{extension}.zip"
                new_blob_client = container_client.get_blob_client(new_filename)
                while new_blob_client.exists():
                    counter += 1
                    new_filename = f"{base_name}_{counter}{extension}.zip"
                    new_blob_client = container_client.get_blob_client(new_filename)
                new_blob_client.upload_blob(compressed_file)
                # Update inventory with new name
                file.filename = new_filename
                update_blobinventory_on_upload(container_client, file, file_hash)
            else:
                blob_client.upload_blob(compressed_file)
                update_blobinventory_on_upload(container_client, file, file_hash)
        return render_template('upload.html', message="Files uploaded successfully", message_type="success")
    except Exception as e:
        return render_template('upload.html', message=f"Error uploading files: {e}", message_type="error")

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)