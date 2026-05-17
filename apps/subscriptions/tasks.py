from celery import shared_task
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.mail import send_mass_mail

from .models import StudentExamSubscription


# You can not pass model instances to Celery tasks, so we need to pass the exam ID and then
# get the exam details in the task
@shared_task
def email_on_exam_change_task(subject: str, message: str, exam_id: int) -> None:
    """
    Send an email to the users that are subscribed to the exam about the change in the exam details.
    """

    # Get encrypted email addresses of students subscribed to the exam
    encrypted_emails = StudentExamSubscription.objects.filter(exam_id=exam_id).values_list(
        "student__email_encrypted", flat=True
    )

    if not encrypted_emails:
        return

    recipients = []

    # Decrypt email addresses
    f = Fernet(settings.FERNET_KEY)
    for encrypted_email in encrypted_emails:
        decrypted_email = f.decrypt(encrypted_email.encode()).decode()
        recipients.append(decrypted_email)

    send_mass_mail(
        [
            (
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
            )
            for recipient in recipients
        ],
        fail_silently=False,
    )
