// notifications.js

// Make sure SweetAlert2 is included in your template separately
document.addEventListener("DOMContentLoaded", function () {
    const messages = JSON.parse(document.getElementById("django-messages").textContent);

    messages.forEach(msg => {
        Swal.fire({
            icon: msg.tags === 'error' ? 'error' : 'success',
            title: msg.tags === 'error' ? 'Error' : 'Success',
            text: msg.message,
            confirmButtonText: 'OK'
        });
    });
});
