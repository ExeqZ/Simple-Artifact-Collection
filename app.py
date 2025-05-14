from flask import Flask, render_template, redirect, url_for, session, request
from app_routes import admin, auth, case
from services.db_service import init_db
import os

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
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return "File uploaded successfully", 200

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)