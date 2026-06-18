from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.core.exceptions import ValidationError

from accounts.models import User

from .models import ComplianceDocument, DriverProfile, Vehicle
from .permissions import IsDriver
from .serializers import (
    ComplianceDocumentSerializer,
    DriverProfileSerializer,
    VehicleSerializer,
)
from .services import build_checklist, missing_mandatory


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


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsDriver])
def documents(request):
    driver = request.user.driver_profile
    if request.method == "POST":
        doc_type = request.data.get("doc_type")
        # Re-uploading a doc type replaces the existing one (resets to PENDING).
        ComplianceDocument.objects.filter(driver=driver, doc_type=doc_type).delete()
        s = ComplianceDocumentSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.save(driver=driver)
        return Response(ComplianceDocumentSerializer(d).data, status=201)
    return Response(
        ComplianceDocumentSerializer(driver.documents.all(), many=True).data
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsDriver])
def submit(request):
    driver = request.user.driver_profile
    missing = missing_mandatory(driver)
    if missing:
        return Response(
            {"detail": "Missing mandatory documents.", "missing": missing},
            status=422,
        )
    try:
        driver.submit_for_review()
    except ValidationError as e:
        return Response({"detail": str(e)}, status=400)
    return Response({"status": driver.status})


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDriver])
def driver_me(request):
    driver = request.user.driver_profile
    return Response(
        {
            **DriverProfileSerializer(driver).data,
            "vehicles": VehicleSerializer(driver.vehicles.all(), many=True).data,
            "documents": ComplianceDocumentSerializer(
                driver.documents.all(), many=True
            ).data,
            "checklist": build_checklist(driver),
        }
    )
