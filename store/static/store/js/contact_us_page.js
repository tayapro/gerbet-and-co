/**
 * Validates the Contact Us form on submission, ensuring that
 * name, email, and message fields meet required criteria.
 * Displays error messages and prevents submission if invalid.
 */
document.addEventListener('DOMContentLoaded', function () {
    document
        .getElementById('contact-form')
        .addEventListener('submit', function (event) {
            let isValid = true;

            // Clear previous error messages
            document.getElementById('id_name_error').innerHTML = '';
            document.getElementById('id_email_error').innerHTML = '';
            document.getElementById('id_message_error').innerHTML = '';

            // Validate Name
            const nameField = document.getElementById('id_name').value.trim();
            const hasLetters = /[a-zA-Z]/; // Regex to check for at least one letter
            if (nameField === '') {
                document.getElementById('id_name_error').innerHTML =
                    'Please enter your name.';
                isValid = false;
            } else if (nameField.length > 100) {
                document.getElementById('id_name_error').innerHTML =
                    'Name cannot exceed 100 characters.';
                isValid = false;
            } else if (nameField.length < 2) {
                document.getElementById('id_name_error').innerHTML =
                    'Name must be at least 2 characters long.';
                isValid = false;
            } else if (!hasLetters.test(nameField)) {
                document.getElementById('id_name_error').innerHTML =
                    'Name must contain at least one letter.';
                isValid = false;
            }

            // Validate Email
            const emailField = document.getElementById('id_email').value.trim();
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // Basic email format
            if (emailField === '') {
                document.getElementById('id_email_error').innerHTML =
                    'Please enter your email address.';
                isValid = false;
            } else if (!emailPattern.test(emailField)) {
                document.getElementById('id_email_error').innerHTML =
                    'Please enter a valid email address.';
                isValid = false;
            }

            // Validate Message
            const messageField = document
                .getElementById('id_message')
                .value.trim();
            if (messageField === '') {
                document.getElementById('id_message_error').innerHTML =
                    'Please enter your message.';
                isValid = false;
            } else if (messageField.length < 10) {
                document.getElementById('id_message_error').innerHTML =
                    'Message must be at least 10 characters long.';
                isValid = false;
            } else if (!hasLetters.test(messageField)) {
                document.getElementById('id_message_error').innerHTML =
                    'Message must contain at least one letter.';
                isValid = false;
            }

            // Prevent submission if validation fails
            if (!isValid) {
                event.preventDefault();
            }
        });
});
