from rest_framework.permissions import BasePermission


class IsDriver(BasePermission):
    message = "Driver profile required."

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(
            request.user, "driver_profile"
        )
