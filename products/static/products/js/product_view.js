document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('ratingModal')
    const ratingForm = document.getElementById('rating-form')

    modal.addEventListener('show.bs.modal', function (event) {
        const trigger = event.relatedTarget
        if (!trigger) return

        const productId = trigger.getAttribute('data-product-id')

        // Update the form action dynamically
        const newAction = `/products/rating/${productId}/`
        ratingForm.setAttribute('action', newAction)
    })

    const stars = document.querySelectorAll('.star-btn')
    const ratingSaveBtn = document.getElementById('save-rating-btn')
    const ratingInput = document.getElementById('rating-value')
    const saveButton = document.getElementById('save-rating-btn')

    // Disable the submit button initially
    saveButton.disabled = true

    // Add event listeners to all star buttons
    stars.forEach((star) => {
        star.addEventListener('click', function () {
            // Update the hidden input's value
            ratingInput.value = this.getAttribute('data-value')

            // Log to confirm value change
            console.log('Selected rating value:', ratingInput.value)

            // Enable the submit button
            saveButton.disabled = !ratingInput.value
        })
    })

    const cancelBtns = document.querySelectorAll('.cancel-rating-btns')
    cancelBtns.forEach((cancelBtn) => {
        cancelBtn.addEventListener('click', () => {
            // Reset stars
            ratingInput.value = ''
            console.log('Rating value:', ratingInput.value)
            stars.forEach((s) => {
                const icon = s.querySelector('i')
                icon.classList.remove('bi-star-fill')
                icon.classList.add('bi-star')
            })
        })
    })

    // Handle star clicks
    stars.forEach((star) => {
        star.addEventListener('click', function () {
            const rating = this.getAttribute('data-value')
            ratingInput.value = rating

            stars.forEach((s) => {
                const val = s.getAttribute('data-value')
                const icon = s.querySelector('i')

                if (val <= rating) {
                    icon.classList.add('bi-star-fill')
                    icon.classList.remove('bi-star')
                } else {
                    icon.classList.add('bi-star')
                    icon.classList.remove('bi-star-fill')
                }
            })
        })
    })
})
