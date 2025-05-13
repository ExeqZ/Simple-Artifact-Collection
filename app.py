from flask import Flask, render_template, redirect, url_for, session
from app_routes import admin, auth, case
from services.db_service import init_db
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default-secret-key")

# Initialize Azure Blob Storage
STORAGE_ACCOUNT_URL = os.environ.get("STORAGE_ACCOUNT_URL")
credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)

# Initialize database
init_db(app)

# Register Blueprints
app.register_blueprint(admin.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(case.bp)

@app.route('/', endpoint='index')
def welcome():
    """Welcome page with app description and navigation menu."""
    return render_template('welcome.html')

@app.route('/admin')
def admin_portal():
    """Admin page that requires login."""
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    return redirect(url_for("admin.admin_portal"))

@app.route('/upload')
def upload_page():
    """File upload page that does not require login."""
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)