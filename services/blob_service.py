from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import os
import re
import secrets

STORAGE_ACCOUNT_URL = os.environ.get("STORAGE_ACCOUNT_URL")
blob_service_client = BlobServiceClient(
    account_url=STORAGE_ACCOUNT_URL,
    credential=DefaultAzureCredential()
)

def generate_secret():
    return '-'.join(f"{secrets.randbelow(10000):04}" for _ in range(4))

def create_container(container_name):
    container_client = blob_service_client.get_container_client(container_name)
    container_client.create_container()