import json
import urllib.parse
import urllib.request

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

GOOGLE = "https://maps.googleapis.com/maps/api"


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "kuber-api"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read().decode())


@api_view(["GET"])
@permission_classes([AllowAny])
def autocomplete(request):
    """Proxy Google Places Autocomplete (key stays server-side), biased to the
    rider's area and restricted to Kenya."""
    key = settings.GOOGLE_PLACES_API_KEY
    q = (request.query_params.get("q") or "").strip()
    if not key or len(q) < 2:
        return Response([])
    params = {"input": q, "key": key, "components": "country:ke"}
    lat, lng = request.query_params.get("lat"), request.query_params.get("lng")
    if lat and lng:
        params["location"] = f"{lat},{lng}"
        params["radius"] = "30000"
    try:
        data = _get(
            f"{GOOGLE}/place/autocomplete/json?" + urllib.parse.urlencode(params)
        )
    except Exception:
        return Response([])
    preds = [
        {"description": p.get("description"), "place_id": p.get("place_id")}
        for p in data.get("predictions", [])
    ]
    return Response(preds)


@api_view(["GET"])
@permission_classes([AllowAny])
def nearest(request):
    """Nearest named place (POI) to a coordinate, for labeling the rider."""
    key = settings.GOOGLE_PLACES_API_KEY
    lat, lng = request.query_params.get("lat"), request.query_params.get("lng")
    if not key or not lat or not lng:
        return Response({"name": None})
    params = {
        "location": f"{lat},{lng}",
        "rankby": "distance",
        "type": "establishment",
        "key": key,
    }
    try:
        data = _get(
            f"{GOOGLE}/place/nearbysearch/json?" + urllib.parse.urlencode(params)
        )
        results = data.get("results", [])
        name = results[0].get("name") if results else None
    except Exception:
        name = None
    return Response({"name": name})
