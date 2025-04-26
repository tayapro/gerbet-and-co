/**
 * Validate a required form field by checking if it is empty.
 *
 * Adds or removes validation error messages and styles dynamically.
 *
 * @param {HTMLElement} field - The form field element to validate.
 * @returns {boolean} - True if the field is valid, otherwise false.
 */
function validateField(field) {
    const errorMsg = 'This field is required';
    const parent = field.closest('.form-group, .form-control, div');

    if (!field.value.trim()) {
        field.classList.add('is-invalid');
        field.setAttribute('title', errorMsg);
        if (
            !field.nextElementSibling ||
            !field.nextElementSibling.classList.contains('invalid-feedback')
        ) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback d-block';
            errorDiv.innerText = errorMsg;
            field.parentNode.insertBefore(errorDiv, field.nextSibling);
        }
        return false;
    } else {
        field.classList.remove('is-invalid');
        field.removeAttribute('title');
        if (
            field.nextElementSibling &&
            field.nextElementSibling.classList.contains('invalid-feedback')
        ) {
            field.nextElementSibling.remove();
        }
        return true;
    }
}

/**
 * Initialize form validation on the address form.
 *
 * Adds real-time validation on input and blur events,
 * and prevents form submission if validation fails.
 */
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('address-form');
    const requiredFields = [
        document.getElementById('id_street_address1'),
        document.getElementById('id_town_or_city'),
        document.getElementById('id_postcode'),
        document.getElementById('id_phone_number'),
        document.getElementById('id_country'),
    ].filter((field) => field !== null);

    // Add listener to validate each required field
    requiredFields.forEach((field) => {
        field.addEventListener('input', () => validateField(field));
        field.addEventListener('blur', () => validateField(field));
    });

    form.addEventListener('submit', function (e) {
        let formIsValid = true;

        requiredFields.forEach((field) => {
            if (!validateField(field)) {
                formIsValid = false;
            }
        });

        if (!formIsValid) {
            e.preventDefault();
        }
    });
});
