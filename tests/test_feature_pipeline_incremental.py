"""
Week 6 task: "Write incremental update query (daily update, not full
refresh)."

This test builds a small in-memory SQLite database, runs the pipeline
twice, and checks that the second run only touches the user who had
new activity - not everyone in the table.
"""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.schema import Base, User, UserSession
from app.pipelines import feature_pipeline


@pytest.fixture
def in_memory_db(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(bind=engine)

    monkeypatch.setattr(feature_pipeline, "SessionLocal", TestSessionLocal)

    session = TestSessionLocal()

    user_a = User(
        user_id=1,
        full_name="User A",
        age=30,
        annual_income=500000,
        monthly_investment=5000,
        portfolio_value=20000,
        risk_profile="Moderate",
        kyc_city="Mumbai",
    )
    user_b = User(
        user_id=2,
        full_name="User B",
        age=28,
        annual_income=400000,
        monthly_investment=3000,
        portfolio_value=10000,
        risk_profile="Low",
        kyc_city="Nagpur",
    )
    session.add_all([user_a, user_b])

    session.add(
        UserSession(
            user_id=1,
            login_time=datetime.utcnow() - timedelta(days=1),
            logout_time=datetime.utcnow(),
            session_duration=600,
            screens_visited=5,
        )
    )
    session.commit()
    session.close()

    yield TestSessionLocal


def test_first_run_is_a_full_refresh_and_sets_city_tier(in_memory_db):
    updated = feature_pipeline.run_behaviour_feature_pipeline()

    # First run has no watermark yet, so both users get created.
    assert updated == 2

    session = in_memory_db()
    from app.db.schema import UserFeatures

    user_a_features = session.query(UserFeatures).filter_by(user_id=1).first()
    user_b_features = session.query(UserFeatures).filter_by(user_id=2).first()

    assert user_a_features.city_tier == "tier_1"  # Mumbai
    assert user_b_features.city_tier == "tier_2"  # Nagpur
    session.close()


def test_second_run_only_touches_user_with_new_activity(in_memory_db):
    # first run, establishes the watermark
    feature_pipeline.run_behaviour_feature_pipeline()

    session = in_memory_db()
    session.add(
        UserSession(
            user_id=2,
            login_time=datetime.utcnow(),
            logout_time=datetime.utcnow(),
            session_duration=300,
            screens_visited=3,
        )
    )
    session.commit()
    session.close()

    # second run should be incremental: only user 2 had new activity
    updated = feature_pipeline.run_behaviour_feature_pipeline()

    assert updated == 1
