from flask import Flask, request, render_template, redirect, session, url_for
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from msal import ConfidentialClientApplication
import pyodbc
import struct
import os
import uuid
import secrets

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())  # Secret key for session management

# Set the maximum content length for file uploads (50 MB)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

# Get storage account URL and container name from environment variables
STORAGE_ACCOUNT_URL = os.environ.get("STORAGE_ACCOUNT_URL")
CONTAINER_NAME = "uploads"  # Default container name

# Microsoft Entra ID (Azure AD) configuration
CLIENT_ID = os.environ.get("CLIENT_ID")  # Application (client) ID
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")  # Client secret
TENANT_ID = os.environ.get("TENANT_ID")  # Directory (tenant) ID
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_PATH = "/getAToken"  # Redirect URI path
SCOPE = ["User.Read"]  # Permissions to request

# MSAL Confidential Client
msal_app = ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET,
)

# Authenticate with Managed Identity
credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)

# Azure SQL Database connection
SQL_SERVER = os.environ.get("SQL_SERVER")  # e.g., "your-sql-server.database.windows.net"
SQL_DATABASE = os.environ.get("SQL_DATABASE")  # e.g., "your-database-name"

# Use Managed Identity to authenticate
access_token = credential.get_token("https://database.windows.net/").token.encode("UTF-16-LE")
token_struct = struct.pack(f'<I{len(access_token)}s', len(access_token), access_token)
SQL_COPT_SS_ACCESS_TOKEN = 1256

connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SQL_SERVER};"
    f"DATABASE={SQL_DATABASE};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
)

conn = pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    case_id = request.form.get('caseId')  # Get the case ID from the form
    container_name = CONTAINER_NAME  # Default to the "uploads" container

    if case_id:
        # Find the case by ID
        cursor = conn.cursor()
        cursor.execute("SELECT container_name FROM Cases WHERE id = ?", (case_id,))
        result = cursor.fetchone()
        if result:
            container_name = result[0]  # Use the container name for the specified case
        else:
            return "Invalid Case ID.", 400

    try:
        files = request.files.getlist('file')
        if not files:
            return "No files uploaded.", 400

        uploaded_files = []
        for file in files:
            if file:
                blob_name = f"{file.filename}"
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                blob_client.upload_blob(file.read(), overwrite=True)
                uploaded_files.append(blob_name)

        return f"Upload successful! Files stored in container '{container_name}': {', '.join(uploaded_files)}"
    except Exception as e:
        return f"An error occurred during file upload: {e}", 500


@app.route('/manage', methods=['GET', 'POST'])
def manage_files():
    if not session.get("user"):
        return redirect(url_for("login"))

    try:
        # Get a list of blobs in the container
        blob_list = blob_service_client.get_container_client(CONTAINER_NAME).list_blobs()
        files = [{"name": blob.name, "size": blob.size} for blob in blob_list]

        if request.method == 'POST':
            # Handle file deletion
            file_to_delete = request.form.get('file_to_delete')
            if file_to_delete:
                blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=file_to_delete)
                blob_client.delete_blob()
                return f"File '{file_to_delete}' deleted successfully!", 200

        return render_template('manage.html', files=files)
    except Exception as e:
        # Log the error to the console
        print(f"Error: {e}")
        return f"An error occurred while managing files: {e}", 500


@app.route("/login")
def login():
    # Redirect to Microsoft Entra ID login page
    auth_url = msal_app.get_authorization_request_url(SCOPE, redirect_uri=url_for("authorized", _external=True))
    return redirect(auth_url)


@app.route(REDIRECT_PATH)
def authorized():
    # Handle the redirect from Microsoft Entra ID
    code = request.args.get("code")
    if code:
        result = msal_app.acquire_token_by_authorization_code(
            code,
            scopes=SCOPE,
            redirect_uri=url_for("authorized", _external=True),
        )
        if "access_token" in result:
            session["user"] = result.get("id_token_claims")
    return redirect(url_for("manage_files"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        f"{AUTHORITY}/oauth2/v2.0/logout?post_logout_redirect_uri={url_for('index', _external=True)}"
    )


@app.route('/admin', methods=['GET', 'POST'])
def admin_portal():
    cursor = conn.cursor()

    if request.method == 'POST':
        # Create a new case
        case_name = request.form.get('case_name')
        if not case_name:
            return "Case name is required.", 400

        # Generate a unique container name and secret
        container_name = f"case-{uuid.uuid4().hex[:8]}"
        secret = secrets.token_hex(16)

        try:
            # Create the blob container in Azure Storage
            blob_service_client.create_container(container_name)

            # Save the case to Azure SQL
            cursor.execute(
                "INSERT INTO Cases (name, container_name, secret) VALUES (?, ?, ?)",
                (case_name, container_name, secret),
            )
            conn.commit()
        except Exception as e:
            return f"Error creating case or blob container: {e}", 500

    # Fetch all cases
    cursor.execute("SELECT * FROM Cases")
    cases = cursor.fetchall()
    return render_template('admin.html', cases=cases)


@app.route('/admin/case/<int:case_id>')
def view_case(case_id):
    if not session.get("user"):
        return redirect(url_for("login"))

    case = Case.query.get_or_404(case_id)
    try:
        # List blobs in the container
        container_client = blob_service_client.get_container_client(case.container_name)
        blobs = container_client.list_blobs()
        blob_list = [{"name": blob.name, "size": blob.size} for blob in blobs]
    except Exception as e:
        return f"Error fetching blobs: {e}", 500

    return render_template('case.html', case=case, blobs=blob_list)


if __name__ == '__main__':
    # Force Flask to generate HTTPS URLs
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.run(host='0.0.0.0', port=8000)