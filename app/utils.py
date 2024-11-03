import os
from flask import session, request, abort


def generate_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = os.urandom(16).hex()
    return session["_csrf_token"]


def verify_csrf_token():
    token = session.get("_csrf_token")
    request_token = request.form.get("csrf_token") or request.headers.get("X-CSRFToken")
    if not token or not request_token or token != request_token:
        abort(400)
