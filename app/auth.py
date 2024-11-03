from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)  # Used for password hashing and checking
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)  # Flask-Login functions and decorators
from .models import User  # Import the User model
from . import db, login_manager  # Import database instance and login manager
from .models import (
    Task,
    TaskGroup,
)  # Import Task and TaskGroup models for managing tasks

# Create a Blueprint for the authentication routes
auth = Blueprint("auth", __name__)


# User loader for Flask-Login
# This function loads the user given their user_id and is required by Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Retrieve user by ID for session management


# Registration route
@auth.route("/register", methods=["GET", "POST"])
def register():
    # Redirect to dashboard if user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    # Process form submission
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if username already exists in the database
        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for("auth.register"))

        # Create new user, hash the password, and save user to database
        user = User(username=username)
        user.set_password(password)  # Set hashed password
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for("auth.login"))

    # Render registration form
    return render_template("register.html")


# Login route
@auth.route("/login", methods=["GET", "POST"])
def login():
    # Redirect to dashboard if user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    # Process form submission
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if user exists and if password matches
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)  # Log the user in
            return redirect(url_for("auth.dashboard"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("auth.login"))

    # Render login form
    return render_template("login.html")


# Dashboard route - requires login
@auth.route("/")
@login_required
def dashboard():
    # Fetch task groups associated with the logged-in user
    task_groups = TaskGroup.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", task_groups=task_groups)


# Create a new task group
@auth.route("/create_task_group", methods=["GET", "POST"])
@login_required
def create_task_group():
    if request.method == "POST":
        title = request.form.get("title")

        # Check if title is provided
        if not title:
            flash("Title is required.")
            return redirect(url_for("auth.create_task_group"))

        # Check if task group with the same title already exists for the user
        existing_group = TaskGroup.query.filter_by(
            title=title, user_id=current_user.id
        ).first()
        if existing_group:
            flash("A list with this name already exists.")
            return redirect(url_for("auth.create_task_group"))

        # Create and save new task group
        new_group = TaskGroup(title=title, user_id=current_user.id)
        db.session.add(new_group)
        db.session.commit()
        flash("New task group created successfully.")
        return redirect(url_for("auth.dashboard"))

    # Render the task group creation form
    return render_template("create_task_group.html")


# Add a new task to a specified task group
@auth.route("/task_groups/<int:group_id>/add_task", methods=["GET", "POST"])
@login_required
def add_task(group_id):
    # Fetch the specified task group to ensure it belongs to the current user
    task_group = TaskGroup.query.filter_by(id=group_id, user_id=current_user.id).first()
    if not task_group:
        flash("Task group not found or you don't have permission.")
        return redirect(url_for("auth.dashboard"))

    # Process form submission
    if request.method == "POST":
        title = request.form.get("title")

        # Check if title is provided
        if not title:
            flash("Title is required.")
            return redirect(url_for("auth.add_task", group_id=group_id))

        # Default status is set to 'To Do'
        status = request.form.get("status", "To Do")

        # Create new task and save it to the database
        new_task = Task(
            title=title,
            status=status,
            task_group_id=group_id,
            user_id=current_user.id,
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("auth.dashboard"))

    # Render task creation form
    return render_template("add_task.html", task_group=task_group)


# Add a subtask under a specific parent task
@auth.route("/tasks/<int:task_id>/add_subtask", methods=["GET", "POST"])
@login_required
def add_subtask(task_id):
    # Fetch parent task and ensure it belongs to the user
    parent_task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not parent_task:
        flash("Parent task not found or you don't have permission.")
        return redirect(url_for("auth.dashboard"))

    # Check task depth to prevent more than 3 levels of subtasks
    if parent_task.get_depth() >= 3:
        flash("Cannot add more than 3 levels of subtasks.")
        return redirect(url_for("auth.dashboard"))

    # Process form submission
    if request.method == "POST":
        title = request.form.get("title")

        # Ensure title is provided for the subtask
        if not title:
            flash("Title is required to add a subtask.")
            return redirect(url_for("auth.add_subtask", task_id=task_id))

        # Default status is the same as the parent task's status
        status = request.form.get("status", parent_task.status)

        # Create new subtask and save it to the database
        new_task = Task(
            title=title,
            status=status,
            parent_task_id=task_id,
            task_group_id=parent_task.task_group_id,
            user_id=current_user.id,
        )
        db.session.add(new_task)
        db.session.commit()

        flash("Subtask added successfully.")
        return redirect(url_for("auth.dashboard"))

    # Render subtask creation form
    return render_template(
        "add_task.html", parent_task=parent_task, task_group=parent_task.task_group
    )


# Delete a task by ID
@auth.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    # Fetch task and ensure it belongs to the current user
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        flash("Task not found or you don't have permission.")
        return redirect(url_for("auth.dashboard"))

    # Delete the task and commit the change
    db.session.delete(task)
    db.session.commit()

    flash("Task deleted successfully.")
    return redirect(url_for("auth.dashboard"))


# Move a task to a different task group
@auth.route("/move_task/<int:task_id>", methods=["POST"])
@login_required
def move_task(task_id):
    data = request.get_json()  # Parse JSON data from the request
    new_group_id = data.get("new_group_id")  # Get the target group ID

    # Fetch the task and ensure it belongs to the user
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({"error": "Task not found or you don't have permission."}), 403

    # Update task group and save changes
    task.task_group_id = new_group_id
    db.session.commit()

    return jsonify({"success": "Task moved successfully."})


# Logout route
@auth.route("/logout")
@login_required
def logout():
    logout_user()  # Log the user out
    return redirect(url_for("auth.login"))


# Delete a task group and optionally delete all associated tasks
@auth.route("/delete_task_group/<int:group_id>", methods=["POST"])
@login_required
def delete_task_group(group_id):
    # Fetch the task group and ensure it belongs to the user
    task_group = TaskGroup.query.filter_by(id=group_id, user_id=current_user.id).first()
    if not task_group:
        flash("Task group not found or you don't have permission.")
        return redirect(url_for("auth.dashboard"))

    # Delete all tasks within the group (optional)
    Task.query.filter_by(task_group_id=group_id).delete()

    # Delete the task group itself
    db.session.delete(task_group)
    db.session.commit()

    flash("Task group deleted successfully.")
    return redirect(url_for("auth.dashboard"))
