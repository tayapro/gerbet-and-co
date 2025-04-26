function scrollToNewsletterSection() {
    const newsletterSection = document.getElementById('newsletter-section-id')

    if (newsletterSection) {
        const scrollToSection = newsletterSection
            .getAttribute('data-scroll-to')
            .trim()

        // Ensure that scrollToSection is valid
        if (scrollToSection && scrollToSection !== 'None') {
            const targetElement = document.getElementById(scrollToSection)
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' })
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    scrollToNewsletterSection()
})
