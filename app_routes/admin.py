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

    # Fetch all current cases to display
    cursor.execute("SELECT name FROM Cases")
    cases = [row[0] for row in cursor.fetchall()]  # Flatten the list
    return render_template('admin.html', cases=cases)

@bp.route('/api/cases', methods=['GET'])
@login_required
def get_cases():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Cases")
    cases = [row[0] for row in cursor.fetchall()]
    return {"cases": cases}, 200