from django.conf import settings
from django.core.mail import BadHeaderError, send_mail


def send_email(subject, message, recipient_email):
    number_of_remaining = 0
    email_sent = False
    while not email_sent and number_of_remaining < settings.EMAIL_TRIES:
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email])
            email_sent = True

        except BadHeaderError:
            pass
        number_of_remaining += 1

    return email_sent
