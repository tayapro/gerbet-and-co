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

function showSpinner() {
    const spinner = document.getElementById('loading-overlay')

    // Show spinner on page unload
    window.addEventListener('beforeunload', function () {
        if (spinner) {
            spinner.classList.remove('d-none')
        }
    })

    // Hide spinner once the page has fully loaded
    window.addEventListener('load', function () {
        if (spinner) {
            spinner.classList.add('d-none')
        }
    })
}

document.addEventListener('DOMContentLoaded', function () {
    showSpinner()

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

    const countryEl = document.getElementById('checkout-country-id')

    if (countryEl) {
        const countryCode = countryEl.textContent.trim()
        const countryName = displayCountryName(countryCode)
        countryEl.textContent = countryName
    }

    const countyCell = document.querySelector('#county-row td p')

    if (countyCell && countyCell.textContent.trim() === '') {
        const row = document.getElementById('county-row')
        if (row) row.style.display = 'none'
    }
})
