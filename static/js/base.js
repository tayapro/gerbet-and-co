// Tooltips
function drawTooltip() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => {
        new bootstrap.Tooltip(el)
    })
}

// Modal window
function drawModalWindow() {
    const messagesModal = document.getElementById('messagesModal')

    if (messagesModal) {
        const alerts = messagesModal.querySelectorAll('.alert')
        if (alerts.length > 0) {
            const modal = new bootstrap.Modal(messagesModal)

            // Add icons to each type of alert
            alerts.forEach((alert) => {
                let iconHTML = ''
                if (alert.classList.contains('success')) {
                    iconHTML = `<i class="fa-solid fa-xl fa-circle-check text-success me-2"></i>`
                } else if (alert.classList.contains('error')) {
                    iconHTML = `<i class="fa-solid fa-xl fa-circle-exclamation text-danger me-2"></i>`
                } else if (alert.classList.contains('warning')) {
                    iconHTML = `<i class="fa-solid fa-xl fa-triangle-exclamation text-warning me-2"></i>`
                } else if (alert.classList.contains('info')) {
                    iconHTML = `<i class="fa-solid fa-xl fa-circle-info text-info me-2"></i>`
                }
                alert.innerHTML = `${iconHTML}${alert.innerHTML}`
            })

            // Manage inert attribute for accessibility
            messagesModal.addEventListener('shown.bs.modal', () => {
                messagesModal.removeAttribute('inert')
                messagesModal.focus()
            })

            messagesModal.addEventListener('hidden.bs.modal', () => {
                const closeButtonHeader = document.getElementById(
                    'messageModalHeaderCloseButton'
                )
                const closeButtonFooter = document.getElementById(
                    'messageModalFooterCloseButton'
                )

                closeButtonHeader.blur()
                closeButtonFooter.blur()

                messagesModal.setAttribute('inert', 'true')
                messagesModal.classList.add('d-none')
            })

            modal.show()
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    drawTooltip()
    drawModalWindow()

    // Prevent Empty Search Submition
    document
        .getElementById('search-form')
        .addEventListener('submit', function (e) {
            const searchInput = document
                .getElementById('search-input')
                .value.trim()
            const errorMessage = document.getElementById('error-message')

            if (!searchInput) {
                e.preventDefault()
                errorMessage.classList.remove('d-none')
            } else {
                errorMessage.classList.add('d-none')
            }
        })

    // Offcanvas
    document.querySelectorAll('.offcanvas').forEach((el) => {
        el.style.display = 'none'

        el.addEventListener('show.bs.offcanvas', function () {
            el.style.display = ''
        })

        el.addEventListener('hidden.bs.offcanvas', function () {
            setTimeout(() => {
                el.style.display = 'none'
            }, 400)
        })
    })
})
