// Tooltips
function drawTooltip() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => {
        new bootstrap.Tooltip(el)
    })
}

document.addEventListener('DOMContentLoaded', function () {
    drawTooltip()
})
