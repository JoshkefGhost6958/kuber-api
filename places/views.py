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


def _decode_polyline(s: str):
    """Decode a Google encoded polyline into [lat, lng] points."""
    points, index, lat, lng = [], 0, 0, 0
    while index < len(s):
        for is_lat in (True, False):
            shift = result = 0
            while True:
                b = ord(s[index]) - 63
                index += 1
                result |= (b & 0x1F) << shift
                shift += 5
                if b < 0x20:
                    break
            delta = ~(result >> 1) if (result & 1) else (result >> 1)
            if is_lat:
                lat += delta
            else:
                lng += delta
        points.append([lat / 1e5, lng / 1e5])
    return points


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


@api_view(["GET"])
@permission_classes([AllowAny])
def directions(request):
    """Driving route + ETA between two points (coords or text)."""
    key = settings.GOOGLE_PLACES_API_KEY
    empty = {"points": [], "duration_text": None, "duration_sec": None, "distance_text": None}
    if not key:
        return Response(empty)
    p = request.query_params
    origin = (
        f"{p['from_lat']},{p['from_lng']}"
        if p.get("from_lat") and p.get("from_lng")
        else (p.get("from") or "")
    )
    dest = (
        f"{p['to_lat']},{p['to_lng']}"
        if p.get("to_lat") and p.get("to_lng")
        else (p.get("to") or "")
    )
    if not origin or not dest:
        return Response(empty)
    params = {"origin": origin, "destination": dest, "mode": "driving", "key": key}
    try:
        data = _get(f"{GOOGLE}/directions/json?" + urllib.parse.urlencode(params))
        routes = data.get("routes", [])
        if not routes:
            return Response(empty)
        leg = routes[0]["legs"][0]
        return Response(
            {
                "points": _decode_polyline(routes[0]["overview_polyline"]["points"]),
                "duration_text": leg["duration"]["text"],
                "duration_sec": leg["duration"]["value"],
                "distance_text": leg["distance"]["text"],
            }
        )
    except Exception:
        return Response(empty)
