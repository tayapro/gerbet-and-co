function validateField(field) {
    const errorMsg = 'This field is required'
    const parent = field.closest('.form-group, .form-control, div')

    if (!field.value.trim()) {
        field.classList.add('is-invalid')
        field.setAttribute('title', errorMsg)
        if (
            !field.nextElementSibling ||
            !field.nextElementSibling.classList.contains('invalid-feedback')
        ) {
            const errorDiv = document.createElement('div')
            errorDiv.className = 'invalid-feedback d-block'
            errorDiv.innerText = errorMsg
            field.parentNode.insertBefore(errorDiv, field.nextSibling)
        }
        return false
    } else {
        field.classList.remove('is-invalid')
        field.removeAttribute('title')
        if (
            field.nextElementSibling &&
            field.nextElementSibling.classList.contains('invalid-feedback')
        ) {
            field.nextElementSibling.remove()
        }
        return true
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('address-form')
    const requiredFields = [
        document.getElementById('id_street_address1'),
        document.getElementById('id_town_or_city'),
        document.getElementById('id_postcode'),
        document.getElementById('id_phone_number'),
        document.getElementById('id_country'),
    ].filter((field) => field !== null)

    // Add listener to validate each required field
    requiredFields.forEach((field) => {
        field.addEventListener('input', () => validateField(field))
        field.addEventListener('blur', () => validateField(field))
    })

    form.addEventListener('submit', function (e) {
        let formIsValid = true

        requiredFields.forEach((field) => {
            if (!validateField(field)) {
                formIsValid = false
            }
        })

        if (!formIsValid) {
            e.preventDefault()
        }
    })
})
