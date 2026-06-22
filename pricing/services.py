from django.conf import settings

from .models import FareRoute


def lookup_fare(frm: str, to: str) -> int | None:
    """Cheapest active flat fare between two named places (fuzzy, both ways)."""
    frm, to = (frm or "").strip().lower(), (to or "").strip().lower()
    if not frm or not to:
        return None

    def matches(stored: str, query: str) -> bool:
        s = stored.lower()
        return s in query or query in s

    best = None
    for r in FareRoute.objects.filter(is_active=True):
        if matches(r.origin, frm) and matches(r.destination, to):
            if best is None or r.price < best:
                best = r.price
    return best


def compute_fare(base: int | None) -> dict:
    """Apply the platform commission model.

    Client pays base + client_fee; driver receives base - driver_fee; the
    platform keeps both fees. e.g. base 50, fees 10/5 -> client 60, driver 45,
    platform 15 (gross trip value 65).
    """
    cf = settings.PLATFORM_CLIENT_FEE
    df = settings.PLATFORM_DRIVER_FEE
    if base is None:
        return {
            "base_fare": None,
            "client_fee": cf,
            "driver_fee": df,
            "client_total": None,
            "driver_payout": None,
            "platform_cut": None,
        }
    return {
        "base_fare": base,
        "client_fee": cf,
        "driver_fee": df,
        "client_total": base + cf,
        "driver_payout": base - df,
        "platform_cut": cf + df,
    }
