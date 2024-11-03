import pytest
from ..models import User, Task, TaskGroup  # Import models for testing
from .. import db, create_app  # Import database and app creation function
from ..utils import generate_csrf_token  # Import CSRF token generation function


# Fixture to set up the test client and initialize the database
@pytest.fixture
def client():
    app = create_app()  # Create an instance of the app
    with app.test_client() as client:  # Set up a test client for requests
        with app.app_context():  # Ensure app context for database setup
            db.create_all()  # Initialize database tables
        yield client  # Provide the test client to the tests
        with app.app_context():  # Clean up database after tests
            db.drop_all()  # Drop all tables to reset state


# Test to check that database connection and user creation work as expected
def test_database_connection(client):
    with client.application.app_context():  # Ensure app context
        # Create a new user
        user = User(username="testuser")
        user.set_password("testpass")  # Set the user's password
        db.session.add(user)  # Add user to the database session
        db.session.commit()  # Commit the session to save user

        # Verify that the user was created successfully
        assert User.query.filter_by(username="testuser").first() is not None


# Test to ensure data integrity by creating task groups and tasks
def test_data_integrity(client):
    with client.application.app_context():
        # Register and log in a user for task creation
        client.post("/register", data={"username": "user1", "password": "password"})
        client.post("/login", data={"username": "user1", "password": "password"})

        # Generate a CSRF token for secure form submission
        csrf_token = generate_csrf_token()

        # Create a task group using the CSRF token
        response_group = client.post(
            "/create_task_group",
            data={"title": "Persistent Group", "csrf_token": csrf_token},
        )
        # Check that task group creation was successful (redirect indicates success)
        assert response_group.status_code == 302

        # Retrieve the created task group for verification
        task_group = TaskGroup.query.filter_by(title="Persistent Group").first()
        print("task_group:", task_group)  # Debug: Print the task group object
        assert task_group is not None  # Verify that the group exists

        # Add a task to the created task group
        response_task = client.post(
            f"/task_groups/{task_group.id}/add_task",
            data={"title": "Persistent Task", "csrf_token": csrf_token},
        )
        print("id:", response_task)  # Debug: Print the response for task creation
        # Check if task creation was successful or redirected (200 or 302)
        assert response_task.status_code in (200, 302)

        # Verify that the task was created successfully in the task group
        task = Task.query.filter_by(
            title="Persistent Task", task_group_id=task_group.id
        ).first()
        assert task is not None  # Ensure the task exists in the database


# Test to verify task completion persistence after marking a task as complete
def test_task_completion_persistence(client):
    with client.application.app_context():
        # Create a user and set a password
        user = User(username="user1")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        # Create a task group associated with the user
        task_group = TaskGroup(title="Persistent Group", user_id=user.id)
        db.session.add(task_group)
        db.session.commit()

        # Create a task within the task group and save to the database
        task = Task(
            title="Persistent Completion", user_id=user.id, task_group_id=task_group.id
        )
        db.session.add(task)
        db.session.commit()

        # Mark the task as completed and save the change
        task.is_completed = True
        db.session.commit()

        # Retrieve the task and verify it is marked as completed
        retrieved_task = Task.query.filter_by(title="Persistent Completion").first()
        assert retrieved_task.is_completed is True  # Assert task completion status
