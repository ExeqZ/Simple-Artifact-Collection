from flask import Flask, request, render_template, redirect, session, url_for
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from msal import ConfidentialClientApplication
import os
import uuid

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())  # Secret key for session management

# Set the maximum content length for file uploads (50 MB)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

# Get storage account URL and container name from environment variables
STORAGE_ACCOUNT_URL = os.environ.get("STORAGE_ACCOUNT_URL")
CONTAINER_NAME = "uploads"

# Microsoft Entra ID (Azure AD) configuration
CLIENT_ID = os.environ.get("CLIENT_ID")  # Application (client) ID
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")  # Client secret
TENANT_ID = os.environ.get("TENANT_ID")  # Directory (tenant) ID
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_PATH = "/getAToken"  # Redirect URI path
SCOPE = ["User.Read"]  # Permissions to request
SESSION_TYPE = "filesystem"  # Token cache will be stored in the session

# MSAL Confidential Client
msal_app = ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET,
)

# Authenticate with Managed Identity
credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        try:
            files = request.files.getlist('file')  # Get all uploaded files
            if not files:
                return "No files uploaded.", 400

            uploaded_files = []
            for file in files:
                if file:
                    # Generate a unique blob name (optional, remove uuid if overwriting by name)
                    blob_name = f"{file.filename}"
                    # Get a blob client
                    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
                    # Upload the file to Azure Blob Storage with overwrite enabled
                    blob_client.upload_blob(file.read(), overwrite=True)
                    uploaded_files.append(blob_name)

            return f"Upload successful! Files stored: {', '.join(uploaded_files)}"
        except Exception as e:
            # Log the error to the console
            print(f"Error: {e}")
            # Return the error message in the response for debugging
            return f"An error occurred during file upload: {e}", 500
    return render_template('index.html')


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)