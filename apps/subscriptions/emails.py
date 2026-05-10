from core.models import Exam
from cryptography.fernet import Fernet
from django.conf import settings
from django.template.loader import render_to_string

from .models import StudentExamSubscription
from .tasks import send_email_task


def email_on_exam_change(old_exam: Exam, new_exam: Exam):
    """
    Send an email to the user about the change in the exam details.

    Args:
        old_exam (Exam): The old exam details.
        new_exam (Exam): The new exam details.
    """

    # Get suscribed users
    ## Can't filter by old exam since its not saved
    subscriptions = StudentExamSubscription.objects.filter(exam=new_exam)

    if not subscriptions.exists():
        return

    # Get recipients email addresses (encrypted)
    encrypted_recipients = [subscription.student.email_encrypted for subscription in subscriptions]

    recipients = []

    # Decrypt email addresses
    f = Fernet(settings.FERNET_KEY)
    for encrypted_email in encrypted_recipients:
        decrypted_email = f.decrypt(encrypted_email.encode()).decode()
        recipients.append(decrypted_email)

    # Render email content
    rendered_email = render_to_string(
        "emails/changed.txt",
        {
            "old": old_exam,
            "new": new_exam,
        },
    )

    # Send email to recipients
    for recipient in recipients:
        send_email_task.delay(
            subject=f"Sprememba pri predmetu {old_exam.school_class.name} - {old_exam.name}",
            message=rendered_email,
            recipient_list=[recipient],
        )
