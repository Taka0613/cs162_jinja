# app/models.py
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)

    # Update backref name to avoid conflict
    task_groups = db.relationship("TaskGroup", backref="owner", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class TaskGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    tasks = db.relationship("Task", backref="task_group", lazy=True)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="To Do")
    is_completed = db.Column(db.Boolean, default=False)
    task_group_id = db.Column(
        db.Integer, db.ForeignKey("task_group.id"), nullable=False
    )
    parent_task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=True)
    subtasks = db.relationship(
        "Task",
        backref=db.backref("parent_task", remote_side=[id]),
        lazy=True,
        cascade="all, delete-orphan",  # Enable cascading deletion of subtasks
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="tasks")

    def get_depth(self):
        depth = 1
        parent = self.parent_task
        while parent:
            depth += 1
            parent = parent.parent_task
        return depth
