import hashlib
import hmac
from datetime import date, time
from unittest.mock import patch

import pytest
from core.models import Exam, Major, Professor, SchoolClass
from cryptography.fernet import Fernet
from django.conf import settings
from django.urls import reverse

from subscriptions.emails import email_on_exam_change
from subscriptions.models import Student, StudentExamSubscription


def _create_exam():
    major = Major.objects.create(name="Test major", url="http://example.com")
    professor = Professor.objects.create(full_name="Test professor")
    school_class = SchoolClass.objects.create(name="Test class", major=major, professor=professor)
    return Exam.objects.create(
        name="Test exam",
        code="10001",
        date=date(2026, 6, 1),
        time=time(10, 0),
        classroom="101",
        results_available=False,
        school_class=school_class,
    )


@pytest.mark.django_db
def test_subscribe_invalid_email(client):
    exam = _create_exam()
    response = client.post(
        reverse("subscribe"),
        data={"email": "invalid-email", "exam_ids": [str(exam.id)]},
    )
    assert response.status_code == 400
    assert Student.objects.count() == 0


@pytest.mark.django_db
def test_subscribe_missing_exam_ids(client):
    response = client.post(reverse("subscribe"), data={"email": "user@example.com"})
    assert response.status_code == 400
    assert Student.objects.count() == 0


@pytest.mark.django_db
def test_subscribe_invalid_exam_ids(client):
    response = client.post(
        reverse("subscribe"),
        data={"email": "user@example.com", "exam_ids": ["not-an-int"]},
    )
    assert response.status_code == 400
    assert Student.objects.count() == 0


@pytest.mark.django_db
def test_subscribe_exam_not_found(client):
    response = client.post(
        reverse("subscribe"),
        data={"email": "user@example.com", "exam_ids": ["99999"]},
    )
    assert response.status_code == 400
    assert Student.objects.count() == 0


@pytest.mark.django_db
def test_subscribe_creates_student_and_subscription(client):
    exam = _create_exam()
    response = client.post(
        reverse("subscribe"),
        data={"email": "User@Example.com", "exam_ids": [str(exam.id)]},
    )
    assert response.status_code == 302

    student = Student.objects.get()
    expected_email = "user@example.com"
    expected_hash = hmac.new(
        settings.SECRET_KEY.encode(), expected_email.encode(), hashlib.sha256
    ).hexdigest()

    assert student.email_hash == expected_hash
    assert (
        Fernet(settings.FERNET_KEY).decrypt(student.email_encrypted.encode()).decode()
        == expected_email
    )
    assert StudentExamSubscription.objects.filter(student=student, exam=exam).count() == 1

    response = client.post(
        reverse("subscribe"),
        data={"email": expected_email, "exam_ids": [str(exam.id)]},
    )
    assert response.status_code == 302
    assert StudentExamSubscription.objects.filter(student=student, exam=exam).count() == 1


@patch("subscriptions.emails.email_on_exam_change_task.delay")
@pytest.mark.django_db
def test_email_on_exam_change_queues_task(mock_delay):
    exam = _create_exam()
    old_exam = Exam(
        name="Old exam",
        code=exam.code,
        date=exam.date,
        time=exam.time,
        classroom=exam.classroom,
        results_available=exam.results_available,
        school_class=exam.school_class,
    )

    email_on_exam_change(old_exam, exam)

    assert mock_delay.call_count == 1
    kwargs = mock_delay.call_args.kwargs
    assert kwargs["exam_id"] == exam.pk
    assert "Sprememba pri predmetu" in kwargs["subject"]
    assert str(exam.code) in kwargs["message"]