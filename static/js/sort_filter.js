/**
 * Handles real-time validation and form submission for filtering products
 * based on a price range, ensuring min/max logic is respected.
 */
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('filter-form');
    const submitBtn = document.getElementById('filter-submit-btn');
    const minInput = document.getElementById('min_price');
    const maxInput = document.getElementById('max_price');
    const errorMessage = document.getElementById('price-error-message');

    /**
     * Validates the minimum and maximum price inputs, displaying
     * an error message and disabling the submit button if invalid.
     */
    function validatePriceRange() {
        const minStr = minInput.value.trim();
        const maxStr = maxInput.value.trim();
        // Allows numbers with optional .xx but blocks symbols
        const numericRegex = /^(?!0+$)(?!0*\.0*$)\d+(?:\.\d{1,2})?$/;
        let isValid = true;

        errorMessage.textContent = '';
        errorMessage.classList.add('d-none');
        submitBtn.classList.remove('disabled-link');

        // Validate Min Price
        if (minStr !== '') {
            if (!numericRegex.test(minStr)) {
                errorMessage.textContent =
                    'Min price must be a positive number (e.g., 10 or 10.99)';
                isValid = false;
            } else {
                const min = parseFloat(minStr);
                if (min <= 0) {
                    errorMessage.textContent =
                        'Min price must be greater than 0';
                    isValid = false;
                }
            }
        }

        // Validate Max Price (only check if min is valid)
        if (isValid && maxStr !== '') {
            if (!numericRegex.test(maxStr)) {
                errorMessage.textContent =
                    'Max price must be a positive number (e.g., 100 or 100.99)';
                isValid = false;
            } else {
                const max = parseFloat(maxStr);
                if (max <= 0) {
                    errorMessage.textContent =
                        'Max price must be greater than 0';
                    isValid = false;
                }
            }
        }

        // Compare prices if both are valid
        if (isValid && minStr && maxStr) {
            const min = parseFloat(minStr);
            const max = parseFloat(maxStr);

            if (min > max) {
                errorMessage.textContent =
                    'Min price cannot be greater than Max price';
                isValid = false;
            }
        }

        if (!isValid) {
            errorMessage.classList.remove('d-none');
            submitBtn.classList.add('disabled-link');
        }

        return isValid;
    }

    // Listen for real-time input changes
    minInput.addEventListener('input', validatePriceRange);
    maxInput.addEventListener('input', validatePriceRange);

    // Final validation on submit
    form.addEventListener('submit', function (e) {
        if (!validatePriceRange()) {
            e.preventDefault();
        }
    });

    // Initial state
    validatePriceRange();

    const filterForm = document.getElementById('filter-form');
    filterForm.addEventListener('submit', function (event) {
        const hiddenSearch = document.getElementById('search-input-hidden');
        const params = new URLSearchParams(window.location.search);
        hiddenSearch.value = params.get('search_query') || '';
    });
});
