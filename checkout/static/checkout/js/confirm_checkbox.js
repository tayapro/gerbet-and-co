document.addEventListener('DOMContentLoaded', function () {
    const confirmCheckbox = document.getElementById('confirm-order-checkbox')
    const submitButton = document.getElementById('submit-button')

    confirmCheckbox.addEventListener('change', function () {
        submitButton.disabled = !this.checked
    })
})
