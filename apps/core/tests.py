from datetime import date, time

import pytest
import requests
from django.urls import reverse

from core.models import Exam, Major, PageSnapshot, Professor, SchoolClass
from core.scraper import scrape_from_major


def _create_exam():
    major = Major.objects.create(name="Test major", url="http://example.com")
    professor = Professor.objects.create(full_name="Test professor")
    school_class = SchoolClass.objects.create(name="Test class", major=major, professor=professor)
    exam = Exam.objects.create(
        name="Test exam",
        code="12345",
        date=date(2026, 6, 1),
        time=time(10, 0),
        classroom="101",
        results_available=False,
        school_class=school_class,
    )
    return major, school_class, exam


def _require_mock_server():
    try:
        response = requests.get("http://localhost:8001", timeout=5)
        response.raise_for_status()
    except Exception as exc:
        pytest.fail(
            "Mock server must be running on http://localhost:8001 with a valid rezultati.htm",
            pytrace=False,
        )


@pytest.mark.django_db
def test_index_view(client):
    response = client.get(reverse("index"))
    assert response.status_code == 200
    assert any(t.name == "core/index.html" for t in response.templates)


@pytest.mark.django_db
def test_select_major_view(client):
    Major.objects.create(name="Major 1", url="http://example.com")
    response = client.get(reverse("select_major"))
    assert response.status_code == 200
    assert any(t.name == "core/select-major.html" for t in response.templates)
    assert response.context["majors"].count() == 1


@pytest.mark.django_db
def test_select_exams_view(client):
    major, _, exam = _create_exam()
    response = client.get(reverse("select_exams", args=[major.id]))
    assert response.status_code == 200
    assert any(t.name == "core/select-exams.html" for t in response.templates)
    assert response.context["major"] == major
    assert exam in response.context["exams"]


@pytest.mark.django_db
def test_subscription_success_view(client):
    response = client.get(reverse("subscription_success"))
    assert response.status_code == 200
    assert any(t.name == "core/subscription-success.html" for t in response.templates)


@pytest.mark.django_db
def test_scrape_from_major_with_mock_server():
    _require_mock_server()
    major = Major.objects.create(name="Mock major", url="http://localhost:8001")

    scrape_from_major(major)

    assert SchoolClass.objects.exists()
    assert Exam.objects.exists()
    assert PageSnapshot.objects.filter(major=major).count() == 1

    scrape_from_major(major)
    assert PageSnapshot.objects.filter(major=major).count() == 1