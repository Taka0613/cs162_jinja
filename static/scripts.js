// static/scripts.js

// Function to toggle the display of child items
function toggleChildren(event) {
    const button = event.target;
    const parentLi = button.closest('li');
    const childUl = parentLi.querySelector('ul');

    if (childUl.style.display === 'none') {
        childUl.style.display = 'block';
        button.textContent = '[-]';
    } else {
        childUl.style.display = 'none';
        button.textContent = '[+]';
    }
}

// Attach event listeners after the DOM content is loaded
document.addEventListener('DOMContentLoaded', function() {
    const togglerButtons = document.querySelectorAll('.toggler');
    togglerButtons.forEach(function(button) {
        button.addEventListener('click', toggleChildren);
    });
});
