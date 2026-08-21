from uuid import UUID

from services.recommendation_ab import assign_recommendation_variant


def test_same_user_gets_same_variant():
    user_id = UUID("11111111-1111-1111-1111-111111111111")

    variant1 = assign_recommendation_variant(user_id)
    variant2 = assign_recommendation_variant(user_id)

    assert variant1 == variant2


def test_variant_is_valid():
    user_id = UUID("22222222-2222-2222-2222-222222222222")

    variant = assign_recommendation_variant(user_id)

    assert variant in ["A", "B"]