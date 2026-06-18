from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User

from .models import DriverProfile, Vehicle
from .permissions import IsDriver
from .serializers import DriverProfileSerializer, VehicleSerializer


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


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsDriver])
def vehicles(request):
    driver = request.user.driver_profile
    if request.method == "POST":
        s = VehicleSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        first = not driver.vehicles.exists()
        v = s.save(driver=driver, is_active=first)
        return Response(VehicleSerializer(v).data, status=201)
    return Response(VehicleSerializer(driver.vehicles.all(), many=True).data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsDriver])
def vehicle_detail(request, pk):
    driver = request.user.driver_profile
    try:
        v = driver.vehicles.get(pk=pk)
    except Vehicle.DoesNotExist:
        return Response({"detail": "Not found."}, status=404)
    if request.data.get("is_active") is True:
        driver.vehicles.update(is_active=False)
        v.is_active = True
        v.save(update_fields=["is_active"])
    return Response(VehicleSerializer(v).data)
