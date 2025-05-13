from flask import Flask
from app_routes import admin, auth, case, manage
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)