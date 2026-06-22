from django.contrib import admin

from .models import DocumentRequirement, FareRoute, VehicleType

admin.site.register(VehicleType)
admin.site.register(DocumentRequirement)


@admin.register(FareRoute)
class FareRouteAdmin(admin.ModelAdmin):
    list_display = ["origin", "destination", "price", "vehicle_type", "is_active"]
    list_filter = ["is_active", "vehicle_type"]
    search_fields = ["origin", "destination"]
    list_editable = ["price", "is_active"]
