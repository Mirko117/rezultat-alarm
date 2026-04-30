from django.urls import path

from .views import index, select_exams, select_major

urlpatterns = [
    path("", index, name="index"),
    path("izberi-smer/", select_major, name="select_major"),
    path("izberi-izpite/<int:major_id>/", select_exams, name="select_exams"),
]
