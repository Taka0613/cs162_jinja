import pytest
from ..models import User  # Import User model using relative import
from .. import db, create_app  # Import database and app creation function


@pytest.fixture
def client():
    # Set up the Flask app and database for testing
    app = create_app()  # Create the app without any configuration argument
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create all tables before each test
        yield client
        with app.app_context():
            db.drop_all()  # Drop all tables after each test to ensure a clean state


def test_user_registration(client):
    # Test that a new user can register successfully
    response = client.post(
        "/register", data={"username": "testuser", "password": "testpass"}
    )
    # Check if registration redirects (status code 302 means "Found" for redirection)
    assert response.status_code == 302  # Registration should redirect after success
    # Verify that the user was successfully added to the database
    assert User.query.filter_by(username="testuser").first() is not None


def test_user_login(client):
    # Register a user to set up for login
    client.post("/register", data={"username": "testuser", "password": "testpass"})
    # Test that a registered user can log in
    response = client.post(
        "/login", data={"username": "testuser", "password": "testpass"}
    )
    # Check if login redirects (status code 302 means "Found" for redirection)
    assert (
        response.status_code == 302
    )  # Login should redirect to the dashboard or home page


def test_user_access_control(client):
    # Register two users for testing access control
    client.post("/register", data={"username": "user1", "password": "password1"})
    client.post("/register", data={"username": "user2", "password": "password2"})

    # Log in as user1 and check if they can access the main page
    client.post("/login", data={"username": "user1", "password": "password1"})
    response = client.get("/")  # Test the root route as a fallback
    assert (
        response.status_code == 200
    )  # Should successfully show user1's dashboard or tasks

    # Log out user1 before logging in as user2
    client.get("/logout")  # Ensure a logout route is defined

    # Log in as user2 and check if they can access the same main page
    client.post("/login", data={"username": "user2", "password": "password2"})
    response = client.get("/")
    assert (
        response.status_code == 200
    )  # Should successfully show user2's dashboard or tasks
