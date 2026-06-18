import re


def normalize_phone(raw: str) -> str:
    """Normalize a Kenyan phone number to E.164 (+254XXXXXXXXX)."""
    digits = re.sub(r"[\s\-()]", "", raw or "")
    if digits.startswith("+254") and len(digits) == 13 and digits[1:].isdigit():
        return digits
    if digits.startswith("254") and len(digits) == 12 and digits.isdigit():
        return "+" + digits
    if digits.startswith("0") and len(digits) == 10 and digits.isdigit():
        return "+254" + digits[1:]
    raise ValueError(f"Invalid Kenyan phone number: {raw!r}")
