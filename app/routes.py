from flask import (
    Blueprint,
    render_template,
)  # Import Blueprint to organize routes, render_template for HTML rendering
from flask_login import (
    login_required,
)  # Import login_required decorator to protect routes

# Create a Blueprint named "main" for main routes
main = Blueprint("main", __name__)


# Dashboard route that displays the user's task groups
# Protected by @login_required so only logged-in users can access this route
@main.route("/")
@login_required
def dashboard():
    # Query the database for all task groups associated with the current user
    task_groups = TaskGroup.query.filter_by(user_id=current_user.id).all()

    # Render the "dashboard.html" template, passing in the user's task groups
    return render_template("dashboard.html", task_groups=task_groups)
