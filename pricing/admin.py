from django.contrib import admin

from .models import DocumentRequirement, VehicleType

admin.site.register(VehicleType)
admin.site.register(DocumentRequirement)
