import hashlib
import hmac
import logging

from core.models import Exam
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from .models import Student, StudentExamSubscription

logger = logging.getLogger("django")


@require_POST
def subscribe(request):
    email = request.POST.get("email")
    exam_ids = request.POST.getlist("exam_ids")

    email = email.strip().lower() if email else ""

    # Validate email
    try:
        validate_email(email)
    except ValidationError:
        return HttpResponse("Invalid email address", status=400)

    # Check if exams were selected
    if not exam_ids or len(exam_ids) == 0:
        return HttpResponse("No exams selected", status=400)

    # Check if exams are integers
    try:
        exam_ids = [int(e) for e in exam_ids]
    except ValueError:
        return HttpResponse("Invalid exam IDs", status=400)

    try:
        # Check if exams exist
        exams = Exam.objects.filter(id__in=exam_ids)
        if exams.count() != len(exam_ids):
            return HttpResponse("One or more exams not found", status=400)

        f = Fernet(settings.FERNET_KEY)

        email_encrypted = f.encrypt(email.encode()).decode()

        # Since fernet encryption is non-deterministic (every time it generates a unique key),
        # we need to hash the email for lookup
        email_hash = hmac.new(
            settings.SECRET_KEY.encode(), email.encode(), hashlib.sha256
        ).hexdigest()

        # Use hash for lookup
        student, _ = Student.objects.get_or_create(
            email_hash=email_hash, defaults={"email_encrypted": email_encrypted}
        )

        new_subscriptions = []
        for exam in exams:
            new_subscriptions.append(StudentExamSubscription(student=student, exam=exam))

        # ignore_conflicts=True to avoid duplicate subscriptions
        StudentExamSubscription.objects.bulk_create(new_subscriptions, ignore_conflicts=True)

        return redirect("subscription_success")
    except Exception as e:
        logger.critical(f"Error occurred while subscribing student to exams: {e}", exc_info=True)
        return HttpResponse("Something went wrong.", status=500)
