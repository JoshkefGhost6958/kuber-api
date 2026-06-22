from django.urls import path

from . import views

urlpatterns = [
    path("vehicle-types", views.vehicle_types),
    path("drivers/document-requirements", views.document_requirements),
    path("fare", views.fare),
]
