# Week 6 task: city_tier is derived from the user's KYC city.
# This is a simple, common classification used by most Indian fintech
# apps. It is not official government data, just a practical mapping.

TIER_1_CITIES = {
    "mumbai",
    "delhi",
    "bengaluru",
    "bangalore",
    "hyderabad",
    "chennai",
    "kolkata",
    "pune",
    "ahmedabad",
}

TIER_2_CITIES = {
    "jaipur",
    "lucknow",
    "kanpur",
    "nagpur",
    "indore",
    "thane",
    "bhopal",
    "visakhapatnam",
    "patna",
    "vadodara",
    "surat",
    "coimbatore",
    "kochi",
    "chandigarh",
    "guwahati",
    "nashik",
}


def get_city_tier(city):
    """Return 'tier_1', 'tier_2', 'tier_3' or None if city is unknown."""
    if not city:
        return None

    normalized = city.strip().lower()

    if normalized in TIER_1_CITIES:
        return "tier_1"

    if normalized in TIER_2_CITIES:
        return "tier_2"

    return "tier_3"
