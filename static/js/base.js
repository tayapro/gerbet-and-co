/**
 * Initializes Bootstrap tooltips for elements with data-bs-toggle="tooltip".
 */
function drawTooltip() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => {
        new bootstrap.Tooltip(el);
    });
}

/**
 * Handles displaying a Bootstrap modal for messages,
 * including adding icons and managing accessibility features.
 */
function drawModalWindow() {
    const messagesModal = document.getElementById('messagesModal');

    if (messagesModal) {
        const alerts = messagesModal.querySelectorAll('.alert');
        if (alerts.length > 0) {
            const modal = new bootstrap.Modal(messagesModal);

            // Add icons to each type of alert
            alerts.forEach((alert) => {
                let iconHTML = '';
                if (alert.classList.contains('success')) {
                    iconHTML = `<i class="bi bi-check-circle-fill fs-1 text-success me-2"></i>`;
                } else if (alert.classList.contains('error')) {
                    iconHTML = `<i class="bi bi-exclamation-circle-fill fs-1 text-danger me-2"></i>`;
                } else if (alert.classList.contains('warning')) {
                    iconHTML = `<i class="bi bi-exclamation-circle-fill fs-1 text-warning me-2"></i>`;
                } else if (alert.classList.contains('info')) {
                    iconHTML = `<i class="bi bi-info-circle-fill fs-1 text-info me-2"></i>`;
                }
                alert.innerHTML = `${iconHTML}${alert.innerHTML}`;
            });

            // Manage inert attribute for accessibility
            messagesModal.addEventListener('shown.bs.modal', () => {
                messagesModal.removeAttribute('inert');
                messagesModal.focus();
            });

            messagesModal.addEventListener('hidden.bs.modal', () => {
                const closeButtonHeader = document.getElementById(
                    'messageModalHeaderCloseButton'
                );
                const closeButtonFooter = document.getElementById(
                    'messageModalFooterCloseButton'
                );

                closeButtonHeader.blur();
                closeButtonFooter.blur();

                messagesModal.setAttribute('inert', 'true');
                messagesModal.classList.add('d-none');
            });

            modal.show();
        }
    }
}

/**
 * Initializes tooltips, modals, prevents empty search submissions,
 * manages offcanvas visibility, and handles search sidebar reset.
 */
document.addEventListener('DOMContentLoaded', function () {
    drawTooltip();
    drawModalWindow();

    // Prevent Empty Search Submition
    document
        .getElementById('search-form')
        .addEventListener('submit', function (e) {
            const searchInput = document
                .getElementById('search-input')
                .value.trim();
            const errorMessage = document.getElementById('error-message');

            if (!searchInput) {
                e.preventDefault();
                errorMessage.classList.remove('d-none');
            } else {
                errorMessage.classList.add('d-none');
            }
        });

    // Offcanvas
    document.querySelectorAll('.offcanvas').forEach((el) => {
        el.style.display = 'none';

        el.addEventListener('show.bs.offcanvas', function () {
            el.style.display = '';
        });

        el.addEventListener('hidden.bs.offcanvas', function () {
            setTimeout(() => {
                el.style.display = 'none';
            }, 400);
        });
    });

    // Search sidebar
    const searchCloseBtn = document.getElementById('search-btn-close');
    const input = document.getElementById('search-input');

    searchCloseBtn.addEventListener('click', function () {
        input.value = '';
        input.focus();
    });
});

/**
 * Handles hiding the toast notification after it has been swapped via HTMX.
 */
document.addEventListener('htmx:afterSwap', function () {
    const closeBtn = document.getElementById('close-toast-btn');
    const toastContainer = document.getElementById('toast-container');

    if (closeBtn && toastContainer) {
        closeBtn.addEventListener('click', () => {
            toastContainer.classList.remove('position-absolute');
            toastContainer.classList.add('d-none');
        });
    }
});
