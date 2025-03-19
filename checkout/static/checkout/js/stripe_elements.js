function getFullName(form) {
    const isGuest = form.elements['guest_first_name'] !== undefined

    if (isGuest) {
        const firstName = form.guest_first_name.value.trim()
        const lastName = form.guest_last_name.value.trim()
        return `${firstName} ${lastName}`.trim()
    } else {
        return form.full_name ? form.full_name.value.trim() : ''
    }
}

function validateForm() {
    let isValid = true
    const requiredFields = [
        'phone_number',
        'street_address1',
        'town_or_city',
        'postcode',
        'country',
    ]

    requiredFields.forEach((fieldName) => {
        const field = document.getElementById(`id_${fieldName}`)
        if (!field || field.value.trim() === '') {
            console.log('Auth user mode: ', field)
            field.classList.add('is-invalid')
            isValid = false
        } else {
            field.classList.remove('is-invalid')
        }
    })

    // Guest users validation
    const guestFields = ['guest_first_name', 'guest_last_name', 'guest_email']
    if (document.getElementById('id_guest_first_name')) {
        guestFields.forEach((fieldName) => {
            const field = document.getElementById(`id_${fieldName}`)
            console.log('Guest mode: ', field)
            if (!field || field.value.trim() === '') {
                field.classList.add('is-invalid')
                isValid = false
            } else {
                field.classList.remove('is-invalid')
            }
        })
    }

    return isValid
}

function handleError(cardErrors, error) {
    cardErrors.textContent = error.message
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('checkout-form')
    const submitButton = document.getElementById('submit-button')
    const cardErrors = document.getElementById('card-errors')

    if (!form || !submitButton || !cardErrors) return

    const orderId = document.getElementById('order_id').value
    if (!orderId) {
        document.getElementById('card-errors').textContent =
            'Missing order reference'
        return
    }

    const stripePublicKey = JSON.parse(
        document.getElementById('id_stripe_public_key').textContent
    )
    const clientSecret = JSON.parse(
        document.getElementById('id_client_secret').textContent
    )
    const stripe = window.Stripe(stripePublicKey)

    const currency = document.getElementById('currency').value
    if (!currency) {
        document.getElementById('card-errors').textContent =
            'Missing currency reference'
        return
    }

    const amount = document.getElementById('amount').value
    if (!amount) {
        document.getElementById('card-errors').textContent =
            'Missing amount reference'
        return
    }

    const elements = stripe.elements({
        mode: 'payment',
        currency: currency,
        amount: parseInt(amount),
        paymentMethodCreation: 'manual',
    })

    const paymentElement = elements.create('payment', {
        layout: {
            type: 'tabs',
            defaultCollapsed: false,
        },
    })
    paymentElement.mount('#payment-element')

    form.addEventListener('submit', async (event) => {
        event.preventDefault()
        submitButton.disabled = true

        if (!validateForm()) {
            cardErrors.textContent = 'Please fix the errors before proceeding.'
            submitButton.disabled = false
            return
        }

        try {
            // Call elements.submit() to validate inputs
            const { error: validationError } = await elements.submit()
            if (validationError) {
                handleError(cardErrors, validationError)
                submitButton.disabled = false
                return
            }

            // Retrieve user full name and email
            const name = getFullName(form)
            const emailField =
                document.getElementById('id_guest_email') ||
                document.getElementById('id_email')
            const email = emailField ? emailField.value.trim() : ''

            // Cache checkout data in Django session
            const postData = new FormData()
            postData.append('order_id', orderId)
            postData.append(
                'save_info',
                document.getElementById('id-save-info')?.checked
            )

            const resp = await fetch('/checkout/cache_checkout_data/', {
                method: 'POST',
                body: postData,
            })

            const responseData = await resp.json()

            if (resp.status !== 200) {
                // If backend validation fails, show error and stop payment
                console.log(
                    'If backend validation fails, show error and stop payment',
                    responseData.error
                )
                cardErrors.textContent =
                    responseData.error ||
                    'An error occurred while storing your checkout details.'
                submitButton.disabled = false
                return
            }

            // Confirm Stripe payment, if session storage was successful
            const { paymentIntent, error } = await stripe.confirmPayment({
                elements,
                clientSecret,
                confirmParams: {
                    return_url:
                        window.location.origin +
                        `/checkout/success/${orderId}/`,
                    payment_method_data: {
                        billing_details: {
                            name: name,
                            email: email,
                        },
                    },
                },
                redirect: 'if_required',
            })

            if (error) {
                handleError(cardErrors, error)
                submitButton.disabled = false
            } else {
                form.submit()
            }
        } catch (err) {
            console.error('Error processing payment:', err)
            handleError(cardErrors, err)
            submitButton.disabled = false
        }
    })
})
