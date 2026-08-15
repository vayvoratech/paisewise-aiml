import hashlib
from uuid import UUID


def assign_recommendation_variant(user_id: UUID) -> str:
    """
    Assign a user to a stable A/B recommendation variant.
    The same user always receives the same variant.
    """

    hash_value = hashlib.sha256(
        str(user_id).encode("utf-8")
    ).hexdigest()

    bucket = int(hash_value, 16) % 100

    if bucket < 50:
        return "A"

    return "B"