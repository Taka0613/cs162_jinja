// Function to toggle the display of child items with a smooth slide transition
function toggleChildren(event) {
    const button = event.target;  // Get the button that triggered the event
    const parentLi = button.closest('li');  // Find the closest list item (li) to the button
    const childUl = parentLi.querySelector('ul');  // Get the ul element containing child items

    if (!childUl) return;  // Exit if there are no child items

    // Toggle visibility of child items and update button text
    if (childUl.style.display === 'none' || childUl.style.display === '') {
        childUl.style.display = 'block';  // Show child items
        button.textContent = '[-]';  // Change button text to indicate expanded state
    } else {
        childUl.style.display = 'none';  // Hide child items
        button.textContent = '[+]';  // Change button text to indicate collapsed state
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
    event.preventDefault();  // Prevent default handling of the drop event
    const taskId = event.dataTransfer.getData("taskId");  // Retrieve the dragged task ID

    // Get CSRF token dynamically from meta tag for security
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Send AJAX request to move the task to the new group
    fetch(`/move_task/${taskId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken  // Include CSRF token in headers
        },
        body: JSON.stringify({ new_group_id: newGroupId })  // Send the new group ID in the request body
    })
    .then(response => {
        if (response.ok) {
            location.reload();  // Reload the page to reflect the moved task
        } else {
            response.json().then(data => {
                alert(data.error || "Failed to move task.");  // Show error message if the request fails
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("An error occurred.");  // Log and display an error message if the fetch fails
    });
}

// Attach event listeners after the DOM content is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Attach click event to toggler buttons for collapsing/expanding child items
    const togglerButtons = document.querySelectorAll('.toggler');
    togglerButtons.forEach(button => {
        button.addEventListener('click', toggleChildren);
    });

    // Add drag event listeners to each draggable task
    const draggableTasks = document.querySelectorAll('[draggable="true"]');
    draggableTasks.forEach(task => {
        task.addEventListener('dragstart', (event) => {
            const taskId = task.getAttribute('data-task-id');  // Get task ID from data attribute
            drag(event, taskId);  // Call drag function with event and task ID
        });
    });

    // Add drop event listeners to each task group
    const taskGroups = document.querySelectorAll('.task-group');
    taskGroups.forEach(group => {
        const groupId = group.getAttribute('data-group-id');  // Get group ID from data attribute
        group.addEventListener('dragover', allowDrop);  // Allow items to be dropped in this group
        group.addEventListener('drop', (event) => drop(event, groupId));  // Handle drop and move task
    });
});


