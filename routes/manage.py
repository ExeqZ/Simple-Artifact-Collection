from flask import Blueprint, request, jsonify
from services.db_service import get_db_connection
from services.blob_service import blob_service_client
import os

bp = Blueprint('manage', __name__, url_prefix='/manage')

@bp.route('/api/upload', methods=['POST'])
def upload_file():
    # Get the connection ID from the request
    connection_id = request.form.get('connectionId')
    if not connection_id:
        return jsonify({"error": "Connection ID is required."}), 400

    # Validate the connection ID and get the container name
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT container_name FROM Cases WHERE secret = ?", (connection_id,))
    result = cursor.fetchone()
    if not result:
        return jsonify({"error": "Invalid Connection ID."}), 400

    container_name = result[0]

    # Get the uploaded files
    files = request.files.getlist('file')
    if not files:
        return jsonify({"error": "No files uploaded."}), 400

    # Upload files to the blob container
    uploaded_files = []
    try:
        for file in files:
            blob_name = file.filename
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            blob_client.upload_blob(file.read(), overwrite=True)
            uploaded_files.append(blob_name)

        return jsonify({
            "message": "Files uploaded successfully.",
            "uploaded_files": uploaded_files,
            "container_name": container_name
        }), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred during file upload: {str(e)}"}), 500