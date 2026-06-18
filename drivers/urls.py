from django.urls import path

from . import views

urlpatterns = [
    path("drivers/register", views.register),
    path("drivers/me/vehicles", views.vehicles),
    path("drivers/me/vehicles/<int:pk>", views.vehicle_detail),
]
