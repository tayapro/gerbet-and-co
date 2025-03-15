document.addEventListener('DOMContentLoaded', function () {
    const confirmCheckbox = document.getElementById('confirm-order-checkbox')
    const submitButton = document.getElementById('submit-button')

    confirmCheckbox.addEventListener('change', function () {
        submitButton.disabled = !this.checked
    })

    // Disable the default behavior of the Enter key submitting
    // a form when focused on input fields
    const form = document.getElementById('checkout-form')

    form.addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault()
        }
    })

    // Handle DefaultAddress and SaveAsDefault checkboxes
    const useDefaultCheckbox = document.getElementById(
        '{{ form.use_default.id_for_label }}'
    )
    const saveAsDefaultCheckbox = document.getElementById(
        '{{ form.save_as_default.id_for_label }}'
    )
    const addressFields = document.getElementById('address-fields')
    const preview = document.getElementById('default-address-preview')

    const toggleFields = (checked) => {
        if (!addressFields || !preview) return

        addressFields.style.display = checked ? 'none' : 'block'
        preview.style.display = checked ? 'block' : 'none'

        // Clear fields when using default address
        addressFields
            .querySelectorAll('input, select, textarea')
            .forEach((field) => {
                if (checked) {
                    field.value = ''
                    field.classList.remove('is-invalid') // Remove validation error
                }
            })

        // Reset 'save as default' when using default address
        if (saveAsDefaultCheckbox) {
            saveAsDefaultCheckbox.checked = false
            saveAsDefaultCheckbox.value = 'false'
        }
    }

    if (useDefaultCheckbox) {
        // Initial toggle based on checkbox state
        toggleFields(useDefaultCheckbox.checked)

        // Handle user changes
        useDefaultCheckbox.addEventListener('change', (e) => {
            toggleFields(e.target.checked)
        })
    }
})
