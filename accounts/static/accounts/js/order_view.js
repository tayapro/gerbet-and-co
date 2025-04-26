document.addEventListener('DOMContentLoaded', function () {
    const countryEl = document.getElementById('order-country-id')

    if (countryEl) {
        const countryCode = countryEl.textContent.trim()
        const countryName = displayCountryName(countryCode)
        countryEl.textContent = countryName
    }
})
