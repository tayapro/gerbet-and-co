// Tooltips
function drawTooltip() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => {
        new bootstrap.Tooltip(el)
    })
}

document.addEventListener('DOMContentLoaded', function () {
    drawTooltip()

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
