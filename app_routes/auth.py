from flask import Blueprint, redirect, session, url_for, request, current_app
from msal import ConfidentialClientApplication
import os

bp = Blueprint('auth', __name__, url_prefix='/auth')

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
TENANT_ID = os.environ.get("TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_PATH = "/auth/callback"
SCOPE = ["User.Read"]

msal_app = ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET,
)

def get_redirect_uri():
    """Generate the redirect URI dynamically based on the request."""
    return f"https://{request.host}{REDIRECT_PATH}"  # Force HTTPS for production

@bp.route('/login')
def login():
    redirect_uri = get_redirect_uri()
    auth_url = msal_app.get_authorization_request_url(SCOPE, redirect_uri=redirect_uri)
    return redirect(auth_url)

@bp.route('/callback')
def callback():
    code = request.args.get("code")
    if code:
        try:
            redirect_uri = get_redirect_uri()
            result = msal_app.acquire_token_by_authorization_code(
                code,
                scopes=SCOPE,
                redirect_uri=redirect_uri,
            )
            if "access_token" in result:
                session["user"] = result.get("id_token_claims")
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
    return redirect(url_for("admin.admin_portal"))

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))  # Redirect to the home page after logout