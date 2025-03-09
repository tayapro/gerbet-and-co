from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_welcome_email(request, user, **kwargs):
    """
    Sends a welcome email to the user after they successfully sign up.

    Args:
        request: The HTTP request object (passed automatically by the signal).
        user: The user who has just signed up.
        **kwargs: Additional keyword arguments that may be passed with
        the signal.
    """
    subject = "Welcome to Gerbet & Co!"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    # Render email content
    context = {'user': user}
    text_content = render_to_string('accounts/emails/welcome_email.txt',
                                    context)
    html_content = render_to_string('accounts/emails/welcome_email.html',
                                    context)

    # Send the email
    email = EmailMultiAlternatives(subject, text_content, email_from,
                                   recipient_list)
    email.attach_alternative(html_content, "text/html")

    email.send()
