from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import DocumentRequirement, VehicleType
from .serializers import DocumentRequirementSerializer, VehicleTypeSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def vehicle_types(_request):
    qs = VehicleType.objects.filter(is_active=True).order_by("id")
    return Response(VehicleTypeSerializer(qs, many=True).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def document_requirements(request):
    code = request.query_params.get("vehicle_type")
    qs = DocumentRequirement.objects.filter(vehicle_type__code=code)
    return Response(DocumentRequirementSerializer(qs, many=True).data)
