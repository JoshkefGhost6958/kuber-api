from django.contrib import admin

from .models import Trip


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "passenger",
        "driver",
        "origin_label",
        "dest_label",
        "status",
        "client_total",
        "driver_payout",
        "platform_cut",
        "created_at",
    ]
    list_filter = ["status", "payment_method"]
    search_fields = ["origin_label", "dest_label"]
