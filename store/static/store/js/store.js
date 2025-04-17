function scrollToNewsletterSection() {
    const newsletterSection = document.getElementById('newsletter-section-id')
    console.log('newsletterSection', newsletterSection)

    if (newsletterSection) {
        const scrollToSection = newsletterSection
            .getAttribute('data-scroll-to')
            .trim()
        console.log('scrollToSection', scrollToSection)

        // Ensure that scrollToSection is valid
        if (scrollToSection && scrollToSection !== 'None') {
            const targetElement = document.getElementById(scrollToSection)
            console.log('targetElement', targetElement)
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' })
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    console.log('Script is loaded')
    scrollToNewsletterSection()
})
