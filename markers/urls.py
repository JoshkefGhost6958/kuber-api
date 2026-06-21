from django.urls import path

from . import views

urlpatterns = [
    path("markers", views.markers),
]
