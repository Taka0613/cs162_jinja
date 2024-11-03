import pytest
from ..models import User, Task, TaskGroup  # Import your models
from .. import db, create_app  # Import the app and database


@pytest.fixture
def client():
    app = create_app()  # Create an instance of the Flask app
    with app.test_client() as client:  # Set up a test client for requests
        with app.app_context():  # Ensure application context is available
            db.create_all()  # Initialize the database
        yield client  # Provide the test client to the tests
        with app.app_context():  # Clean up the database after tests
            db.drop_all()  # Drop all tables to reset state


def test_task_group_creation(client):
    """Test that a user can create a task group."""
    with client.application.app_context():  # Ensure we have the application context
        # Create a user and set the password properly
        user = User(username="testuser")  # Create a user with username
        user.set_password("testpass")  # Use a method to set the password
        db.session.add(user)  # Add user to the session
        db.session.commit()  # Commit the session to save changes

        # Log in as the user
        client.post("/login", data={"username": "testuser", "password": "testpass"})

        # Create a task group as the logged-in user
        response = client.post("/create_task_group", data={"title": "New Task Group"})
        assert response.status_code == 302  # Check for redirection upon success

        # Verify that the task group was created
        task_group = TaskGroup.query.filter_by(title="New Task Group").first()
        assert task_group is not None  # Task group should exist


def test_task_creation(client):
    """Test that a task can be added to a task group."""
    with client.application.app_context():  # Ensure we have the application context
        user = User(username="testuser2")  # Create a different user for this test
        user.set_password("testpass")  # Set password
        db.session.add(user)  # Add user to the session
        db.session.commit()  # Commit the session

        # Log in as the user
        client.post("/login", data={"username": "testuser2", "password": "testpass"})

        # Create a task group first
        client.post("/create_task_group", data={"title": "Task Group for Tasks"})

        # Retrieve the created task group to add a task
        task_group = TaskGroup.query.filter_by(title="Task Group for Tasks").first()
        response = client.post(
            f"/task_groups/{task_group.id}/add_task", data={"title": "New Task"}
        )
        assert response.status_code in (200, 302)  # Check for success or redirect


def test_task_completion(client):
    """Test that a task can be marked as complete."""
    with client.application.app_context():  # Ensure we have the application context
        user = User(username="testuser3")  # Create yet another user
        user.set_password("testpass")  # Set password
        db.session.add(user)  # Add user to the session
        db.session.commit()  # Commit the session

        # Create a task group and a task
        task_group = TaskGroup(title="Completion Group", user_id=user.id)
        db.session.add(task_group)
        db.session.commit()

        task = Task(
            title="Task to Complete", user_id=user.id, task_group_id=task_group.id
        )
        db.session.add(task)
        db.session.commit()

        # Mark the task as completed
        task.is_completed = True
        db.session.commit()

        # Verify the task's completion status
        retrieved_task = Task.query.filter_by(title="Task to Complete").first()
        assert retrieved_task.is_completed is True  # Ensure task is marked complete
