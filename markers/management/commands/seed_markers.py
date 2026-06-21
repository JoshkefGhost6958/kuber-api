from django.core.management.base import BaseCommand

from markers.models import MapMarker

SEED = [
    ("Kerugoya Boda Stage", "BODA_STAGE", -0.4986, 37.2803),
    ("Kutus Tuktuk Stage", "TUKTUK_STAGE", -0.553, 37.296),
    ("Kagio Cab Rank", "CAB_RANK", -0.61, 37.333),
    ("Mwea Hub", "HUB", -0.687, 37.374),
    ("Sagana Demand Hotspot", "DEMAND", -0.664, 37.205),
    ("Kerugoya Referral Hospital", "LANDMARK", -0.499, 37.282),
]


class Command(BaseCommand):
    help = "Seed example data-collection markers around Kirinyaga (idempotent)."

    def handle(self, *args, **opts):
        created = 0
        for label, category, lat, lng in SEED:
            _, made = MapMarker.objects.get_or_create(
                label=label,
                defaults={"category": category, "latitude": lat, "longitude": lng},
            )
            created += int(made)
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded markers ({created} new). "
                f"{MapMarker.objects.filter(is_active=True).count()} active markers."
            )
        )
