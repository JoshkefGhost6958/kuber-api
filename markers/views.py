from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import MapMarker
from .serializers import MapMarkerSerializer


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def markers(request):
    if request.method == "POST":
        # Field data collection — staff only.
        user = request.user
        if not (user and user.is_authenticated and user.is_staff):
            return Response({"detail": "Staff access required."}, status=403)
        s = MapMarkerSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        marker = s.save(created_by=user)
        return Response(MapMarkerSerializer(marker).data, status=201)

    qs = MapMarker.objects.filter(is_active=True).order_by("id")
    category = request.query_params.get("category")
    if category:
        qs = qs.filter(category=category)
    return Response(MapMarkerSerializer(qs, many=True).data)
