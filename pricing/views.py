from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import DocumentRequirement, VehicleType
from .serializers import DocumentRequirementSerializer, VehicleTypeSerializer
from .services import compute_fare, lookup_fare


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


@api_view(["GET"])
@permission_classes([AllowAny])
def fare(request):
    """Look up the collected flat fare between two named places.

    Fuzzy, case-insensitive match in both directions so "Mbuni Hostel" hits an
    origin stored as "Mbuni". Returns the cheapest active match, or price=null.
    """
    frm = request.query_params.get("from") or ""
    to = request.query_params.get("to") or ""
    if not frm.strip() or not to.strip():
        return Response({"detail": "from and to are required"}, status=400)
    base = lookup_fare(frm, to)
    return Response({**compute_fare(base), "from": frm, "to": to})
