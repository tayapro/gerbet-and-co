/**
 * Smoothly scrolls to the newsletter section if a subscription form error occurs
 * and the page specifies a scroll target.
 */
function scrollToNewsletterSection() {
    const newsletterSection = document.getElementById('newsletter-section-id');

    if (newsletterSection) {
        const scrollToSection = newsletterSection
            .getAttribute('data-scroll-to')
            .trim();

        // Ensure that scrollToSection is valid
        if (scrollToSection && scrollToSection !== 'None') {
            const targetElement = document.getElementById(scrollToSection);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        }
    }
}

/**
 * Initialize the scroll behavior to the newsletter section after the page loads.
 */
document.addEventListener('DOMContentLoaded', function () {
    scrollToNewsletterSection();
});
