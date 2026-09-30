"""Mock product/service catalog (Activity 3.4) used as fallback when Gemini fails.
Prices are in INR."""

CATALOG = {
    "lights": [
        ("LED Panel Light 12W", "Amazon", 450), ("Pendant Lamp", "IKEA", 1499),
        ("Designer Chandelier", "Flipkart", 4999)],
    "ceiling fans": [
        ("Crompton 1200mm Fan", "Amazon", 2199), ("Havells BLDC Fan", "Flipkart", 3899),
        ("Atomberg Renesa Fan", "Amazon", 3199)],
    "furniture": [
        ("Bean Bag Chair", "Flipkart", 1299), ("KLIPPAN 2-Seater Sofa", "IKEA", 12990),
        ("Wooden Bookshelf", "Amazon", 5499), ("Accent Armchair", "Flipkart", 7999)],
    "dining tables": [
        ("4-Seater Dining Set", "Flipkart", 8999), ("MELLTORP Table", "IKEA", 4990),
        ("Solid Wood 6-Seater", "Amazon", 18999)],
    "catering": [
        ("Veg Buffet (per guest)", "Zomato", 350), ("Mixed Party Platter (per guest)", "Swiggy", 500),
        ("Premium Multi-Cuisine (per guest)", "Zomato", 900)],
    "decoration": [
        ("Balloon & Banner Kit", "Amazon", 1200), ("Fairy Light + Backdrop Set", "Flipkart", 3500),
        ("Full Theme Decoration", "Swiggy", 12000)],
    "entertainment": [
        ("Bluetooth Speaker + Playlist", "Amazon", 2500), ("DJ (3 hours)", "Zomato", 9000),
        ("Live Band (2 hours)", "Zomato", 25000)],
    "venue & stay": [
        ("Budget Party Room", "OYO", 3000), ("Banquet Hall (4 hours)", "OYO", 15000)],
    "jewelry": [
        ("Oxidised Silver Earrings", "Amazon", 599), ("Kundan Necklace Set", "Flipkart", 2499),
        ("Pearl Pendant Set", "Amazon", 3999), ("Gold-Plated Bridal Set", "Flipkart", 8999),
        ("Diamond-Look Studs", "Amazon", 1499)],
}


def pick(category, allowance):
    """Best (most expensive) item that fits the allowance, else the cheapest one."""
    options = sorted(CATALOG[category], key=lambda x: x[2])
    fitting = [o for o in options if o[2] <= allowance]
    return (fitting[-1], True) if fitting else (options[0], False)
