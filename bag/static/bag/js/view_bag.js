/**
 * Sets the delete link dynamically when the delete confirmation modal is shown.
 *
 * - Captures the delete URL from the clicked trigger button.
 * - Updates the confirmation button inside the modal with the correct URL.
 */
document.addEventListener('DOMContentLoaded', function () {
    const confirmModal = document.getElementById('confirmRemoveModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');

    confirmModal.addEventListener('show.bs.modal', function (event) {
        const triggerButton = event.relatedTarget;
        const deleteUrl = triggerButton.getAttribute('data-href');

        confirmDeleteBtn.setAttribute('href', deleteUrl);
    });
});

/**
 * Validates input in a form before sending an HTMX request and prevents the request
 * if the validation fails.
 *
 * - Checks if the input value is a valid quantity within the acceptable range (1–99).
 * - Displays an error message and disables the checkout button if validation fails.
 * - Removes validation errors and enables the checkout button if input is valid.
 *
 * @event htmx:beforeRequest Fired before HTMX sends a request.
 * @param {Object} event HTMX event object containing the request context.
 */
document.addEventListener('htmx:beforeRequest', function (event) {
    const form = event.target.closest('form.update-form');
    if (!form) return;

    const processToCheckoutBtn = document.getElementById('to-checkout-btn');

    const input = form.querySelector('input[name="quantity"]');
    const value = input.value.trim();

    // 1. Check for empty string
    if (value === '') {
        isValid = false;
    }
    // 2. Check for valid numeric format and range
    else {
        // Allow only numbers (no decimals, no leading zeros unless single zero)
        const isNumeric = /^(0|[1-9]\d*)$/.test(value);
        const numericValue = parseInt(value, 10);

        isValid =
            isNumeric &&
            !isNaN(numericValue) &&
            numericValue >= 1 &&
            numericValue <= 99;
    }

    if (!isValid) {
        // Stop HTMX request if input is invalid
        event.preventDefault();
        input.classList.add('is-invalid');
        const errorMessage = form.querySelector('.bag-error-message');
        if (errorMessage) {
            errorMessage.classList.remove('d-none');
        }
        processToCheckoutBtn.classList.add('disabled-link');
    } else {
        // Remove 'is-invalid' class if input is valid
        input.classList.remove('is-invalid');
        const errorMessage = form.querySelector('.bag-error-message');
        if (errorMessage) {
            errorMessage.classList.add('d-none');
        }
        // Enable the checkout button
        processToCheckoutBtn.classList.remove('disabled-link');
    }
});

/**
 * Revalidates and updates dynamically loaded inputs after HTMX swaps content into the DOM.
 *
 * - Validates quantity inputs to ensure the value is within the acceptable range (1–99).
 * - Displays or hides error messages and adds or removes the `is-invalid` class based on
 *   validation results.
 * - Attaches event listeners to new inputs after HTMX updates the DOM.
 *
 * @event htmx:afterSwap Fired after HTMX swaps new content into the DOM.
 * @param {Object} event HTMX event object containing the swap context.
 */
document.addEventListener('htmx:afterSwap', function (event) {
    // Validate each quantity input within its form
    function validateInput(input) {
        const form = input.closest('form');
        const errorMessage = form.querySelector('.bag-error-message');
        const value = input.value.trim();

        // 1. Check for empty string
        if (value === '') {
            isValid = false;
        }
        // 2. Check for valid numeric format and range
        else {
            // Allow only numbers (no decimals, no leading zeros unless single zero)
            const isNumeric = /^(0|[1-9]\d*)$/.test(value);
            const numericValue = parseInt(value, 10);

            isValid =
                isNumeric &&
                !isNaN(numericValue) &&
                numericValue >= 1 &&
                numericValue <= 99;
        }

        input.classList.toggle('is-invalid', !isValid);
        errorMessage.classList.toggle('d-none', isValid);
    }

    // Check all inputs on initial load and after swaps
    function checkAllInputs() {
        document.querySelectorAll('input[name="quantity"]').forEach((input) => {
            validateInput(input);
        });
    }

    // Attach event listeners to each input
    document.querySelectorAll('input[name="quantity"]').forEach((input) => {
        input.addEventListener('blur', () => validateInput(input));
        input.addEventListener('input', () => {
            // Validate on input for real-time feedback but don't show error yet
            const value = parseInt(input.value.trim(), 10);
            input.classList.toggle(
                'is-invalid',
                !isNaN(value) && (value < 1 || value > 99)
            );
        });
        input.addEventListener('change', () => validateInput(input));
    });

    checkAllInputs(); // Initial validation
});
