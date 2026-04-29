from django.urls import path

from core.views import index, select_exams, select_major, subscribe

urlpatterns = [
    path("", index, name="index"),
    path("izbira-smeri/", select_major, name="select_major"),
    path("izbira-izpitov/<int:major_id>/", select_exams, name="select_exams"),
    path("subscribe/", subscribe, name="subscribe"),
]
