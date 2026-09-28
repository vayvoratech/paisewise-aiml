import pytest

from app.repositories.recommendation_exposure_repository import (
    RecommendationExposureRepository,
)


class TestRecommendationExposureRepositoryValidation:
    def test_record_exposure_requires_user_id(self):
        with pytest.raises(ValueError, match="user_id cannot be empty"):
            RecommendationExposureRepository.record_exposure(
                user_id="",
                scheme_code="TEST001",
                amc_name="Test AMC",
                recommendation_rank=1,
                recommendation_source="content",
            )

    def test_record_exposure_requires_scheme_code(self):
        with pytest.raises(
            ValueError,
            match="scheme_code cannot be empty",
        ):
            RecommendationExposureRepository.record_exposure(
                user_id="user-1",
                scheme_code="",
                amc_name="Test AMC",
                recommendation_rank=1,
                recommendation_source="content",
            )

    def test_record_exposure_requires_amc_name(self):
        with pytest.raises(
            ValueError,
            match="amc_name cannot be empty",
        ):
            RecommendationExposureRepository.record_exposure(
                user_id="user-1",
                scheme_code="TEST001",
                amc_name="",
                recommendation_rank=1,
                recommendation_source="content",
            )

    def test_record_exposure_requires_positive_rank(self):
        with pytest.raises(
            ValueError,
            match="recommendation_rank must be greater than zero",
        ):
            RecommendationExposureRepository.record_exposure(
                user_id="user-1",
                scheme_code="TEST001",
                amc_name="Test AMC",
                recommendation_rank=0,
                recommendation_source="content",
            )

    def test_record_exposure_requires_source(self):
        with pytest.raises(
            ValueError,
            match="recommendation_source cannot be empty",
        ):
            RecommendationExposureRepository.record_exposure(
                user_id="user-1",
                scheme_code="TEST001",
                amc_name="Test AMC",
                recommendation_rank=1,
                recommendation_source="",
            )

    def test_recent_exposures_requires_user_id(self):
        repository = RecommendationExposureRepository()

        with pytest.raises(
            ValueError,
            match="user_id cannot be empty",
        ):
            repository.get_recent_user_exposures("")

    def test_recent_exposures_requires_positive_days(self):
        repository = RecommendationExposureRepository()

        with pytest.raises(
            ValueError,
            match="days must be greater than zero",
        ):
            repository.get_recent_user_exposures(
                "user-1",
                days=0,
            )

    def test_scheme_exposure_count_requires_user_id(self):
        repository = RecommendationExposureRepository()

        with pytest.raises(
            ValueError,
            match="user_id cannot be empty",
        ):
            repository.get_user_scheme_exposure_count(
                "",
                "TEST001",
            )

    def test_scheme_exposure_count_requires_scheme_code(self):
        repository = RecommendationExposureRepository()

        with pytest.raises(
            ValueError,
            match="scheme_code cannot be empty",
        ):
            repository.get_user_scheme_exposure_count(
                "user-1",
                "",
            )

    def test_monthly_amc_exposure_requires_valid_period(self):
        from datetime import datetime

        repository = RecommendationExposureRepository()

        start = datetime(2026, 1, 1)
        end = datetime(2026, 1, 1)

        with pytest.raises(
            ValueError,
            match="month_end must be greater than month_start",
        ):
            repository.get_monthly_amc_exposure(
                month_start=start,
                month_end=end,
            )