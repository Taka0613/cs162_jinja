# app/routes.py
from flask import Blueprint, render_template
from flask_login import login_required

main = Blueprint("main", __name__)


@main.route("/")
@login_required
def dashboard():
    task_groups = TaskGroup.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", task_groups=task_groups)
