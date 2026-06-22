from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import DocumentRequirement, FareRoute, VehicleType
from .serializers import (
    DocumentRequirementSerializer,
    FareRouteSerializer,
    VehicleTypeSerializer,
)


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
    frm = (request.query_params.get("from") or "").strip().lower()
    to = (request.query_params.get("to") or "").strip().lower()
    if not frm or not to:
        return Response({"detail": "from and to are required"}, status=400)

    def matches(stored: str, query: str) -> bool:
        s = stored.lower()
        return s in query or query in s

    best = None
    for r in FareRoute.objects.filter(is_active=True):
        if matches(r.origin, frm) and matches(r.destination, to):
            if best is None or r.price < best.price:
                best = r
    if not best:
        return Response({"price": None})
    return Response(FareRouteSerializer(best).data)
