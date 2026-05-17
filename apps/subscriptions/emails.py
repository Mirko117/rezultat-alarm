from core.models import Exam
from django.template.loader import render_to_string

from .tasks import email_on_exam_change_task


def email_on_exam_change(old_exam: Exam, new_exam: Exam):
    """
    Send an email to the user about the change in the exam details.

    Args:
        old_exam (Exam): The old exam details. Just a copy of the current exam before we update it
                         with new details.
        new_exam (Exam): The new exam details. The exam details that we just scraped and updated in
                         the database.
    """

    # Render email content
    rendered_email = render_to_string(
        "emails/changed.txt",
        {
            "old": old_exam,
            "new": new_exam,
        },
    )
    subject = f"Sprememba pri predmetu {old_exam.school_class.name} - {old_exam.name}"

    # Send email asynchronously using Celery task
    email_on_exam_change_task.delay(
        subject=subject,
        message=rendered_email,
        exam_id=new_exam.pk,
    )
