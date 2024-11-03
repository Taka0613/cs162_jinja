from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from . import db, login_manager  # Import login_manager
from .models import Task, TaskGroup


auth = Blueprint("auth", __name__)


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Registration route
@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for("auth.register"))

        # Create new user
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for("auth.login"))
    return render_template("register.html")


# Login route
@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("auth.dashboard"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("auth.login"))
    return render_template("login.html")


# Dashboard route
@auth.route("/")
@login_required
def dashboard():
    task_groups = TaskGroup.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", task_groups=task_groups)


@auth.route("/create_task_group", methods=["GET", "POST"])
@login_required
def create_task_group():
    if request.method == "POST":
        title = request.form.get("title")
        if not title:
            flash("Title is required.")
            return redirect(url_for("auth.create_task_group"))

        # Check if the user already has a list with the same name
        existing_group = TaskGroup.query.filter_by(
            title=title, user_id=current_user.id
        ).first()
        if existing_group:
            flash("A list with this name already exists.")
            return redirect(url_for("auth.create_task_group"))

        new_group = TaskGroup(title=title, user_id=current_user.id)
        db.session.add(new_group)
        db.session.commit()
        flash("New task group created successfully.")
        return redirect(url_for("auth.dashboard"))

    # Render the form if the request method is GET
    return render_template("create_task_group.html")


@auth.route("/task_groups/<int:group_id>/add_task", methods=["GET", "POST"])
@login_required
def add_task(group_id):
    # Fetch the task group
    task_group = TaskGroup.query.filter_by(id=group_id, user_id=current_user.id).first()
    if not task_group:
        flash("Task group not found or you don't have permission.")
        return redirect(url_for("auth.dashboard"))

    # Check for POST method to process the form
    if request.method == "POST":
        # Try to retrieve title from request.form
        title = request.form.get("title")
        if not title:
            flash("Title is required.")
            return redirect(url_for("auth.add_task", group_id=group_id))

        status = request.form.get("status", "To Do")
        new_task = Task(
            title=title,
            status=status,
            task_group_id=group_id,
            user_id=current_user.id,
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("auth.dashboard"))

    return render_template("add_task.html", task_group=task_group)


@auth.route("/tasks/<int:task_id>/add_subtask", methods=["GET", "POST"])
@login_required
def add_subtask(task_id):
    # Fetch the parent task to ensure it exists and belongs to the user
    parent_task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not parent_task:
        flash("Parent task not found or you don't have permission.")
        return redirect(url_for("auth.dashboard"))

    # Check depth before allowing subtask addition
    if parent_task.get_depth() >= 3:
        flash("Cannot add more than 3 levels of subtasks.")
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        # Check if 'title' is present in form data to avoid KeyError
        title = request.form.get("title")
        if not title:
            flash("Title is required to add a subtask.")
            return redirect(url_for("auth.add_subtask", task_id=task_id))

        # Get the status, defaulting to the parent task's status if not provided
        status = request.form.get("status", parent_task.status)

        # Create the new subtask
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

    # Render the add_task form for GET requests
    return render_template(
        "add_task.html", parent_task=parent_task, task_group=parent_task.task_group
    )


@auth.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    # Find the task and ensure it belongs to the current user
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        flash("Task not found or you don't have permission.")
        return redirect(url_for("auth.dashboard"))

    # Delete the task
    db.session.delete(task)
    db.session.commit()

    flash("Task deleted successfully.")
    return redirect(url_for("auth.dashboard"))


@auth.route("/move_task/<int:task_id>", methods=["POST"])
@login_required
def move_task(task_id):
    data = request.get_json()
    new_group_id = data.get("new_group_id")

    # Fetch the task and ensure it belongs to the user
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({"error": "Task not found or you don't have permission."}), 403

    # Update the task's group
    task.task_group_id = new_group_id
    db.session.commit()

    return jsonify({"success": "Task moved successfully."})


# Logout route
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/delete_task_group/<int:group_id>", methods=["POST"])
@login_required
def delete_task_group(group_id):
    # Fetch the task group and ensure it belongs to the user
    task_group = TaskGroup.query.filter_by(id=group_id, user_id=current_user.id).first()
    if not task_group:
        flash("Task group not found or you don't have permission.")
        return redirect(url_for("auth.dashboard"))

    # Optional: Delete all tasks associated with this task group
    Task.query.filter_by(task_group_id=group_id).delete()

    # Delete the task group
    db.session.delete(task_group)
    db.session.commit()

    flash("Task group deleted successfully.")
    return redirect(url_for("auth.dashboard"))
