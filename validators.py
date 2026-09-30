"""Input parsing + validation (Activity 5.3)."""
ALLOWED_IMAGES = {"image/png", "image/jpeg", "image/webp"}


def _num(form, key, label, minimum=0, required=True, default=0):
    raw = (form.get(key) or "").strip()
    if not raw:
        if required:
            raise ValueError(f"{label} is required.")
        return default
    try:
        val = float(raw)
    except ValueError:
        raise ValueError(f"{label} must be a number.")
    if val < minimum:
        raise ValueError(f"{label} must be at least {minimum}.")
    return val


def parse_home(form, files):
    data = {
        "budget": _num(form, "budget", "Total budget", 1),
        "lights": int(_num(form, "lights", "Lights", required=False)),
        "fans": int(_num(form, "fans", "Ceiling fans", required=False)),
        "furniture": int(_num(form, "furniture", "Furniture pieces", required=False)),
        "dining_tables": int(_num(form, "dining_tables", "Dining tables", required=False)),
        "rooms": form.getlist("rooms"),
        "notes": (form.get("notes") or "").strip()[:500],
    }
    if not any([data["lights"], data["fans"], data["furniture"], data["dining_tables"]]):
        raise ValueError("Enter a quantity for at least one item.")
    return data


def parse_party(form, files):
    return {
        "budget": _num(form, "budget", "Total budget", 1),
        "guests": int(_num(form, "guests", "Guest count", 1)),
        "event_type": (form.get("event_type") or "birthday").strip()[:40],
        "venue": (form.get("venue") or "").strip()[:200],
        "notes": (form.get("notes") or "").strip()[:500],
    }


def parse_jewelry(form, files):
    data = {
        "budget": _num(form, "budget", "Budget", 1),
        "occasion": (form.get("occasion") or "").strip()[:60],
        "style": (form.get("style") or "").strip()[:100],
        "image": None,
    }
    if not data["occasion"]:
        raise ValueError("Occasion is required.")
    f = files.get("outfit_image")
    if f and f.filename:
        if f.mimetype not in ALLOWED_IMAGES:
            raise ValueError("Outfit image must be PNG, JPG or WEBP.")
        data["image"] = (f.read(), f.mimetype)
    return data


PARSERS = {"home": parse_home, "party": parse_party, "jewelry": parse_jewelry}
