from django.shortcuts import render
from subscriptions.tasks import test

from .models import Exam, Major, SchoolClass


def index(request):
    test.delay()
    return render(request, "core/index.html")


def select_major(request):
    majors = Major.objects.all()
    return render(request, "core/select-major.html", {"majors": majors})


def select_exams(request, major_id):
    major = Major.objects.get(id=major_id)
    classes = SchoolClass.objects.filter(major=major)
    exams = Exam.objects.filter(school_class__in=classes).order_by("date", "time")

    context = {
        "major": major,
        "classes": classes,
        "exams": exams,
    }

    return render(request, "core/select-exams.html", context)
