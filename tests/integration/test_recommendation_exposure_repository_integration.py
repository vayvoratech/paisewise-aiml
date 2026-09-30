from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.db.session import get_db
from app.repositories.recommendation_exposure_repository import (
    RecommendationExposureRepository,
)


def test_recommendation_exposure_repository_integration():
    user_id = uuid4()
    scheme_code = f"TEST{uuid4().hex[:16]}"

    repository = RecommendationExposureRepository()

    try:
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO auth.users (
                        id,
                        phone,
                        name,
                        password_hash
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        user_id,
                        f"test-{uuid4().hex[:20]}",
                        "Recommendation Test User",
                        "test-password-hash",
                    ),
                )

                cursor.execute(
                    """
                    INSERT INTO mf_schemes (
                        scheme_code,
                        scheme_name,
                        amc_name,
                        category,
                        scheme_type
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        scheme_code,
                        "Temporary Recommendation Test Fund",
                        "Temporary Test AMC",
                        "Equity",
                        "Open Ended",
                    ),
                )

        recorded_at = datetime.now(timezone.utc)

        result = repository.record_exposure(
            user_id=str(user_id),
            scheme_code=scheme_code,
            amc_name="Temporary Test AMC",
            recommendation_rank=1,
            recommendation_source="integration_test",
            recommended_at=recorded_at,
        )

        assert result["user_id"] == user_id
        assert result["scheme_code"] == scheme_code
        assert result["amc_name"] == "Temporary Test AMC"
        assert result["recommendation_rank"] == 1
        assert result["recommendation_source"] == "integration_test"

        exposures = repository.get_recent_user_exposures(
            str(user_id),
            days=28,
        )

        assert len(exposures) == 1
        assert exposures[0]["scheme_code"] == scheme_code

        count = repository.get_user_scheme_exposure_count(
            str(user_id),
            scheme_code,
            days=28,
        )

        assert count == 1

        month_start = recorded_at - timedelta(days=1)
        month_end = recorded_at + timedelta(days=1)

        amc_exposure = repository.get_monthly_amc_exposure(
            month_start=month_start,
            month_end=month_end,
        )

        temporary_amc = next(
            (
                item
                for item in amc_exposure
                if item["amc_name"] == "Temporary Test AMC"
            ),
            None,
        )

        assert temporary_amc is not None
        assert temporary_amc["exposure_count"] == 1
        assert temporary_amc["unique_user_count"] == 1
        assert temporary_amc["unique_scheme_count"] == 1

    finally:
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM recommendation_exposures
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM mf_schemes
                    WHERE scheme_code = %s
                    """,
                    (scheme_code,),
                )

                cursor.execute(
                    """
                    DELETE FROM auth.users
                    WHERE id = %s
                    """,
                    (user_id,),
                )