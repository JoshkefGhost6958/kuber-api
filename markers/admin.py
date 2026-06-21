from django.contrib import admin

from .models import MapMarker


@admin.register(MapMarker)
class MapMarkerAdmin(admin.ModelAdmin):
    change_form_template = "admin/markers/mapmarker/change_form.html"
    list_display = ["label", "category", "latitude", "longitude", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["label", "notes"]

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
