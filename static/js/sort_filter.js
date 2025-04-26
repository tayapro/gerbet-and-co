document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('filter-form')
    const submitBtn = document.getElementById('filter-submit-btn')
    const minInput = document.getElementById('min_price')
    const maxInput = document.getElementById('max_price')
    const errorMessage = document.getElementById('price-error-message')

    function validatePriceRange() {
        const minVal = parseFloat(minInput.value.trim())
        const maxVal = parseFloat(maxInput.value.trim())

        const min = parseFloat(minVal)
        const max = parseFloat(maxVal)

        let isValid = true

        if (minVal && (isNaN(min) || min < 1)) {
            isValid = false
        }

        if (maxVal && (isNaN(max) || max < 1)) {
            isValid = false
        }

        if (minVal && maxVal && min > max) {
            isValid = false
        }

        if (!isValid) {
            errorMessage.classList.remove('d-none')
            submitBtn.setAttribute('disabled', true)
        } else {
            errorMessage.classList.add('d-none')
            submitBtn.removeAttribute('disabled')
        }

        return isValid
    }

    // Listen for real-time input changes
    minInput.addEventListener('input', validatePriceRange)
    maxInput.addEventListener('input', validatePriceRange)

    // Final validation on submit
    form.addEventListener('submit', function (e) {
        if (!validatePriceRange()) {
            e.preventDefault()
        }
    })

    // Initial state
    validatePriceRange()

    const filterForm = document.getElementById('filter-form')
    filterForm.addEventListener('submit', function (event) {
        const hiddenSearch = document.getElementById('search-input-hidden')
        const params = new URLSearchParams(window.location.search)
        hiddenSearch.value = params.get('search_query') || ''
    })
})
