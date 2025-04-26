document.addEventListener('DOMContentLoaded', function () {
    const confirmModal = document.getElementById('confirmRemoveModal')
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn')

    confirmModal.addEventListener('show.bs.modal', function (event) {
        const triggerButton = event.relatedTarget
        const deleteUrl = triggerButton.getAttribute('data-href')

        confirmDeleteBtn.setAttribute('href', deleteUrl)
    })
})
