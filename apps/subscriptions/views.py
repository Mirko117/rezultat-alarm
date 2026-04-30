import logging

from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse

from subscriptions.models import Student, StudentExamSubscription

from .models import Exam

logger = logging.getLogger("django")


def subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email")
        exam_ids = request.POST.getlist("exam_ids")

        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            return HttpResponse("Invalid email address", status=400)

        # Chekc if exams were selected
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

            # TODO: Right now fernet generates unique key every time, because of that also generate
            #       hash of the email and store it in the database, so we can check if the email is
            #       already subscribed to the exam without decrypting it every time.

            f = Fernet(settings.FERNET_KEY)

            encrypted_email = f.encrypt(email.encode()).decode()

            student, _ = Student.objects.get_or_create(email_encrypted=encrypted_email)

            for exam in exams:
                StudentExamSubscription.objects.create(student=student, exam=exam)

            return HttpResponse("Uspesno ste se prijavili na obvestila za izpite!")
        except Exception as e:
            logger.critical(
                f"Error occurred while subscribing student to exams: {e}", exc_info=True
            )
            return HttpResponse("Something went wrong.", status=500)
    else:
        return HttpResponse("Invalid request method", status=400)
