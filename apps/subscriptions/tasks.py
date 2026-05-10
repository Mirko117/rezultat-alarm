from time import sleep

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def test() -> str:
    sleep(5)
    return "Test from Celery completed!"


@shared_task
def send_email_task(subject: str, message: str, recipient_list: list[str]) -> None:
    """
    Send an email to the user.

    Args:
        subject (str): The subject of the email.
        message (str): The message of the email.
        recipient_list (list[str]): The list of recipients.
    """
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
