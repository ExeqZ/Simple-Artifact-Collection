from flask import Blueprint, request, render_template
from services.db_service import get_db_connection
from services.blob_service import create_container, blob_service_client
from utils.auth import login_required
import uuid
import secrets

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/', methods=['GET', 'POST'])
@login_required
def admin_portal():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        case_name = request.form.get('case_name')
        if not case_name:
            return "Case name is required.", 400

        container_name = f"case-{uuid.uuid4().hex[:8]}"
        secret = secrets.token_hex(16)

        try:
            create_container(container_name, blob_service_client)
            cursor.execute(
                "INSERT INTO Cases (name, container_name, secret) VALUES (?, ?, ?)",
                (case_name, container_name, secret),
            )
            conn.commit()
        except Exception as e:
            return f"Error creating case: {e}", 500

    # Fetch all current cases with additional details
    cursor.execute("SELECT name, secret, container_name FROM Cases")
    cases = []
    for row in cursor.fetchall():
        case_name, secret, container_name = row
        try:
            container_client = blob_service_client.get_container_client(container_name)
            blobs = list(container_client.list_blobs())
            file_count = len(blobs)
            total_size = sum(blob.size for blob in blobs)
        except Exception:
            file_count = 0
            total_size = 0
        cases.append({
            "name": case_name,
            "secret": secret,
            "file_count": file_count,
            "total_size": total_size,
            "container_name": container_name,
        })

    return render_template('admin.html', cases=cases)

@bp.route('/api/cases', methods=['GET'])
@login_required
def get_cases():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Cases")
    cases = [row[0] for row in cursor.fetchall()]
    return {"cases": cases}, 200