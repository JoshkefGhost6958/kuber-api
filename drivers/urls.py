from django.urls import path

from . import views

urlpatterns = [
    path("drivers/register", views.register),
    path("drivers/online", views.online_drivers),
    path("drivers/me", views.driver_me),
    path("drivers/me/availability", views.availability),
    path("drivers/me/location", views.update_location),
    path("drivers/me/vehicles", views.vehicles),
    path("drivers/me/vehicles/<int:pk>", views.vehicle_detail),
    path("drivers/me/documents", views.documents),
    path("drivers/me/submit", views.submit),
]
