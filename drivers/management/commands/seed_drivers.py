from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from drivers.models import DriverProfile, Vehicle
from pricing.models import VehicleType

# Dummy drivers positioned around Nairobi, ready to appear as online cars.
SEED = [
    ("+254700100001", "Otieno Boda", "MOTORBIKE", "Boxer", "150", "Red", "KMEA001A", -1.2649, 36.8030),
    ("+254700100002", "Wanjiru Cab", "STANDARD", "Toyota", "Fielder", "Silver", "KMEB002B", -1.2906, 36.7820),
    ("+254700100003", "Kamau Express", "MINI", "Toyota", "Vitz", "White", "KMEC003C", -1.2864, 36.8172),
    ("+254700100004", "Achieng XL", "XL", "Toyota", "Noah", "Grey", "KMED004D", -1.2700, 36.8100),
    ("+254700100005", "Mwangi Boda", "MOTORBIKE", "TVS", "HLX", "Blue", "KMEE005E", -1.2950, 36.7900),
    ("+254700100006", "Njeri Ride", "STANDARD", "Mazda", "Demio", "Black", "KMEF006F", -1.2820, 36.8230),
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
