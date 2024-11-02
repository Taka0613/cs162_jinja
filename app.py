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
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = (
    "42e76d8053493a28cc90a625d2315d2666da0c445351d01c5ddb8ba8aaa71f55"  # Replace with a secure secret key
)
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
    lists = db.relationship("List", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    items = db.relationship("Item", backref="list", lazy=True)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey("list.id"), nullable=False)
    parent_item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    children = db.relationship(
        "Item", backref=db.backref("parent", remote_side=[id]), lazy=True
    )


# User loader callback for Flask-Login
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


# Dashboard showing lists
@app.route("/")
@login_required
def dashboard():
    lists = List.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", lists=lists)


# Create a new list
@app.route("/lists/new", methods=["GET", "POST"])
@login_required
def create_list():
    if request.method == "POST":
        title = request.form["title"]
        new_list = List(title=title, user_id=current_user.id)
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for("dashboard"))
    return render_template("create_list.html")


# Edit a list
@app.route("/lists/<int:list_id>/edit", methods=["GET", "POST"])
@login_required
def edit_list(list_id):
    list = List.query.get_or_404(list_id)
    if list.user_id != current_user.id:
        flash("You do not have permission to edit this list.")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        title = request.form["title"]
        list.title = title
        db.session.commit()
        return redirect(url_for("dashboard"))
    return render_template("edit_list.html", list=list)


# Delete a list
@app.route("/lists/<int:list_id>/delete", methods=["POST"])
@login_required
def delete_list(list_id):
    list = List.query.get_or_404(list_id)
    if list.user_id != current_user.id:
        flash("You do not have permission to delete this list.")
        return redirect(url_for("dashboard"))
    db.session.delete(list)
    db.session.commit()
    return redirect(url_for("dashboard"))


# View items in a list
@app.route("/lists/<int:list_id>")
@login_required
def view_list(list_id):
    list = List.query.get_or_404(list_id)
    if list.user_id != current_user.id:
        flash("You do not have permission to view this list.")
        return redirect(url_for("dashboard"))
    items = Item.query.filter_by(list_id=list_id, parent_item_id=None).all()
    return render_template("list.html", list=list, items=items)


# Add an item to a list
@app.route("/lists/<int:list_id>/items/new", methods=["GET", "POST"])
@login_required
def add_item(list_id):
    list = List.query.get_or_404(list_id)
    if list.user_id != current_user.id:
        flash("You do not have permission to add items to this list.")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        title = request.form["title"]
        parent_item_id = request.form.get("parent_item_id")
        if parent_item_id:
            parent_item_id = int(parent_item_id)
        else:
            parent_item_id = None
        new_item = Item(title=title, list_id=list_id, parent_item_id=parent_item_id)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for("view_list", list_id=list_id))
    parent_items = Item.query.filter_by(list_id=list_id, parent_item_id=None).all()
    return render_template("add_item.html", list=list, parent_items=parent_items)


# Edit an item
@app.route("/items/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    list = item.list
    if list.user_id != current_user.id:
        flash("You do not have permission to edit this item.")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        item.title = request.form["title"]
        db.session.commit()
        return redirect(url_for("view_list", list_id=list.id))
    return render_template("edit_item.html", item=item)


# Delete an item and its sub-items
@app.route("/items/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    list = item.list
    if list.user_id != current_user.id:
        flash("You do not have permission to delete this item.")
        return redirect(url_for("dashboard"))
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("view_list", list_id=list.id))


# Move a top-level item to a different list
@app.route("/items/<int:item_id>/move", methods=["GET", "POST"])
@login_required
def move_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.parent_item_id is not None:
        flash("Only top-level items can be moved.")
        return redirect(url_for("view_list", list_id=item.list_id))
    if item.list.user_id != current_user.id:
        flash("You do not have permission to move this item.")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        new_list_id = request.form["new_list_id"]
        new_list = List.query.get_or_404(new_list_id)
        if new_list.user_id != current_user.id:
            flash("You do not have permission to move items to this list.")
            return redirect(url_for("dashboard"))
        item.list_id = new_list_id
        db.session.commit()
        return redirect(url_for("view_list", list_id=new_list_id))
    lists = List.query.filter_by(user_id=current_user.id).all()
    return render_template("move_item.html", item=item, lists=lists)


# Toggle completion status
@app.route("/items/<int:item_id>/complete", methods=["POST"])
@login_required
def complete_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.list.user_id != current_user.id:
        flash("You do not have permission to complete this item.")
        return redirect(url_for("dashboard"))
    item.is_completed = not item.is_completed
    db.session.commit()
    return redirect(url_for("view_list", list_id=item.list_id))


# Run the app
if __name__ == "__main__":
    # Create database tables if they don't exist
    db.create_all()
    app.run(debug=True)
