import smtplib

from celery import shared_task
from celery.utils.log import get_task_logger
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.mail import send_mass_mail

from .models import StudentExamSubscription

logger = get_task_logger(__name__)


# You can not pass model instances to Celery tasks, so we need to pass the exam ID and then
# get the exam details in the task
@shared_task(
    bind=True,
    autoretry_for=(smtplib.SMTPException, ConnectionError),
    max_retries=3,
    default_retry_delay=60 * 5,  # Retry after 5 minutes
)
def email_on_exam_change_task(self, subject: str, message: str, exam_id: int) -> None:
    """
    Send an email to the users that are subscribed to the exam about the change in the exam details.
    """

    # Get encrypted email addresses of students subscribed to the exam
    encrypted_emails = StudentExamSubscription.objects.filter(exam_id=exam_id).values_list(
        "student__email_encrypted", flat=True
    )

    if not encrypted_emails:
        logger.info(f"No subscribers found for exam {exam_id}. No email will be sent.")
        return

    recipients = []

    # Decrypt email addresses
    f = Fernet(settings.FERNET_KEY)
    for encrypted_email in encrypted_emails:
        try:
            decrypted_email = f.decrypt(encrypted_email.encode()).decode()
            recipients.append(decrypted_email)
        except Exception as e:
            logger.error(f"Failed to decrypt email for exam {exam_id}: {e}")

    if not recipients:
        logger.info(f"No valid email addresses found for exam {exam_id}. No email will be sent.")
        return

    try:
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
    except Exception as e:
        logger.error(f"Error sending mass email for exam {exam_id}: {e}")

        # Re-raise the exception to trigger Celery's retry mechanism
        raise e

        # Note: The exception will be caught by the autoretry_for parameter in the task decorator,
        # and the task will be retried according to the specified retry policy.
        # self.retry can also be used to manually trigger a retry
