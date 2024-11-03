from app import (
    create_app,
)  # Import the app factory function from the app package to initialize the application

# Create an instance of the application by calling the create_app() function
# This function sets up the configuration, routes, and other necessary parts of the app
app = create_app()

# If this script is run directly (not imported as a module), start the application
# The app will run in debug mode, which provides detailed error messages and auto-reload functionality for development
if __name__ == "__main__":
    app.run(debug=True)
