from . import db  # Import the database instance
from flask_login import UserMixin  # Flask-Login's mixin for user session management
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)  # Functions for hashing and verifying passwords


# User model representing each user in the application
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    username = db.Column(
        db.String(150), nullable=False, unique=True
    )  # Username must be unique and not nullable
    password_hash = db.Column(
        db.String(256), nullable=False
    )  # Stores hashed password for security

    # Establish one-to-many relationship with TaskGroup model, 'task_groups' stores all groups owned by a user
    task_groups = db.relationship("TaskGroup", backref="owner", lazy=True)

    # Method to hash and set the user's password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Method to check if a provided password matches the stored hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# TaskGroup model representing a group of tasks, associated with a user
class TaskGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    title = db.Column(
        db.String(150), nullable=False
    )  # Task group title must be provided
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # Foreign key linking to the User model
    tasks = db.relationship(
        "Task", backref="task_group", lazy=True
    )  # One-to-many relationship with Task model


# Task model representing individual tasks, which can be organized hierarchically with subtasks
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    title = db.Column(db.String(150), nullable=False)  # Task title must be provided
    status = db.Column(
        db.String(20), nullable=False, default="To Do"
    )  # Default status is "To Do"
    is_completed = db.Column(
        db.Boolean, default=False
    )  # Boolean flag indicating if the task is completed
    task_group_id = db.Column(
        db.Integer, db.ForeignKey("task_group.id"), nullable=False
    )  # Foreign key to TaskGroup
    parent_task_id = db.Column(
        db.Integer, db.ForeignKey("task.id"), nullable=True
    )  # Foreign key for hierarchical tasks

    # Establish self-referential relationship for subtasks with cascading delete
    subtasks = db.relationship(
        "Task",
        backref=db.backref("parent_task", remote_side=[id]),
        lazy=True,
        cascade="all, delete-orphan",  # Deletes all subtasks when parent task is deleted
    )

    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # Foreign key to User model
    user = db.relationship(
        "User", backref="tasks"
    )  # Relationship linking task to its owner (User)

    # Method to calculate the depth of a task in the hierarchy, where depth is limited in the app logic
    def get_depth(self):
        depth = 1
        parent = self.parent_task
        while parent:
            depth += 1  # Increase depth with each level of parent task
            parent = parent.parent_task  # Move up to the next level in hierarchy
        return depth
