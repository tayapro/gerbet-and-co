document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('checkout-form')
    const stripePublicKey = JSON.parse(
        document.getElementById('id_stripe_public_key').textContent
    )
    const clientSecret = JSON.parse(
        document.getElementById('id_client_secret').textContent
    )

    const stripe = Stripe(stripePublicKey)

    const optionsElements = document.getElementById('checkout_details')

    console.log('Currency JS: ', optionsElements.dataset.currency)
    console.log('Amount JS: ', optionsElements.dataset.amount)

    const elements = stripe.elements({
        mode: 'payment',
        currency: optionsElements.dataset.currency,
        amount: parseInt(optionsElements.dataset.amount),
        paymentMethodCreation: 'manual',
    })

    const paymentElement = elements.create('payment', {
        layout: {
            type: 'tabs',
            defaultCollapsed: false,
        },
    })
    paymentElement.mount('#payment-element')

    const tempOrderId = document.getElementById('temp_order_id').value
    if (!tempOrderId) {
        document.getElementById('card-errors').textContent =
            'Missing order reference'
        return
    }
    console.log('OrderID from JS: ', tempOrderId)
    const successUrl =
        window.location.origin + `/checkout/success/${tempOrderId}/`
    console.log('Successful URL from JS: ', successUrl)

    form.addEventListener('submit', async (event) => {
        event.preventDefault()
        const submitButton = document.getElementById('submit-button')
        submitButton.disabled = true

        // Validate elements first
        const { error: elementsError } = await elements.submit()
        if (elementsError) {
            handleError(elementsError)
            return
        }

        const { paymentIntent, error } = await stripe.confirmPayment({
            elements,
            clientSecret,
            confirmParams: {
                return_url: successUrl,
                payment_method_data: {
                    billing_details: {
                        name: form.full_name.value.trim(),
                        email: form.email.value.trim(),
                        address: {
                            line1: form.street_address1.value.trim(),
                            city: form.town_or_city.value.trim(),
                            country: form.country.value.trim(),
                        },
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
        submitButton.disabled = false
    })

    function handleError(error) {
        const errorElement = document.getElementById('card-errors')
        errorElement.textContent = error.message
    }
})
