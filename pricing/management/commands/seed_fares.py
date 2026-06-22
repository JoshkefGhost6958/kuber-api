from django.core.management.base import BaseCommand

from pricing.models import FareRoute

# Starting point: Mbuni + neighbouring hostels -> Kutus Town = KSh 50.
# Field staff extend this as drivers report stage-to-stage fares.
ORIGINS = [
    "Mbuni",
    "Joslian",
    "Real Vision One",
    "Executive Hostel",
    "Mory Hostel",
    "Mjini",
]
DESTINATION = "Kutus Town"
PRICE = 50


class Command(BaseCommand):
    help = "Seed initial driver-collected fares (idempotent)."

    def handle(self, *args, **opts):
        created = 0
        for origin in ORIGINS:
            _, made = FareRoute.objects.get_or_create(
                origin=origin,
                destination=DESTINATION,
                defaults={"price": PRICE, "notes": "Seed: hostels area to Kutus"},
            )
            created += int(made)
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded fares ({created} new). "
                f"{FareRoute.objects.filter(is_active=True).count()} active fares."
            )
        )
