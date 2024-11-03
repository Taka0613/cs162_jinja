import pytest
from ..models import User, Task, TaskGroup  # Import necessary models
from .. import db, create_app  # Import database and app factory


@pytest.fixture
def client():
    # Set up the Flask app and database for testing
    app = create_app()
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Initialize the database for tests
        yield client
        with app.app_context():
            db.drop_all()  # Clean up the database after tests


def test_task_movement(client):
    with client.application.app_context():  # Ensure application context for database queries
        # Create a user, task group, and task to test movement
        user = User(username="user1")
        user.set_password("password")  # Use set_password method to set hashed password
        db.session.add(user)
        db.session.commit()

        task_group1 = TaskGroup(title="Group 1", user_id=user.id)
        task_group2 = TaskGroup(title="Group 2", user_id=user.id)
        db.session.add(task_group1)
        db.session.add(task_group2)
        db.session.commit()

        task = Task(title="Task 1", user_id=user.id, task_group_id=task_group1.id)
        db.session.add(task)
        db.session.commit()

        # Log in as the user and move the task to a different group
        client.post("/login", data={"username": "user1", "password": "password"})
        response = client.post(
            f"/move_task/{task.id}", json={"new_group_id": task_group2.id}
        )
        assert response.status_code == 200  # Should succeed in moving the task


def test_unauthorized_task_movement(client):
    with client.application.app_context():
        # Create two users and a task for user1
        user1 = User(username="user1")
        user1.set_password("password1")  # Use set_password method for password hashing
        user2 = User(username="user2")
        user2.set_password("password2")  # Use set_password method for password hashing
        db.session.add_all([user1, user2])
        db.session.commit()

        task_group1 = TaskGroup(title="Group 1", user_id=user1.id)
        task_group2 = TaskGroup(title="Group 2", user_id=user1.id)
        db.session.add_all([task_group1, task_group2])
        db.session.commit()

        task = Task(title="Task 1", user_id=user1.id, task_group_id=task_group1.id)
        db.session.add(task)
        db.session.commit()

        # Log in as user2 and attempt to move user1's task (should be unauthorized)
        client.post("/login", data={"username": "user2", "password": "password2"})
        response = client.post(
            f"/move_task/{task.id}", json={"new_group_id": task_group2.id}
        )
        assert response.status_code == 403  # Unauthorized users should not move tasks
