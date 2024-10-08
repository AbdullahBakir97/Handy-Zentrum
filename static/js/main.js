// General purpose JavaScript for interaction

// Function to handle modal for confirmations (like order cancellation)
document.addEventListener('DOMContentLoaded', () => {
    const cancelButtons = document.querySelectorAll('.btn-danger');

    cancelButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            const confirmation = confirm('Are you sure you want to cancel this order?');
            if (!confirmation) {
                e.preventDefault();
            }
        });
    });
});

// Example function for dynamic notifications (for future extension)
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerText = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}
