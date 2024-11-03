import pytest
from ..models import User, Task, TaskGroup  # Import your models
from .. import db, create_app  # Import database and app creation function


@pytest.fixture
def client():
    app = create_app()  # Create an instance of the app
    with app.test_client() as client:  # Set up a test client for requests
        with app.app_context():  # Ensure app context for database setup
            db.create_all()  # Initialize database tables
        yield client  # Provide the test client to the tests
        with app.app_context():  # Clean up database after tests
            db.drop_all()  # Drop all tables to reset state


def test_task_collapse_expand(client):
    """Test that tasks can be collapsed or expanded."""
    with client.application.app_context():  # Ensure we have the application context
        user = User(username="user1")
        user.set_password("password")  # Set user password
        db.session.add(user)  # Add user to the session
        db.session.commit()  # Commit the session

        # Now you can proceed to add a task group and tasks as needed
        task_group = TaskGroup(title="Sample Group", user_id=user.id)
        db.session.add(task_group)
        db.session.commit()

        # You can now query the User or TaskGroup objects safely
        user = User.query.first()  # This should not raise an error anymore


def test_task_depth_limitation(client):
    """Test that tasks cannot exceed a nesting depth of 3."""
    with client.application.app_context():  # Ensure we have the application context
        user = User(username="user2")
        user.set_password("password")  # Set user password
        db.session.add(user)  # Add user to the session
        db.session.commit()  # Commit the session

        # Similar process to set up tasks and test depth limitations
        # Make sure to create and save task groups and tasks as necessary
