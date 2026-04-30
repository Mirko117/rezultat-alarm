from django.urls import path

from .views import subscribe

urlpatterns = [
    path("naroci-me/", subscribe, name="subscribe"),
]
