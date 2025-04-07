from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_contact_us_email(request, contact_us_context, **kwargs):
    """
    Sends a contact us email to the user after they successfully submit form.

    Args:
        request: The HTTP request object (passed automatically by the signal).
        user: The user who has just signed up.
        **kwargs: Additional keyword arguments that may be passed with
        the signal.
    """

    subject = "Thank you for contacting Gerbet & Co."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [contact_us_context["email"]]

    # Render email content
    context = {
        "name": contact_us_context["name"],
        "message": contact_us_context["message"],
    }
    text_content = render_to_string("store/emails/contact_us_email.txt",
                                    context)
    html_content = render_to_string("store/emails/contact_us_email.html",
                                    context)

    # Send the email
    email = EmailMultiAlternatives(subject, text_content, email_from,
                                   recipient_list)
    email.attach_alternative(html_content, "text/html")

    email.send()
