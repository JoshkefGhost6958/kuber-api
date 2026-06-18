from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import ComplianceDocument, DriverProfile, Vehicle


@admin.register(ComplianceDocument)
class ComplianceDocumentAdmin(admin.ModelAdmin):
    list_display = ["driver", "doc_type", "status", "reviewed_at"]
    list_filter = ["status", "doc_type"]
    actions = ["approve_docs"]

    @admin.action(description="Approve selected documents")
    def approve_docs(self, request, queryset):
        for doc in queryset:
            doc.approve(by=request.user)


class VehicleInline(admin.TabularInline):
    model = Vehicle
    extra = 0


class DocInline(admin.TabularInline):
    model = ComplianceDocument
    extra = 0


@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "status", "is_online", "approved_at"]
    list_filter = ["status", "is_online"]
    inlines = [VehicleInline, DocInline]
    actions = ["approve_drivers", "suspend_drivers"]

    @admin.action(description="Approve selected drivers")
    def approve_drivers(self, request, queryset):
        for d in queryset:
            try:
                d.approve()
            except ValidationError as e:
                self.message_user(request, f"{d}: {e.message}", level=messages.ERROR)

    @admin.action(description="Suspend selected drivers")
    def suspend_drivers(self, request, queryset):
        for d in queryset:
            try:
                d.suspend()
            except ValidationError as e:
                self.message_user(request, f"{d}: {e.message}", level=messages.ERROR)


admin.site.register(Vehicle)
