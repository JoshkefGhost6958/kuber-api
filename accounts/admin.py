from django.contrib import admin

from .models import OtpCode, PassengerProfile, User

admin.site.register(User)
admin.site.register(PassengerProfile)
admin.site.register(OtpCode)
