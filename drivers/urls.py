from django.urls import path

from . import views

urlpatterns = [
    path("drivers/register", views.register),
]
