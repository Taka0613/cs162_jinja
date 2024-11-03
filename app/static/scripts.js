// Function to toggle the display of child items with a smooth slide transition
function toggleChildren(event) {
    const button = event.target;
    const parentLi = button.closest('li');
    const childUl = parentLi.querySelector('ul');

    if (!childUl) return;  // If no children, exit function

    // Toggle visibility with a smooth transition
    if (childUl.style.display === 'none' || childUl.style.display === '') {
        childUl.style.display = 'block';
        button.textContent = '[-]';
    } else {
        childUl.style.display = 'none';
        button.textContent = '[+]';
    }
}

// Enable drag-and-drop functionality for moving tasks
function allowDrop(event) {
    event.preventDefault();  // Allow the drop by preventing default behavior
}

function drag(event, taskId) {
    event.dataTransfer.setData("taskId", taskId);  // Pass the task ID during drag
}

function drop(event, newGroupId) {
    event.preventDefault();
    const taskId = event.dataTransfer.getData("taskId");

    // Get CSRF token dynamically
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Send AJAX request to move the task to the new list
    fetch(`/move_task/${taskId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken  // CSRF token for security
        },
        body: JSON.stringify({ new_group_id: newGroupId })  // Send new group ID
    })
    .then(response => {
        if (response.ok) {
            location.reload();  // Reload page to reflect changes
        } else {
            response.json().then(data => {
                alert(data.error || "Failed to move task.");
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("An error occurred.");
    });
}

// Attach event listeners after the DOM content is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Toggle child items visibility
    const togglerButtons = document.querySelectorAll('.toggler');
    togglerButtons.forEach(button => {
        button.addEventListener('click', toggleChildren);
    });

    // Add drag event listeners
    const draggableTasks = document.querySelectorAll('[draggable="true"]');
    draggableTasks.forEach(task => {
        task.addEventListener('dragstart', (event) => {
            const taskId = task.getAttribute('data-task-id');
            drag(event, taskId);
        });
    });

    // Add drop event listeners to task groups
    const taskGroups = document.querySelectorAll('.task-group');
    taskGroups.forEach(group => {
        const groupId = group.getAttribute('data-group-id');
        group.addEventListener('dragover', allowDrop);
        group.addEventListener('drop', (event) => drop(event, groupId));
    });
});

