# Todo List App

## Description

The Todo List App is a web application that enables users to create and manage hierarchical todo lists with up to three levels of depth. Users can create multiple lists (task groups), each containing tasks that can have sub-tasks and sub-sub-tasks. This structure allows users to organize tasks efficiently, focus on the most important ones, and hide details until they are ready to address them.

## Features

- **User Registration and Authentication**: Secure user accounts where each user can only see and modify their own tasks.
- **Create and Delete Lists and Tasks**: Users can manage their lists and tasks, including adding new tasks and deleting existing ones.
- **Hierarchical Structure**: Supports tasks nested up to three levels deep (task → sub-task → sub-sub-task).
- **Collapse and Expand Tasks**: Users can hide or show sub-tasks to focus on specific levels of their todo list.
- **Task Completion**: Mark tasks as complete by deleting them with a click of a button.
- **Move Tasks Between Lists**: Users can move top-level tasks between different lists by dragging them.
- **Persistent Data Storage**: All data is stored in a durable SQLite database using SQLAlchemy.
- **Unit Testing**: Includes a suite of unit tests to ensure code reliability and functionality.

## Installation

**Before you begin**, ensure that you have **Python 3** installed on your system.

1. **Download the Project**

   Download the ZIP file of the project and extract it to your desired directory.

2. **Navigate to the Project Directory**

   ```bash
   cd path_to_project_directory
   ```

3. **Create a Virtual Environment**

   - **macOS/Linux:**

     ```bash
     python3 -m venv venv
     ```

   - **Windows:**

     ```bash
     python -m venv venv
     ```

4. **Activate the Virtual Environment**

   - **macOS/Linux:**

     ```bash
     source venv/bin/activate
     ```

   - **Windows (Command Prompt):**

     ```bash
     venv\Scripts\activate.bat
     ```

   - **Windows (PowerShell):**

     ```powershell
     venv\Scripts\Activate.ps1
     ```

5. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

6. **Run the Application**

   ```bash
   python app.py
   ```

7. **Access the Application**

   Open your web browser and navigate to [http://localhost:5000](http://localhost:5000) to start using the app.

**Note**: Ensure that the `venv` directory is **not** included in your ZIP file when submitting the assignment.

## Project Structure

```
app
├── __init__.py            # Initializes the Flask app
├── auth.py                # Authentication routes and logic
├── models.py              # Database models (User, Task, TaskGroup)
├── routes.py              # Application routes and view functions
├── static
│   ├── scripts.js         # JavaScript functions for interactivity
│   └── styles.css         # CSS styles for the application
├── templates              # HTML templates for rendering views
│   ├── add_item.html
│   ├── add_task.html
│   ├── base.html          # Base template extended by other templates
│   ├── create_list.html
│   ├── create_task_group.html
│   ├── dashboard.html     # User dashboard after login
│   ├── edit_item.html
│   ├── edit_list.html
│   ├── item.html
│   ├── list.html
│   ├── login.html         # User login page
│   ├── move_item.html
│   ├── register.html      # User registration page
│   ├── task_groups.html
│   └── task_item.html
├── tests                  # Unit tests for the application
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_task.py
│   ├── test_task_movement.py
│   ├── test_task_persistence.py
│   └── test_task_visibility.py
├── utils.py               # Utility functions (e.g., CSRF token generation)
app.py                     # Entry point to run the Flask app
config.py                  # Configuration settings for the app
requirements.txt           # Python dependencies
```

## Usage Guide

### User Registration and Login

- **Register**: Navigate to the registration page (`/register`) to create a new user account.
- **Login**: After registering, log in through the login page (`/login`).

### Creating Task Groups and Tasks

- **Create a Task Group**: From the dashboard, click on **"Create New List"** to organize your tasks into different categories.
- **Add Tasks**: Within a task group, click on **"Add New Task"** to add a top-level task.
- **Add Subtasks**: For any task, click **"Add Subtask"** next to it to create a sub-task.
- **Task Hierarchy**: Tasks can be nested up to three levels deep:
  - **Task**
    - **Sub-task**
      - **Sub-sub-task**

### Managing Tasks

- **Collapse/Expand Tasks**: Click on a task's title to toggle the visibility of its sub-tasks.
- **Mark Tasks as Complete**: Click the **"Complete"** button next to a task to delete it upon completion.
- **Move Tasks Between Lists**: Drag and drop top-level tasks to move them between different task groups.

### Deleting Tasks and Lists

- **Delete Tasks**: Click the **"Delete"** button next to a task to remove it.
- **Delete Lists**: On the dashboard, you can delete an entire task group if needed.

## Testing

The application includes a suite of unit tests to ensure functionality and catch regressions.

### Running Tests

1. **Activate the Virtual Environment**

   - **macOS/Linux:**

     ```bash
     source venv/bin/activate
     ```

   - **Windows:**

     ```bash
     venv\Scripts\activate.bat
     ```

2. **Run Tests Using Pytest**

   ```bash
   pytest -s app/tests/
   ```

   The `-s` flag is used to display print statements during testing.

### Test Coverage

- **Authentication Tests** (`test_auth.py`): Tests user registration and login functionalities.
- **Task Tests** (`test_task.py`): Tests task group creation and task addition.
- **Task Movement Tests** (`test_task_movement.py`): Tests moving tasks between task groups.
- **Task Persistence Tests** (`test_task_persistence.py`): Tests data persistence in the database.
- **Task Visibility Tests** (`test_task_visibility.py`): Tests collapsing and expanding of tasks.

## Demo Video

A demo video showcasing the application's features is available (https://www.loom.com/share/8262d1d9c1514ddfba023a18068da9ad?sid=4e35f27b-0032-47a9-a020-6bd5036b09b5).

## Assignment Compliance

### MVP Requirements

1. **Multiple Users**: Implemented. Users can register and only see their own tasks.
2. **User Task Isolation**: Implemented. Users cannot see or modify other users' tasks.
3. **Forgot Password Functionality**: Not required and not implemented.
4. **Task Completion**: Implemented. Users can mark tasks as complete by deleting them.
5. **Collapse/Expand Tasks**: Implemented. Users can collapse and expand tasks to hide or show sub-tasks.
6. **Move Top-Level Tasks**: Implemented. Users can move top-level tasks between different lists by dragging.
7. **Durable Data Storage**: Implemented using SQLite with SQLAlchemy ORM.

### Extensions

1. **Infinite Nesting**: Not implemented. The app limits nesting to three levels, adhering to the assignment guidelines.
2. **Arbitrary Task Movement**: Not implemented. Only top-level task movement is supported.
3. **Unit Testing**: Implemented. A comprehensive suite of unit tests ensures code reliability.

## Code Comments and Documentation

The codebase includes detailed comments that explain the purpose and functionality of different sections. This aids in understanding the application's flow and facilitates future maintenance.

## Best Practices Followed

- **Virtual Environment Exclusion**: The `venv` directory is excluded from the ZIP file to ensure portability.
- **Code Readability**: Descriptive variable and function names are used throughout the code.
- **Modularity**: The application is organized logically with separate modules for routes, models, templates, and utilities.
- **Security**: Implemented CSRF protection and followed best practices for user authentication.

## Acknowledgments

- **Instructor and TAs**: For guidance and support throughout the project.
- **OpenAI's ChatGPT and GitHub Copilot**: For assistance in code generation, debugging, and documentation.

## Additional Notes

- **Assignment Instructions**: The application meets all the MVP requirements specified in the assignment. The depth limitation of three levels is maintained to ensure usability.
- **Modifications**: Adjustments were made to allow users to delete tasks as a way of marking them complete and to move tasks between lists via drag-and-drop functionality.

---

_This project was developed as part of an assignment to create a hierarchical todo list app with specific requirements provided by the course instructor._
