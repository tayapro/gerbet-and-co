/**
 * Handles FAQ sidebar navigation:
 * - Highlights the active section based on the URL.
 * - Updates the active link when a new sidebar link is clicked.
 */
document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('faq-sidebar');

    // Highlight based on current URL
    const currentPath = window.location.pathname;
    const sectionMatch = currentPath.match(/\/help\/section\/([\w-]+)/);
    const links = sidebar.querySelectorAll(
        'a.list-group-item:not(.contact-link)'
    );

    if (sectionMatch) {
        const currentSection = sectionMatch[1];

        links.forEach((link) => {
            const href = link.getAttribute('href');
            if (href.includes(currentSection)) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    } else {
        if (links.length > 0) {
            links.forEach((link) => link.classList.remove('active'));
            links[0].classList.add('active');
        }
    }

    // Update active class on click (HTMX navigation)
    sidebar.addEventListener('click', function (e) {
        const link = e.target.closest('a.list-group-item');

        if (link) {
            sidebar.querySelectorAll('a.list-group-item').forEach((el) => {
                el.classList.remove('active');
            });

            link.classList.add('active');
        }
    });
});
