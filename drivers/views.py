from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User

from .models import DriverProfile
from .serializers import DriverProfileSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register(request):
    user = request.user
    if request.data.get("name"):
        user.name = request.data["name"]
    user.role = User.Role.DRIVER
    user.save(update_fields=["name", "role"])
    profile, _ = DriverProfile.objects.get_or_create(user=user)
    return Response(DriverProfileSerializer(profile).data)
