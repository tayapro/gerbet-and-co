document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('checkout-form')
    const submitButton = document.getElementById('payment-btn')
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

        // Step 1: Validate form fields before anything else
        const isFormValid = validateForm()
        if (!isFormValid) {
            focusFirstInvalidField()
            cardErrors.textContent =
                'Please correct the highlighted errors before continuing.'
            submitButton.disabled = false
            return
        }

        try {
            // Step 2: Validate Stripe Elements
            const { error: elementsError } = await elements.submit()
            if (elementsError) {
                handleError(cardErrors, elementsError)
                submitButton.disabled = false
                return
            }

            // Step 3: Cache Checkout Data
            const cacheResponse = await cacheCheckoutData()
            if (cacheResponse.redirect) {
                window.location.href = cacheResponse.redirect
                return
            }
            if (cacheResponse.error) {
                cardErrors.textContent = cacheResponse.error
                submitButton.disabled = false
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
                `${field.labels[0]?.textContent} is required or invalid`
            )
        }
    }

    function validateForm() {
        let isValid = true
        const isGuest = !!document.getElementById('id_guest_email')
        const useDefault = document.getElementById('id_use_default')?.checked

        // Validate Guest Fields
        if (isGuest) {
            isValid =
                validateFields([
                    'guest_first_name',
                    'guest_last_name',
                    'guest_email',
                ]) && isValid
        }

        // Validate Address Fields
        if (!useDefault) {
            isValid =
                validateFields([
                    'phone_number',
                    'street_address1',
                    'town_or_city',
                    'postcode',
                    'country',
                ]) && isValid
        }

        return isValid
    }

    function validateFields(fieldIds) {
        let groupIsValid = true

        fieldIds.forEach((id) => {
            const field = document.getElementById(`id_${id}`)
            if (!field) return

            const fieldValid = validateField(field)
            if (!fieldValid) {
                groupIsValid = false
            }
        })

        return groupIsValid
    }

    function validateField(field) {
        if (!field) return true

        const fieldType = field.getAttribute('data-validate') || field.type
        let isValid = true

        switch (fieldType) {
            case 'text':
            case 'textarea':
                isValid = field.value.trim().length >= 2
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
                isValid = field.value.trim().length >= 2
        }

        // Apply validation feedback
        field.classList.toggle('is-invalid', !isValid)

        if (!isValid) {
            const label = field.labels
                ? field.labels[0]?.textContent
                : 'This field'

            let message
            if (fieldType === 'tel') {
                message = `${label} must be a valid phone number (7-15 digits, optional + at start)`
            } else if (fieldType === 'email') {
                message = `${label} must be a valid email address (e.g. name@example.com)`
            } else {
                message = `${label} is required or invalid`
            }

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
        const postData = new FormData()
        postData.append('order_id', document.getElementById('order_id').value)
        postData.append(
            'save_info',
            document.getElementById('id-save-info')?.checked
        )

        try {
            const response = await fetch('/checkout/cache_checkout_data/', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken,
                },
                body: postData,
            })

            const data = await response.json()

            if (data.redirect_url) {
                return { redirect: true, url: data.redirect_url }
            }

            if (response.status !== 200) {
                return {
                    error: data.error || 'Failed to cache checkout data',
                    status: response.status,
                }
            }

            return { success: true }
        } catch (err) {
            console.error('Cache error:', err)
            return {
                error: 'A network error occurred.',
                status: 500,
            }
        }
    }

    function getConfirmParams() {
        const orderId = document.getElementById('order_id').value
        const returnUrl = `${window.location.origin}/checkout/success/${orderId}/`

        return {
            return_url: returnUrl,
            payment_method_data: {
                billing_details: {
                    name: getFullName(),
                    email: getEmail(),
                    phone: getPhone(),
                },
            },
        }
    }

    function getFullName() {
        const guestFirstName = document.getElementById('id_guest_first_name')
        const guestLastName = document.getElementById('id_guest_last_name')

        if (guestFirstName && guestLastName) {
            return `${guestFirstName.value} ${guestLastName.value}`.trim()
        }

        return document.getElementById('full_name')?.value.trim() || ''
    }

    function getEmail() {
        const guestEmailElement = document.getElementById('id_guest_email')
        const guestEmail =
            guestEmailElement && guestEmailElement.value
                ? guestEmailElement.value.trim()
                : ''

        const authEmailElement = document.getElementById('email')
        const authEmail =
            authEmailElement && authEmailElement.value
                ? authEmailElement.value.trim()
                : ''

        const email = guestEmail || authEmail || ''

        return email
    }

    function getPhone() {
        const preview = document.getElementById('default-address-preview')
        const previewPhone =
            preview && preview.dataset.phone ? preview.dataset.phone.trim() : ''

        const phoneElement = document.getElementById('id_phone_number')
        const phoneInput =
            phoneElement && phoneElement.value ? phoneElement.value.trim() : ''

        const phone = phoneInput || previewPhone || ''

        return phone
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
