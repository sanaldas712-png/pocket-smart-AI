"""Gemini integration (Milestone 1) + fallback recommendations (Activity 5.4)."""
import json
import os
import re

from mock_data import pick

SYSTEM = (
    "You are PocketSmart AI, a budget-aware shopping and planning assistant for India. "
    "Recommend real, commonly available products/services from platforms such as Amazon, "
    "Flipkart, IKEA, Swiggy, Zomato and OYO. Prices are in INR. "
    "The total of all item prices MUST NOT exceed the user's budget."
)
SCHEMA = (
    'Return ONLY valid JSON: {"summary": string, "items": [{"category": string, '
    '"name": string, "platform": string, "price": number, "reason": string}]}'
)
_client = None


def _get_client():
    global _client
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return None
    if _client is None:
        from google import genai
        _client = genai.Client(api_key=key)
    return _client


def build_prompt(kind, d):
    if kind == "home":
        body = (f"Home interior plan. Budget: {d['budget']}. Rooms: {', '.join(d['rooms']) or 'any'}. "
                f"Quantities - lights: {d['lights']}, ceiling fans: {d['fans']}, "
                f"furniture pieces: {d['furniture']}, dining tables: {d['dining_tables']}. "
                f"Preferences: {d['notes'] or 'none'}. Balance functionality, style and price.")
    elif kind == "party":
        body = (f"Party plan. Budget: {d['budget']}. Guests: {d['guests']}. Event: {d['event_type']}. "
                f"Venue: {d['venue'] or 'not decided'}. Split the budget across catering, decoration "
                f"and entertainment (add venue/stay only if needed). Notes: {d['notes'] or 'none'}.")
    else:
        body = (f"Jewelry plan. Budget: {d['budget']}. Occasion: {d['occasion']}. "
                f"Style: {d['style'] or 'any'}. If an outfit image is attached, match its colours.")
    return f"{body}\n{SCHEMA}"


def _parse(text):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(text)


def _validate(result, budget):
    items = result.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("no items")
    clean = []
    for it in items:
        price = float(it["price"])
        clean.append({"category": str(it["category"]), "name": str(it["name"]),
                      "platform": str(it.get("platform", "")), "price": round(price),
                      "reason": str(it.get("reason", ""))})
    total = sum(i["price"] for i in clean)
    if total > budget:
        raise ValueError("over budget")
    return {"summary": str(result.get("summary", "")), "items": clean}


def call_gemini(kind, data):
    client = _get_client()
    if client is None:
        raise RuntimeError("GEMINI_API_KEY not set")
    from google.genai import types
    parts = [build_prompt(kind, data)]
    if kind == "jewelry" and data.get("image"):
        parts.append(types.Part.from_bytes(data=data["image"][0], mime_type=data["image"][1]))
    resp = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=parts,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM, response_mime_type="application/json", temperature=0.4),
    )
    return _parse(resp.text)


# ---------- fallback (used when AI is unavailable or returns bad output) ----------
def _line(category, allowance, qty=1):
    (name, platform, price), fits = pick(category, allowance / max(qty, 1))
    label = f"{name} x{qty}" if qty > 1 else name
    reason = "Best fit within your allocation." if fits else "Cheapest option available; allocation is tight."
    return {"category": category, "name": label, "platform": platform,
            "price": price * qty, "reason": reason}


def _allocate(budget, weights, qtys=None):
    total_w = sum(weights.values())
    qtys = qtys or {}
    return [_line(cat, budget * w / total_w, qtys.get(cat, 1)) for cat, w in weights.items()]


def fallback(kind, d):
    if kind == "home":
        qty = {"lights": d["lights"], "ceiling fans": d["fans"],
               "furniture": d["furniture"], "dining tables": d["dining_tables"]}
        base = {"lights": 15, "ceiling fans": 20, "furniture": 40, "dining tables": 25}
        weights = {k: v for k, v in base.items() if qty[k] > 0}
        items = _allocate(d["budget"], weights, qty)
    elif kind == "party":
        weights = {"catering": 50, "decoration": 25, "entertainment": 15}
        if d["venue"]:
            weights["venue & stay"] = 10
        items = _allocate(d["budget"], weights, {"catering": d["guests"]})
    else:
        items = [_line("jewelry", d["budget"])]
    return {"summary": "Default recommendations (AI was unavailable).", "items": items}


def recommend(kind, data):
    try:
        result = _validate(call_gemini(kind, data), data["budget"])
        source = "gemini"
    except Exception:
        result, source = fallback(kind, data), "fallback"
    total = sum(i["price"] for i in result["items"])
    result.update(source=source, budget=data["budget"], total=total,
                  remaining=data["budget"] - total, over_budget=total > data["budget"])
    return result
