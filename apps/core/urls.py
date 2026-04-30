from django.urls import path

from core.views import index, select_exams, select_major, subscribe

urlpatterns = [
    path("", index, name="index"),
    path("izberi-smer/", select_major, name="select_major"),
    path("izberi-izpite/<int:major_id>/", select_exams, name="select_exams"),
    path("naroci-me/", subscribe, name="subscribe"),
]
