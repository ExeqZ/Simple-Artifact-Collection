from flask import session, redirect, url_for
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            # Redirect to the login page if the user is not logged in
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function