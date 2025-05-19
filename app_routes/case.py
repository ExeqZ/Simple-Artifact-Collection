from flask import Blueprint, render_template, request, jsonify
from services.db_service import get_db_connection
from services.blob_service import blob_service_client
from utils.auth import login_required
import json

bp = Blueprint('case', __name__, url_prefix='/case')

def load_blobinventory(container_client):
    inventory_client = container_client.get_blob_client('.blobinventory')
    if inventory_client.exists():
        content = inventory_client.download_blob().readall()
        try:
            return json.loads(content.decode('utf-8'))
        except Exception:
            return []
    return []

def save_blobinventory(container_client, inventory):
    inventory_client = container_client.get_blob_client('.blobinventory')
    inventory_bytes = json.dumps(inventory, indent=2).encode('utf-8')
    inventory_client.upload_blob(inventory_bytes, overwrite=True)

def update_blobinventory_on_delete(container_client, filename):
    inventory = load_blobinventory(container_client)
    inventory = [entry for entry in inventory if entry['name'] != filename]
    save_blobinventory(container_client, inventory)

@bp.route('/<case_id>', methods=['GET'])
@login_required
def view_case(case_id):
    """
    View details of a specific case, including files in its blob container.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch case details from the database
    cursor.execute("SELECT name, container_name FROM Cases WHERE container_name = ?", (case_id,))
    case = cursor.fetchone()
    if not case:
        return "Case not found.", 404

    case_name, container_name = case

    # List blobs in the container
    try:
        container_client = blob_service_client.get_container_client(container_name)
        blobs = container_client.list_blobs()
        blob_list = [{"name": blob.name, "size": blob.size} for blob in blobs]
    except Exception as e:
        return f"Error fetching blobs: {e}", 500

    return render_template('case.html', case={"name": case_name, "container_name": container_name}, blobs=blob_list)

@bp.route('/<case_id>/files', methods=['GET'])
@login_required
def list_case_files(case_id):
    """
    API endpoint to list files in a specific case's blob container.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the container name for the case
    cursor.execute("SELECT container_name FROM Cases WHERE id = ?", (case_id,))
    result = cursor.fetchone()
    if not result:
        return jsonify({"error": "Case not found."}), 404

    container_name = result[0]

    # List blobs in the container
    try:
        container_client = blob_service_client.get_container_client(container_name)
        blobs = container_client.list_blobs()
        blob_list = [{"name": blob.name, "size": blob.size} for blob in blobs]
        return jsonify(blob_list), 200
    except Exception as e:
        return jsonify({"error": f"Error fetching blobs: {e}"}), 500

@bp.route('/<case_id>/files/<filename>', methods=['DELETE'])
@login_required
def delete_file(case_id, filename):
    """
    API endpoint to delete a specific file from a case's blob container.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the container name for the case
    cursor.execute("SELECT container_name FROM Cases WHERE container_name = ?", (case_id,))
    result = cursor.fetchone()
    if not result:
        return jsonify({"error": "Case not found."}), 404

    container_name = result[0]

    try:
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(filename)
        if blob_client.exists():
            blob_client.delete_blob()
            update_blobinventory_on_delete(container_client, filename)
            return jsonify({"message": "File deleted successfully."}), 200
        else:
            return jsonify({"error": "File not found."}), 404
    except Exception as e:
        return jsonify({"error": f"Error deleting file: {e}"}), 500

@bp.route('/<case_id>/files/<filename>', methods=['GET'])
@login_required
def download_file(case_id, filename):
    """
    API endpoint to download a specific file from a case's blob container.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the container name for the case
    cursor.execute("SELECT container_name FROM Cases WHERE container_name = ?", (case_id,))
    result = cursor.fetchone()
    if not result:
        return jsonify({"error": "Case not found."}), 404

    container_name = result[0]

    try:
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(filename)
        if blob_client.exists():
            file_stream = blob_client.download_blob().readall()
            return file_stream, 200, {
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/octet-stream",
            }
        else:
            return jsonify({"error": "File not found."}), 404
    except Exception as e:
        return jsonify({"error": f"Error downloading file: {e}"}), 500