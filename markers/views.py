from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import MapMarker
from .serializers import MapMarkerSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def markers(request):
    qs = MapMarker.objects.filter(is_active=True).order_by("id")
    category = request.query_params.get("category")
    if category:
        qs = qs.filter(category=category)
    return Response(MapMarkerSerializer(qs, many=True).data)
