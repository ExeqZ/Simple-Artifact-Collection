from flask import Flask, request, render_template
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import os
import uuid

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

# Get storage account URL and container name from environment variables
STORAGE_ACCOUNT_URL = os.environ.get("STORAGE_ACCOUNT_URL")
CONTAINER_NAME = "uploads"

# Print the storage account URL for debugging
print(f"STORAGE_ACCOUNT_URL: {STORAGE_ACCOUNT_URL}")

# Authenticate with Managed Identity
credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        try:
            file = request.files['file']
            if file:
                # Generate a unique blob name
                blob_name = f"{uuid.uuid4()}_{file.filename}"
                # Get a blob client
                blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
                # Upload the file to Azure Blob Storage
                blob_client.upload_blob(file.read())
                return f"Upload successful! File stored as: {blob_name}"
        except Exception as e:
            # Log the error to the console
            print(f"Error: {e}")
            # Return the error message in the response for debugging
            return f"An error occurred during file upload: {e}", 500
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
