from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health(_request):
    return Response({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("v1/health/", health),
    path("v1/", include("accounts.urls")),
    path("v1/", include("pricing.urls")),
    path("v1/", include("drivers.urls")),
    path("v1/", include("markers.urls")),
    path("v1/", include("places.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
