/**
 * Sets the delete link dynamically when the delete confirmation modal is shown.
 *
 * - Captures the delete URL from the clicked trigger button.
 * - Updates the confirmation button inside the modal with the correct URL.
 */
document.addEventListener('DOMContentLoaded', function () {
    const confirmModal = document.getElementById('confirmRemoveModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');

    confirmModal.addEventListener('show.bs.modal', function (event) {
        const triggerButton = event.relatedTarget;
        const deleteUrl = triggerButton.getAttribute('data-href');

        confirmDeleteBtn.setAttribute('href', deleteUrl);
    });
});
