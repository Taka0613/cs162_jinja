from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
    UserMixin,
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


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

    # Use a unique backref name, like `task_group_tasks`
    tasks = db.relationship("Task", backref="parent_group", lazy=True)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="To Do")
    is_completed = db.Column(db.Boolean, default=False)
    task_group_id = db.Column(
        db.Integer, db.ForeignKey("task_group.id"), nullable=False
    )

    # Task now references `parent_group` instead of `task_group`
    parent_task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=True)
    subtasks = db.relationship(
        "Task", backref=db.backref("parent_task", remote_side=[id]), lazy=True
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="tasks")

    @property
    def get_depth(self):
        depth = 1
        parent = self.parent_task
        while parent:
            depth += 1
            parent = parent.parent_task
        return depth


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Routes for authentication
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for("register"))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/create_task_group", methods=["GET", "POST"])
@login_required
def create_task_group():
    if request.method == "POST":
        title = request.form["title"]
        # Check if the user already has a list with the same name
        existing_group = TaskGroup.query.filter_by(
            title=title, user_id=current_user.id
        ).first()
        if existing_group:
            flash("A list with this name already exists.")
            return redirect(url_for("create_task_group"))

        new_group = TaskGroup(title=title, user_id=current_user.id)
        db.session.add(new_group)
        db.session.commit()
        flash("New task group created successfully.")
        return redirect(url_for("dashboard"))

    return render_template("create_task_group.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def dashboard():
    task_groups = TaskGroup.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", task_groups=task_groups)


@app.route("/task_groups/<int:group_id>/add_task", methods=["GET", "POST"])
@login_required
def add_task(group_id):
    task_group = TaskGroup.query.filter_by(id=group_id, user_id=current_user.id).first()
    if not task_group:
        flash("Task group not found or you don't have permission.")
        return redirect(url_for("dashboard"))

    parent_task_id = request.args.get("parent_task_id")
    parent_task = (
        Task.query.filter_by(id=parent_task_id, user_id=current_user.id).first()
        if parent_task_id
        else None
    )

    if request.method == "POST":
        title = request.form["title"]
        status = request.form.get("status", "To Do")
        new_task = Task(
            title=title,
            status=status,
            parent_task_id=parent_task.id if parent_task else None,
            task_group_id=group_id,
            user_id=current_user.id,
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template(
        "add_task.html", task_group=task_group, parent_task=parent_task
    )


@app.route("/tasks/<int:task_id>/add_subtask", methods=["GET", "POST"])
@login_required
def add_subtask(task_id):
    parent_task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not parent_task:
        flash("Parent task not found or you don't have permission.")
        return redirect(url_for("dashboard"))

    # Retrieve the task group from the parent task
    task_group = parent_task.parent_group

    # Check the depth of the parent task
    if parent_task.get_depth >= 3:
        flash("Cannot add more than 3 levels of subtasks.")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        title = request.form["title"]
        status = request.form.get("status", parent_task.status)
        new_task = Task(
            title=title,
            status=status,
            parent_task_id=task_id,
            task_group_id=parent_task.task_group_id,
            user_id=current_user.id,
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("dashboard"))

    # Pass task_group to the template context
    return render_template(
        "add_task.html", task_group=task_group, parent_task=parent_task
    )


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        flash("Task not found or you don't have permission to delete it.")
        return redirect(url_for("dashboard"))

    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("dashboard"))


# Initialize database tables if they don’t exist
@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
