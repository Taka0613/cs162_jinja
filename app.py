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


# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    task_groups = db.relationship("TaskGroup", backref="user", lazy=True)

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
    status = db.Column(db.String(20), nullable=False, default="To Do")  # Status field
    is_completed = db.Column(db.Boolean, default=False)
    task_group_id = db.Column(
        db.Integer,
        db.ForeignKey("task_group.id"),
        nullable=True,  # Set nullable=True here
    )
    parent_task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=True)
    subtasks = db.relationship(
        "Task", backref=db.backref("parent_task", remote_side=[id]), lazy=True
    )


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


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def dashboard():
    # Retrieve tasks categorized by status
    categorized_tasks = {
        "To Do": Task.query.filter_by(status="To Do", task_group_id=None).all(),
        "In Progress": Task.query.filter_by(
            status="In Progress", task_group_id=None
        ).all(),
        "Done": Task.query.filter_by(status="Done", task_group_id=None).all(),
    }
    return render_template("dashboard.html", categorized_tasks=categorized_tasks)


@app.route("/add_task/<status>", methods=["GET", "POST"])
@login_required
def add_task(status):
    if request.method == "POST":
        title = request.form["title"]
        # Save the new task with the chosen status
        new_task = Task(
            title=title,
            status=status,
            task_group_id=None,  # Adjust if task groups are needed
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template("add_task.html", status=status)


# Delete a task
@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("dashboard"))


# Initialize database tables if they don’t exist
@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
