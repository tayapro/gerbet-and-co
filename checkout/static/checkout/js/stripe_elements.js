function getFullName(form) {
    const isGuest = form.elements['guest_first_name'] !== undefined

    if (isGuest) {
        const firstName = form.guest_first_name.value.trim()
        const lastName = form.guest_last_name.value.trim()
        return `${firstName} ${lastName}`.trim()
    } else {
        return form.full_name.value.trim()
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('checkout-form')
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

    const orderId = document.getElementById('order_id').value
    if (!orderId) {
        document.getElementById('card-errors').textContent =
            'Missing order reference'
        return
    }

    const successUrl = window.location.origin + `/checkout/success/${orderId}/`

    form.addEventListener('submit', async (event) => {
        event.preventDefault()
        const submitButton = document.getElementById('submit-button')
        submitButton.disabled = true

        const isGuest = document.getElementById('id_guest_first_name') !== null

        const emailField = isGuest ? 'guest_email' : 'email'
        const email = form[emailField]?.value.trim() || ''

        const name = getFullName(form)

        // Validate elements first
        const { error: elementsError } = await elements.submit()
        if (elementsError) {
            handleError(elementsError)
            return
        }

        // Cache checkout data in Django
        const postData = new FormData()
        postData.append('order_id', document.getElementById('order_id').value)
        postData.append(
            'save_info',
            document.getElementById('id-save-info')?.checked
        )

        try {
            await fetch('/checkout/cache_checkout_data/', {
                method: 'POST',
                body: postData,
            })

            const { paymentIntent, error } = await stripe.confirmPayment({
                elements,
                clientSecret,
                confirmParams: {
                    return_url: successUrl,
                    payment_method_data: {
                        billing_details: {
                            name: name,
                            email: email,
                            //         address: {
                            //             line1: form.street_address1.value.trim(),
                            //             line2: form.street_address2.value.trim(),
                            //             city: form.town_or_city.value.trim(),
                            //             state: form.county.value.trim(),
                            //             postal_code: form.postcode.value.trim(),
                            //             country: form.country.value.trim(),
                            //         },
                        },
                    },
                },
                redirect: 'if_required',
            })

            if (error) {
                handleError(error)
            } else {
                // Handle server-side confirmation
                const paymentIntentId = document.createElement('input')
                paymentIntentId.type = 'hidden'
                paymentIntentId.name = 'payment_intent_id'
                paymentIntentId.value = paymentIntent.id
                form.appendChild(paymentIntentId)

                form.submit()
            }
        } catch (err) {
            console.error('Error caching checkout data:', err)
            handleError(err)
        }

        submitButton.disabled = false
    })

    function handleError(error) {
        const errorElement = document.getElementById('card-errors')
        errorElement.textContent = error.message
    }
})
