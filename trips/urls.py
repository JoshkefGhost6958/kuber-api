from django.urls import path

from . import views

urlpatterns = [
    path("trips", views.create_trip),
    path("trips/<int:pk>", views.trip_detail),
    path("trips/<int:pk>/cancel", views.cancel_trip),
    path("trips/<int:pk>/accept", views.accept_trip),
    path("trips/<int:pk>/status", views.update_status),
    path("driver/requests", views.driver_requests),
]
