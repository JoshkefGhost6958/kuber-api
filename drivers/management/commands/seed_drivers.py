from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from drivers.models import DriverProfile, Vehicle
from pricing.models import VehicleType

# Dummy drivers positioned around Kirinyaga County (Kerugoya/Kutus/Mwea/Kagio),
# ready to appear as online cars near the rider.
SEED = [
    ("+254700100001", "Otieno Boda", "BODA_ELECTRIC", "Roam", "Air", "Green", "KMEA001A", -0.4986, 37.2803),  # Kerugoya
    ("+254700100002", "Wanjiru Cab", "CAB", "Toyota", "Fielder", "Silver", "KMEB002B", -0.5530, 37.2960),  # Kutus
    ("+254700100003", "Kamau Tuktuk", "TUKTUK", "Bajaj", "RE", "Black", "KMEC003C", -0.6100, 37.3330),  # Kagio
    ("+254700100004", "Achieng Cab", "CAB", "Toyota", "Axio", "White", "KMED004D", -0.6870, 37.3740),  # Mwea/Ngurubani
    ("+254700100005", "Mwangi Boda", "BODA", "Boxer", "150", "Red", "KMEE005E", -0.5300, 37.2200),  # Baricho
    ("+254700100006", "Njeri Tuktuk", "TUKTUK", "Piaggio", "Ape", "Blue", "KMEF006F", -0.5100, 37.2900),  # near Kerugoya
]


class Command(BaseCommand):
    help = "Seed dummy APPROVED, online drivers around Nairobi (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Remove seeded dummy drivers first")

    def handle(self, *args, **opts):
        if opts["clear"]:
            User.objects.filter(phone_number__in=[s[0] for s in SEED]).delete()
            self.stdout.write("Cleared seeded dummy drivers.")

        now = timezone.now()
        created = 0
        for phone, name, vt_code, make, model, color, plate, lat, lng in SEED:
            user, _ = User.objects.get_or_create(
                phone_number=phone, defaults={"name": name, "role": User.Role.DRIVER}
            )
            user.name = name
            user.role = User.Role.DRIVER
            user.save(update_fields=["name", "role"])

            driver, made = DriverProfile.objects.get_or_create(user=user)
            driver.status = DriverProfile.Status.APPROVED
            driver.is_online = True
            driver.approved_at = now
            driver.current_lat = lat
            driver.current_lng = lng
            driver.last_location_at = now
            driver.save()

            vt = VehicleType.objects.get(code=vt_code)
            Vehicle.objects.update_or_create(
                plate_number=plate,
                defaults={
                    "driver": driver,
                    "vehicle_type": vt,
                    "make": make,
                    "model": model,
                    "color": color,
                    "year": 2020,
                    "is_active": True,
                },
            )
            created += int(made)

        total = DriverProfile.objects.filter(
            status=DriverProfile.Status.APPROVED, is_online=True
        ).count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(SEED)} dummy drivers ({created} new). "
                f"{total} approved+online drivers total."
            )
        )
