import os  # Import os module for generating random data
from flask import (
    session,
    request,
    abort,
)  # Import session for storing token, request for accessing form data, and abort for error handling


# Function to generate a CSRF token and store it in the user's session
def generate_csrf_token():
    # Check if a CSRF token already exists in the session
    if "_csrf_token" not in session:
        # Generate a new token as a random 16-byte hexadecimal string
        session["_csrf_token"] = os.urandom(16).hex()
    return session["_csrf_token"]  # Return the token (newly generated or existing)


# Function to verify the CSRF token provided in a request
def verify_csrf_token():
    # Retrieve the token stored in the session
    token = session.get("_csrf_token")
    # Retrieve the CSRF token provided by the client, either from the form or the headers
    request_token = request.form.get("csrf_token") or request.headers.get("X-CSRFToken")

    # If no token is found in the session or request, or if tokens don't match, abort with a 400 error
    if not token or not request_token or token != request_token:
        abort(400)
