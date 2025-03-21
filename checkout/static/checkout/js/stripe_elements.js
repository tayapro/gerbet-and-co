document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('checkout-form')
    const submitButton = document.getElementById('submit-button')
    const cardErrors = document.getElementById('card-errors')
    const csrfToken = document.querySelector(
        '[name=csrfmiddlewaretoken]'
    )?.value

    if (!form || !submitButton || !cardErrors) return

    const stripePublicKey = JSON.parse(
        document.getElementById('id_stripe_public_key').textContent
    )
    const clientSecret = JSON.parse(
        document.getElementById('id_client_secret').textContent
    )
    const stripe = window.Stripe(stripePublicKey)

    const elements = stripe.elements({
        mode: 'payment',
        currency: document.getElementById('currency').value,
        amount: parseInt(document.getElementById('amount').value),
        paymentMethodCreation: 'manual',
    })

    const paymentElement = elements.create('payment', {
        layout: {
            type: 'tabs',
            defaultCollapsed: false,
        },
    })
    paymentElement.mount('#payment-element')

    // Real-time Validation Setup
    setupValidation()
    initializeStripeValidation()

    // Form Submission Handler
    form.addEventListener('submit', async (event) => {
        event.preventDefault()
        submitButton.disabled = true
        clearAllErrors()

        try {
            // Step 1: Validate Django Form Fields
            if (!validateForm()) {
                focusFirstInvalidField()
                throw new Error('Please fix form errors')
            }

            // Step 2: Validate Stripe Elements
            const { error: elementsError } = await elements.submit()
            if (elementsError) throw elementsError

            // Step 3: Cache Checkout Data
            const cacheResponse = await cacheCheckoutData()
            if (cacheResponse.redirected) {
                window.location.href = cacheResponse.url
                return
            }

            // Step 4: Confirm Payment
            const { error: paymentError } = await stripe.confirmPayment({
                elements,
                clientSecret,
                confirmParams: getConfirmParams(),
                redirect: 'if_required',
            })

            if (paymentError) throw paymentError

            // Final Submission
            form.submit()
        } catch (error) {
            handleError(error)
        } finally {
            submitButton.disabled = false
        }
    })

    // Helper Functions
    function setupValidation() {
        document.querySelectorAll('.form-control').forEach((field) => {
            field.addEventListener('input', handleFieldInput)
            field.addEventListener('blur', handleFieldBlur)
        })
    }

    function initializeStripeValidation() {
        paymentElement.on('change', (event) => {
            cardErrors.textContent = event.error?.message || ''
            cardErrors.style.display = event.error ? 'block' : 'none'
        })
    }

    function handleFieldInput(event) {
        const field = event.target
        field.classList.remove('is-invalid')
        hideErrorMessage(field)
        cardErrors.textContent = ''
    }

    function handleFieldBlur(event) {
        const field = event.target
        if (field.required && field.value.trim() === '') {
            showErrorMessage(
                field,
                `${field.labels[0]?.textContent} is required`
            )
        }
    }

    function validateForm() {
        let isValid = true
        const isGuest = !!document.getElementById('id_guest_email')
        const useDefault = document.getElementById('id_use_default')?.checked

        // Validate Guest Fields
        if (isGuest) {
            isValid = [
                'guest_first_name',
                'guest_last_name',
                'guest_email',
            ].every((id) => {
                return validateField(document.getElementById(`id_${id}`))
            })
        }

        // Validate Address Fields
        if (!useDefault) {
            isValid =
                [
                    'phone_number',
                    'street_address1',
                    'town_or_city',
                    'country',
                ].every((id) => {
                    return validateField(document.getElementById(`id_${id}`))
                }) && isValid
        }

        return isValid
    }

    // function validateField(field) {
    //     if (!field) return true
    //     const isValid = field.value.trim() !== ''
    //     field.classList.toggle('is-invalid', !isValid)
    //     if (!isValid)
    //         showErrorMessage(
    //             field,
    //             `${field.labels[0]?.textContent} is required`
    //         )
    //     return isValid
    // }

    function validateField(field) {
        if (!field) return true

        const fieldType = field.getAttribute('data-validate') || field.type
        let isValid = true

        switch (fieldType) {
            case 'text':
            case 'textarea':
                isValid = field.value.trim().length > 2
                break

            case 'email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
                isValid = emailRegex.test(field.value.trim())
                break

            case 'tel':
                const phoneRegex = /^\+?\d{7,15}$/
                isValid = phoneRegex.test(field.value.trim())
                break

            case 'number':
                isValid =
                    field.value.trim() !== '' && !isNaN(parseFloat(field.value))
                break

            case 'checkbox':
                isValid = field.required ? field.checked : true
                break

            case 'select-one':
                isValid = field.value !== '' && field.value !== 'default'
                break

            default:
                isValid = field.value.trim().length > 2
        }

        // Apply validation feedback
        field.classList.toggle('is-invalid', !isValid)

        if (!isValid) {
            const label = field.labels
                ? field.labels[0]?.textContent
                : 'This field'
            const message =
                fieldType === 'tel'
                    ? `${label} must be a valid phone number (7-15 digits, optional + at start)`
                    : `${label} is required or invalid`
            showErrorMessage(field, message)
        } else {
            clearErrorMessage(field)
        }

        return isValid
    }

    function clearErrorMessage(field) {
        let errorSpan = field.nextElementSibling
        if (errorSpan && errorSpan.classList.contains('invalid-feedback')) {
            errorSpan.style.display = 'none'
        }
    }

    async function cacheCheckoutData() {
        return await fetch('/checkout/cache_checkout_data/', {
            method: 'POST',
            body: new FormData(form),
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken,
            },
        })
    }

    function getConfirmParams() {
        return {
            return_url: `${window.location.origin}/checkout/success/${
                document.getElementById('order_id').value
            }/`,
            payment_method_data: {
                billing_details: {
                    name: getFullName(),
                    email:
                        document.getElementById('id_guest_email')?.value ||
                        document.getElementById('id_email')?.value,
                },
            },
        }
    }

    function getFullName() {
        const isGuest = !!document.getElementById('id_guest_first_name')
        if (isGuest) {
            return `${document.getElementById('id_guest_first_name').value} ${
                document.getElementById('id_guest_last_name').value
            }`.trim()
        }
        return document.getElementById('full_name')?.value.trim() || ''
    }

    function handleError(error) {
        console.error('Checkout Error:', error)
        cardErrors.textContent = error.message
        cardErrors.style.display = 'block'

        if (error.type === 'validation_error') {
            document.querySelector('#payment-element').scrollIntoView({
                behavior: 'smooth',
                block: 'center',
            })
        }
    }

    function clearAllErrors() {
        document.querySelectorAll('.is-invalid').forEach((field) => {
            field.classList.remove('is-invalid')
            hideErrorMessage(field)
        })
        cardErrors.textContent = ''
    }

    function focusFirstInvalidField() {
        const firstInvalid = document.querySelector('.is-invalid')
        if (firstInvalid) {
            firstInvalid.focus()
            firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
    }

    function showErrorMessage(field, message) {
        field.setAttribute('aria-invalid', 'true')
        const errorId = `error_1_${field.id}`

        let errorElement = document.getElementById(errorId)
        if (!errorElement) {
            errorElement = document.createElement('div')
            errorElement.id = errorId
            errorElement.className = 'invalid-feedback'
            field.parentNode.appendChild(errorElement)
        }

        errorElement.textContent = message
        field.setAttribute('aria-describedby', errorId)
    }

    function hideErrorMessage(field) {
        const errorElement = document.getElementById(`error_1_${field.id}`)
        if (errorElement) errorElement.textContent = ''
        field.removeAttribute('aria-invalid')
        field.removeAttribute('aria-describedby')
    }
})
