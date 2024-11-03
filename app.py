from app import create_app  # Import the app factory function

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
