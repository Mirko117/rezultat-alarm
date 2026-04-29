from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse
from django.shortcuts import render
from subscriptions.models import Student, StudentExamSubscription  # Ruff is tripping

from core.models import Exam, Major, SchoolClass


def index(request):
    return render(request, "core/index.html")


def select_major(request):
    majors = Major.objects.all()
    return render(request, "core/select-major.html", {"majors": majors})


def select_exams(request, major_id):
    major = Major.objects.get(id=major_id)
    classes = SchoolClass.objects.filter(major=major)
    exams = Exam.objects.filter(school_class__in=classes).filter(results_available=False)

    context = {
        "major": major,
        "classes": classes,
        "exams": exams,
    }

    return render(request, "core/select-exams.html", context)


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

        # Check if exams exist
        exams = Exam.objects.filter(id__in=exam_ids)
        if exams.count() != len(exam_ids):
            return HttpResponse("One or more exams not found", status=400)

        f = Fernet(settings.FERNET_KEY)

        encrypted_email = f.encrypt(email.encode()).decode()

        student, _ = Student.objects.get_or_create(email_encrypted=encrypted_email)

        for exam in exams:
            StudentExamSubscription.objects.create(student=student, exam=exam)

        return HttpResponse("Subscription successful!")
    else:
        return HttpResponse("Invalid request method", status=400)
