/**
 * Replaces the country code in the order summary page
 * with the full country name after the page loads.
 *
 * - Retrieves the country code from the specified element.
 * - Converts it to the full country name.
 * - Updates the element's text content.
 */
document.addEventListener('DOMContentLoaded', function () {
    const countryEl = document.getElementById('order-country-id');

    if (countryEl) {
        const countryCode = countryEl.textContent.trim();
        const countryName = displayCountryName(countryCode);
        countryEl.textContent = countryName;
    }
});
