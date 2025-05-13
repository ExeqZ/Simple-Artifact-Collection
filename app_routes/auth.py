from flask import Blueprint, redirect, session, url_for, request
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

@bp.route('/login')
def login():
    auth_url = msal_app.get_authorization_request_url(SCOPE, redirect_uri=url_for("auth.callback", _external=True))
    return redirect(auth_url)

@bp.route('/callback')
def callback():
    code = request.args.get("code")
    if code:
        try:
            result = msal_app.acquire_token_by_authorization_code(
                code,
                scopes=SCOPE,
                redirect_uri=url_for("auth.callback", _external=True),
            )
            if "access_token" in result:
                session["user"] = result.get("id_token_claims")
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
    return redirect(url_for("admin.admin_portal"))

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("auth.login"))  # Redirect to auth.login after logout