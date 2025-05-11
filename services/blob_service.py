from azure.storage.blob import BlobServiceClient
import os

STORAGE_ACCOUNT_URL = os.environ.get("STORAGE_ACCOUNT_URL")
credential = None  # Use DefaultAzureCredential or other credentials
blob_service_client = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)

def create_container(container_name):
    container_client = blob_service_client.get_container_client(container_name)
    container_client.create_container()