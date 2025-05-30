/**
 * Handles the setup and dynamic content population of the
 * address delete confirmation modal.
 *
 * - When the modal is triggered, it extracts the address details
 *   from the clicked button's data attributes.
 * - Converts the country code into a full country name.
 * - Updates the modal text to show the formatted address.
 * - Sets the correct form action URL for address deletion.
 */
document.addEventListener('DOMContentLoaded', function () {
    // Grab the modal and delete button within it
    const modal = document.getElementById('confirmAddressRemoveModal');
    const addressEl = document.getElementById('modal-address-id');
    const form = document.getElementById('modal-delete-address-form');

    // Add an event listener to handle dynamically setting the delete URL
    modal.addEventListener('show.bs.modal', function (event) {
        const trigger = event.relatedTarget;
        if (!trigger) return;

        const streetAddress1 = trigger.getAttribute('data-street-address1');
        const streetAddress2 = trigger.getAttribute('data-street-address2');
        const city = trigger.getAttribute('data-city');
        const county = trigger.getAttribute('data-county');
        const postcode = trigger.getAttribute('data-postcode');
        const countryCode = trigger.getAttribute('data-country');

        // Convert country code to country name
        const countryName = displayCountryName(countryCode);

        // Update modal content
        const addressParts = [
            streetAddress1,
            streetAddress2,
            city,
            county,
            postcode,
            countryName,
        ].filter((part) => part && part !== 'None');

        // Update modal content
        addressEl.innerHTML = `
        <p class="text-center purple-text-75 fs-5">${addressParts.join(
            ', '
        )}</p>
        `;

        // Update form action
        const actionUrl = trigger.getAttribute('data-action-url');
        form.setAttribute('action', actionUrl);
    });

    // Select all country fields in the table
    const countryElements = document.querySelectorAll('.address-countries p');

    countryElements.forEach(function (countryElement) {
        const countryCode = countryElement.textContent.trim();
        const countryName = displayCountryName(countryCode);
        if (countryName) {
            countryElement.textContent = countryName;
        }
    });
});
