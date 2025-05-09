from flask import Flask, request, render_template
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import os
import uuid

app = Flask(__name__)

# Get storage account URL from environment variable
STORAGE_ACCOUNT_URL = os.environ["STORAGE_ACCOUNT_URL"]
CONTAINER_NAME = "uploads"

# Authenticate with Managed Identity
credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=str(uuid.uuid4()) + "_" + file.filename)
            blob_client.upload_blob(file.read())
            return "Upload successful!"
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
