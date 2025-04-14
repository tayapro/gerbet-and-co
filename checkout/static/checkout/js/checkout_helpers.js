function displayCountryName(countryCode) {
    let countryName = countryCode
    if (countryCode && countryCode.length === 2) {
        try {
            const displayNames = new Intl.DisplayNames(['en'], {
                type: 'region',
            })
            countryName = displayNames.of(countryCode.toUpperCase())
        } catch (error) {
            console.warn('Could not convert country code:', countryCode)
        }
    }
    return countryName
}

document.addEventListener('DOMContentLoaded', function () {
    const confirmCheckbox = document.getElementById('confirm-order-checkbox')
    const submitButton = document.getElementById('payment-btn')

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

    const useDefaultCheckbox = document.querySelector(
        '[data-id-for-label][name="use_default"]'
    )
    const saveAsDefaultCheckbox = document.querySelector(
        '[data-id-for-label][name="save_as_default"]'
    )
    const addressFields = document.getElementById('address-fields')
    const preview = document.getElementById('default-address-preview')

    if (!useDefaultCheckbox || !addressFields) return

    const toggleFields = (checked) => {
        addressFields.style.display = checked ? 'none' : 'block'
        preview.style.display = checked ? 'block' : 'none'

        // Clear fields when using default address
        addressFields
            .querySelectorAll('input, select, textarea')
            .forEach((field) => {
                if (checked) field.value = ''
            })

        // Reset save_as_default when using default address
        if (saveAsDefaultCheckbox) {
            saveAsDefaultCheckbox.checked = false
            saveAsDefaultCheckbox.value = 'false'
        }
    }

    // Initial toggle based on checkbox state
    toggleFields(useDefaultCheckbox.checked)

    useDefaultCheckbox.addEventListener('change', (e) => {
        toggleFields(e.target.checked)
    })
})
