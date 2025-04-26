/**
 * Initializes the rating modal behavior, setting dynamic form actions
 * and resetting stars when canceled.
 */
document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('ratingModal');
    const ratingForm = document.getElementById('rating-form');

    /**
     * Sets the form action dynamically when the rating modal is shown.
     */
    modal.addEventListener('show.bs.modal', function (event) {
        const trigger = event.relatedTarget;
        if (!trigger) return;

        const productId = trigger.getAttribute('data-product-id');

        // Update the form action dynamically
        const newAction = `/products/rating/${productId}/`;
        ratingForm.setAttribute('action', newAction);
    });

    const stars = document.querySelectorAll('.star-btn');
    const ratingInput = document.getElementById('rating-value');
    const saveButton = document.getElementById('save-rating-btn');

    // Disable the submit button initially
    saveButton.disabled = true;

    /**
     * Handles star click events to set the selected rating
     * and enable the save button.
     */
    stars.forEach((star) => {
        star.addEventListener('click', function () {
            // Update the hidden input's value
            ratingInput.value = this.getAttribute('data-value');

            // Enable the submit button
            saveButton.disabled = !ratingInput.value;
        });
    });

    const cancelBtns = document.querySelectorAll('.cancel-rating-btns');
    /**
     * Handles cancel buttons to reset rating input and unfill stars.
     */
    cancelBtns.forEach((cancelBtn) => {
        cancelBtn.addEventListener('click', () => {
            // Reset stars
            ratingInput.value = '';

            stars.forEach((s) => {
                const icon = s.querySelector('i');
                icon.classList.remove('bi-star-fill');
                icon.classList.add('bi-star');
            });
        });
    });

    /**
     * Updates star icons based on the user's selected rating.
     */
    stars.forEach((star) => {
        star.addEventListener('click', function () {
            const rating = this.getAttribute('data-value');
            ratingInput.value = rating;

            stars.forEach((s) => {
                const val = s.getAttribute('data-value');
                const icon = s.querySelector('i');

                if (val <= rating) {
                    icon.classList.add('bi-star-fill');
                    icon.classList.remove('bi-star');
                } else {
                    icon.classList.add('bi-star');
                    icon.classList.remove('bi-star-fill');
                }
            });
        });
    });
});
