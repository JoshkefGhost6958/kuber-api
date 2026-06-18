from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("auth/otp/request", views.otp_request),
    path("auth/otp/verify", views.otp_verify),
    path("auth/token/refresh", TokenRefreshView.as_view()),
    path("me", views.me),
]
