from flask import Flask, request, render_template, redirect, session, url_for
from flask_oauthlib.client import OAuth
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
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
REDIRECT_URI = "/getAToken"  # Redirect URI path
SCOPE = ["User.Read"]  # Permissions to request

# OAuth configuration
oauth = OAuth(app)
microsoft = oauth.remote_app(
    'microsoft',
    consumer_key=CLIENT_ID,
    consumer_secret=CLIENT_SECRET,
    request_token_params={
        'scope': ' '.join(SCOPE),
        'response_type': 'code',
    },
    base_url='https://graph.microsoft.com/v1.0/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url=f'{AUTHORITY}/oauth2/v2.0/token',
    authorize_url=f'{AUTHORITY}/oauth2/v2.0/authorize',
)

# Authenticate with Managed Identity
credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
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


@app.route('/manage', methods=['GET', 'POST'])
def manage_files():
    if 'microsoft_token' not in session:
        return redirect(url_for('login'))

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


@app.route('/login')
def login():
    return microsoft.authorize(callback=url_for('authorized', _external=True))


@app.route(REDIRECT_URI)
def authorized():
    response = microsoft.authorized_response()
    if response is None or response.get('access_token') is None:
        return f"Access denied: {request.args.get('error')} - {request.args.get('error_description')}", 403

    # Store the token in the session
    session['microsoft_token'] = (response['access_token'], '')
    return redirect(url_for('manage_files'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@microsoft.tokengetter
def get_microsoft_oauth_token():
    return session.get('microsoft_token')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)