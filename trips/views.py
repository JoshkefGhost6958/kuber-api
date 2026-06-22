from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drivers.models import DriverProfile
from drivers.permissions import IsDriver
from pricing.models import VehicleType
from pricing.services import compute_fare, lookup_fare

from .models import Trip
from .serializers import TripSerializer


def _involved(user, trip):
    return user == trip.passenger or (trip.driver and trip.driver.user == user)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_trip(request):
    """Passenger requests a ride. Fare is computed from the route table."""
    d = request.data
    origin = (d.get("origin_label") or "").strip()
    dest = (d.get("dest_label") or "").strip()
    if not origin or not dest:
        return Response({"detail": "origin_label and dest_label are required"}, status=400)
    vt = VehicleType.objects.filter(code=d.get("vehicle_type")).first()
    fare = compute_fare(lookup_fare(origin, dest))
    trip = Trip.objects.create(
        passenger=request.user,
        origin_label=origin,
        dest_label=dest,
        origin_lat=d.get("origin_lat"),
        origin_lng=d.get("origin_lng"),
        dest_lat=d.get("dest_lat"),
        dest_lng=d.get("dest_lng"),
        vehicle_type=vt,
        payment_method=d.get("payment_method", "MPESA"),
        **fare,
    )
    return Response(TripSerializer(trip).data, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def trip_detail(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    if not _involved(request.user, trip):
        return Response({"detail": "Not allowed."}, status=403)
    return Response(TripSerializer(trip).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_trip(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    if not _involved(request.user, trip):
        return Response({"detail": "Not allowed."}, status=403)
    if trip.status not in (Trip.Status.COMPLETED, Trip.Status.CANCELLED):
        trip.status = Trip.Status.CANCELLED
        trip.cancelled_at = timezone.now()
        trip.save(update_fields=["status", "cancelled_at"])
    return Response(TripSerializer(trip).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDriver])
def driver_requests(request):
    """Pending ride requests for an online, approved driver (the 'notification'
    in a polling model)."""
    d = request.user.driver_profile
    if d.status != DriverProfile.Status.APPROVED or not d.is_online:
        return Response([])
    qs = Trip.objects.filter(status=Trip.Status.REQUESTED)[:20]
    return Response(TripSerializer(qs, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsDriver])
def accept_trip(request, pk):
    """First online driver to accept wins (atomic)."""
    d = request.user.driver_profile
    if d.status != DriverProfile.Status.APPROVED:
        return Response({"detail": "Driver not approved."}, status=403)
    with transaction.atomic():
        trip = get_object_or_404(Trip.objects.select_for_update(), pk=pk)
        if trip.status != Trip.Status.REQUESTED:
            return Response({"detail": "This ride was already taken."}, status=409)
        trip.driver = d
        trip.status = Trip.Status.ACCEPTED
        trip.accepted_at = timezone.now()
        trip.save(update_fields=["driver", "status", "accepted_at"])
    return Response(TripSerializer(trip).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsDriver])
def update_status(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    if not trip.driver or trip.driver.user != request.user:
        return Response({"detail": "Not your trip."}, status=403)
    allowed = {
        Trip.Status.ARRIVING,
        Trip.Status.ARRIVED,
        Trip.Status.IN_PROGRESS,
        Trip.Status.COMPLETED,
    }
    new = request.data.get("status")
    if new not in allowed:
        return Response({"detail": "Invalid status."}, status=400)
    trip.status = new
    if new == Trip.Status.COMPLETED:
        trip.completed_at = timezone.now()
    trip.save(update_fields=["status", "completed_at"])
    return Response(TripSerializer(trip).data)
