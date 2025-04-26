document
    .getElementById('contact-form')
    .addEventListener('submit', function (event) {
        let isValid = true

        // Clear previous error messages
        document.getElementById('id_name_error').innerHTML = ''
        document.getElementById('id_email_error').innerHTML = ''
        document.getElementById('id_message_error').innerHTML = ''

        // Validate Name
        const nameField = document.getElementById('id_name')
        if (nameField.value.trim() === '') {
            document.getElementById('id_name_error').innerHTML =
                'Please enter your name.'
            isValid = false
        } else if (nameField.value.length > 100) {
            document.getElementById('id_name_error').innerHTML =
                'Name cannot exceed 100 characters.'
            isValid = false
        }

        // Validate Email
        const emailField = document.getElementById('id_email')
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/ // Basic email format
        if (emailField.value.trim() === '') {
            document.getElementById('id_email_error').innerHTML =
                'Please enter your email address.'
            isValid = false
        } else if (!emailPattern.test(emailField.value.trim())) {
            document.getElementById('id_email_error').innerHTML =
                'Please enter a valid email address.'
            isValid = false
        }

        // Validate Message
        const messageField = document.getElementById('id_message')
        if (messageField.value.trim() === '') {
            document.getElementById('id_message_error').innerHTML =
                'Please enter your message.'
            isValid = false
        }

        // Prevent submission if validation fails
        if (!isValid) {
            event.preventDefault()
        }
    })
