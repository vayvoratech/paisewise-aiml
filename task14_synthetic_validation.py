"""Generate and validate a deterministic 100-user synthetic feature fixture.

This standalone harness creates synthetic source events, stores expected feature
values in a golden fixture, recomputes features from those events, and compares
the results. It does not test the production feature-generation pipeline.
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5


SEED = 140026
USER_COUNT = 100
AS_OF = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)

FIXTURE_NAME = "task14_synthetic_fixture.json"
REPORT_NAME = "task14_synthetic_audit_report.json"

ACTIVE_EVENT_TYPES = {
    "session",
    "lesson_completed",
    "quiz_attempt",
    "jargon_tap",
    "paper_trade",
    "investment",
}


def to_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))

    if parsed.tzinfo is None:
        raise ValueError(f"Timestamp must include a timezone: {value}")

    return parsed.astimezone(timezone.utc)


def make_event_time(
    rng: random.Random,
    as_of: datetime,
    age_days: int,
) -> str:
    event_day = as_of.date() - timedelta(days=age_days)
    event_hour = rng.randint(7, 21)
    event_minute = rng.randint(0, 59)

    event_time = datetime.combine(
        event_day,
        time(event_hour, event_minute),
        timezone.utc,
    )
    return to_iso(event_time)


def calculate_streaks(
    active_days: set[date],
    as_of_day: date,
) -> tuple[int, int]:
    if not active_days:
        return 0, 0

    current_streak = 0
    day = as_of_day

    while day in active_days:
        current_streak += 1
        day -= timedelta(days=1)

    longest_streak = 0
    current_run = 0
    previous_day: date | None = None

    for active_day in sorted(active_days):
        if (
            previous_day is not None
            and active_day == previous_day + timedelta(days=1)
        ):
            current_run += 1
        else:
            current_run = 1

        longest_streak = max(longest_streak, current_run)
        previous_day = active_day

    return current_streak, longest_streak


def reference_features(
    user: dict[str, Any],
    as_of: datetime,
) -> dict[str, Any]:
    """Build the expected golden feature values for a generated user."""
    events = [
        event
        for event in user["events"]
        if parse_time(event["occurred_at"]) <= as_of
    ]
    registration = parse_time(user["registered_at"])

    lessons = [
        event for event in events
        if event["event_type"] == "lesson_completed"
    ]
    quizzes = [
        event for event in events
        if event["event_type"] == "quiz_attempt"
    ]
    sessions = [
        event for event in events
        if event["event_type"] == "session"
    ]
    jargon_taps = [
        event for event in events
        if event["event_type"] == "jargon_tap"
    ]
    trades = [
        event for event in events
        if event["event_type"] == "paper_trade"
    ]
    investments = [
        event for event in events
        if (
            event["event_type"] == "investment"
            and event.get("status") == "COMPLETED"
        )
    ]
    notifications_sent = [
        event for event in events
        if event["event_type"] == "notification_sent"
    ]
    notification_opens = {
        event["notification_id"]
        for event in events
        if event["event_type"] == "notification_opened"
    }

    cutoff_7d = as_of - timedelta(days=7)
    cutoff_30d = as_of - timedelta(days=30)

    def in_window(
        rows: list[dict[str, Any]],
        cutoff: datetime,
    ) -> list[dict[str, Any]]:
        return [
            event
            for event in rows
            if parse_time(event["occurred_at"]) >= cutoff
        ]

    active_days = {
        parse_time(event["occurred_at"]).date()
        for event in events
        if event["event_type"] in ACTIVE_EVENT_TYPES
    }
    current_streak, longest_streak = calculate_streaks(
        active_days,
        as_of.date(),
    )

    quiz_scores = [float(event["score"]) for event in quizzes]
    sent_30d = in_window(notifications_sent, cutoff_30d)
    sent_30d_ids = {
        event["notification_id"]
        for event in sent_30d
    }

    if sent_30d_ids:
        notification_open_rate = round(
            sum(
                notification_id in notification_opens
                for notification_id in sent_30d_ids
            )
            / len(sent_30d_ids),
            4,
        )
    else:
        notification_open_rate = 0.0

    if active_days:
        days_since_last_active = max(
            0,
            (as_of.date() - max(active_days)).days,
        )
    else:
        days_since_last_active = max(
            0,
            (as_of.date() - registration.date()).days,
        )

    return {
        "lessons_completed_total": len(lessons),
        "lessons_completed_7d": len(in_window(lessons, cutoff_7d)),
        "lessons_completed_30d": len(in_window(lessons, cutoff_30d)),
        "quiz_attempts_total": len(quizzes),
        "quiz_pass_rate": (
            round(
                sum(bool(event["passed"]) for event in quizzes)
                / len(quizzes),
                4,
            )
            if quizzes
            else 0.0
        ),
        "avg_quiz_score": (
            round(sum(quiz_scores) / len(quiz_scores), 4)
            if quiz_scores
            else 0.0
        ),
        "chapters_completed": len(
            {event["chapter_id"] for event in lessons}
        ),
        "jargon_taps_7d": len(in_window(jargon_taps, cutoff_7d)),
        "streak_days_current": current_streak,
        "streak_days_longest": longest_streak,
        "sessions_7d": len(
            {
                event["session_id"]
                for event in in_window(sessions, cutoff_7d)
            }
        ),
        "sessions_30d": len(
            {
                event["session_id"]
                for event in in_window(sessions, cutoff_30d)
            }
        ),
        "avg_session_duration_secs": (
            round(
                sum(
                    int(event["duration_seconds"])
                    for event in sessions
                )
                / len(sessions)
            )
            if sessions
            else 0
        ),
        "days_since_last_active": days_since_last_active,
        "days_since_registration": max(
            0,
            (as_of.date() - registration.date()).days,
        ),
        "notification_open_rate_30d": notification_open_rate,
        "paper_trades_total": len(trades),
        "paper_trades_7d": len(in_window(trades, cutoff_7d)),
        "has_real_investment": bool(investments),
    }


def materialize_features(
    user: dict[str, Any],
    as_of: datetime,
) -> dict[str, Any]:
    """Recompute features from events using a separate aggregation path."""
    events_by_type: dict[str, list[dict[str, Any]]] = {}

    for event in user["events"]:
        if parse_time(event["occurred_at"]) <= as_of:
            events_by_type.setdefault(
                event["event_type"],
                [],
            ).append(event)

    def recent_events(
        rows: list[dict[str, Any]],
        window_days: int,
    ) -> list[dict[str, Any]]:
        cutoff = as_of - timedelta(days=window_days)
        return [
            row
            for row in rows
            if parse_time(row["occurred_at"]) >= cutoff
        ]

    lessons = events_by_type.get("lesson_completed", [])
    quizzes = events_by_type.get("quiz_attempt", [])
    sessions = events_by_type.get("session", [])
    jargon_taps = events_by_type.get("jargon_tap", [])
    trades = events_by_type.get("paper_trade", [])
    notification_sends = recent_events(
        events_by_type.get("notification_sent", []),
        30,
    )
    opened_notification_ids = {
        row["notification_id"]
        for row in events_by_type.get("notification_opened", [])
    }

    active_days: set[date] = set()
    for event_type in ACTIVE_EVENT_TYPES:
        for event in events_by_type.get(event_type, []):
            active_days.add(
                parse_time(event["occurred_at"]).date()
            )

    current_streak, longest_streak = calculate_streaks(
        active_days,
        as_of.date(),
    )

    registration_date = parse_time(user["registered_at"]).date()
    quiz_count = len(quizzes)
    sent_ids = {
        row["notification_id"]
        for row in notification_sends
    }

    if active_days:
        days_since_last_active = max(
            0,
            (as_of.date() - max(active_days)).days,
        )
    else:
        days_since_last_active = max(
            0,
            (as_of.date() - registration_date).days,
        )

    return {
        "lessons_completed_total": len(lessons),
        "lessons_completed_7d": len(recent_events(lessons, 7)),
        "lessons_completed_30d": len(recent_events(lessons, 30)),
        "quiz_attempts_total": quiz_count,
        "quiz_pass_rate": (
            round(
                sum(1 for row in quizzes if row["passed"]) / quiz_count,
                4,
            )
            if quiz_count
            else 0.0
        ),
        "avg_quiz_score": (
            round(
                sum(float(row["score"]) for row in quizzes) / quiz_count,
                4,
            )
            if quiz_count
            else 0.0
        ),
        "chapters_completed": len(
            {row["chapter_id"] for row in lessons}
        ),
        "jargon_taps_7d": len(recent_events(jargon_taps, 7)),
        "streak_days_current": current_streak,
        "streak_days_longest": longest_streak,
        "sessions_7d": len(
            {
                row["session_id"]
                for row in recent_events(sessions, 7)
            }
        ),
        "sessions_30d": len(
            {
                row["session_id"]
                for row in recent_events(sessions, 30)
            }
        ),
        "avg_session_duration_secs": (
            round(
                sum(row["duration_seconds"] for row in sessions)
                / len(sessions)
            )
            if sessions
            else 0
        ),
        "days_since_last_active": days_since_last_active,
        "days_since_registration": max(
            0,
            (as_of.date() - registration_date).days,
        ),
        "notification_open_rate_30d": (
            round(
                len(sent_ids.intersection(opened_notification_ids))
                / len(sent_ids),
                4,
            )
            if sent_ids
            else 0.0
        ),
        "paper_trades_total": len(trades),
        "paper_trades_7d": len(recent_events(trades, 7)),
        "has_real_investment": any(
            row.get("status") == "COMPLETED"
            for row in events_by_type.get("investment", [])
        ),
    }


def generate_fixture() -> dict[str, Any]:
    rng = random.Random(SEED)
    users: list[dict[str, Any]] = []

    for number in range(1, USER_COUNT + 1):
        user_id = str(
            uuid5(
                NAMESPACE_URL,
                f"paisewise-task14-synthetic-user-{number:03d}",
            )
        )
        registration_age_days = rng.randint(60, 900)
        registered_at = AS_OF - timedelta(
            days=registration_age_days,
            hours=rng.randint(0, 23),
        )

        user: dict[str, Any] = {
            "user_id": user_id,
            "registered_at": to_iso(registered_at),
            "events": [],
        }
        events = user["events"]

        def random_age_days() -> int:
            return rng.randint(
                0,
                max(0, min(registration_age_days, 365)),
            )

        for index in range(rng.randint(0, 12)):
            events.append({
                "event_type": "session",
                "session_id": f"{user_id}-session-{index:02d}",
                "duration_seconds": rng.randint(45, 3600),
                "occurred_at": make_event_time(
                    rng,
                    AS_OF,
                    random_age_days(),
                ),
            })

        for _ in range(rng.randint(0, 18)):
            events.append({
                "event_type": "lesson_completed",
                "chapter_id": f"chapter-{rng.randint(1, 12):02d}",
                "occurred_at": make_event_time(
                    rng,
                    AS_OF,
                    random_age_days(),
                ),
            })

        for _ in range(rng.randint(0, 10)):
            score = rng.randint(0, 100)
            events.append({
                "event_type": "quiz_attempt",
                "score": score,
                "passed": score >= 60,
                "occurred_at": make_event_time(
                    rng,
                    AS_OF,
                    random_age_days(),
                ),
            })

        for _ in range(rng.randint(0, 16)):
            events.append({
                "event_type": "jargon_tap",
                "occurred_at": make_event_time(
                    rng,
                    AS_OF,
                    random_age_days(),
                ),
            })

        for index in range(rng.randint(0, 10)):
            notification_id = f"{user_id}-notification-{index:02d}"
            sent_at = make_event_time(
                rng,
                AS_OF,
                random_age_days(),
            )
            events.append({
                "event_type": "notification_sent",
                "notification_id": notification_id,
                "occurred_at": sent_at,
            })

            if rng.random() < 0.55:
                opened_at = parse_time(sent_at) + timedelta(
                    minutes=rng.randint(1, 180)
                )
                events.append({
                    "event_type": "notification_opened",
                    "notification_id": notification_id,
                    "occurred_at": to_iso(opened_at),
                })

        for _ in range(rng.randint(0, 14)):
            events.append({
                "event_type": "paper_trade",
                "occurred_at": make_event_time(
                    rng,
                    AS_OF,
                    random_age_days(),
                ),
            })

        for _ in range(rng.randint(0, 3)):
            events.append({
                "event_type": "investment",
                "status": (
                    "COMPLETED"
                    if rng.random() < 0.8
                    else "PENDING"
                ),
                "occurred_at": make_event_time(
                    rng,
                    AS_OF,
                    random_age_days(),
                ),
            })

        events.sort(key=lambda event: event["occurred_at"])
        user["expected_features"] = reference_features(user, AS_OF)
        users.append(user)

    return {
        "dataset": "synthetic",
        "fixture_version": 1,
        "random_seed": SEED,
        "as_of": to_iso(AS_OF),
        "synthetic_user_count": len(users),
        "users": users,
    }


def validate_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    as_of = parse_time(fixture["as_of"])
    users = fixture["users"]

    seen_ids: set[str] = set()
    mismatches: list[dict[str, Any]] = []
    event_count = 0
    feature_values_checked = 0

    for user in users:
        user_id = user["user_id"]

        if user_id in seen_ids:
            mismatches.append({
                "user_id": user_id,
                "field": "user_id",
                "reason": "duplicate",
            })

        seen_ids.add(user_id)
        event_count += len(user["events"])

        expected = user["expected_features"]
        actual = materialize_features(user, as_of)
        feature_values_checked += len(expected)

        for field, expected_value in expected.items():
            actual_value = actual.get(field)

            if actual_value != expected_value:
                mismatches.append({
                    "user_id": user_id,
                    "field": field,
                    "expected": expected_value,
                    "actual": actual_value,
                })

    passed = (
        len(users) == USER_COUNT
        and len(seen_ids) == USER_COUNT
        and not mismatches
    )

    return {
        "audit": "task14_synthetic_user_feature_validation",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "synthetic_pass" if passed else "synthetic_fail",
        "dataset_type": "synthetic",
        "fixture_version": fixture["fixture_version"],
        "random_seed": fixture["random_seed"],
        "as_of": fixture["as_of"],
        "users_checked": len(users),
        "required_users": USER_COUNT,
        "unique_users": len(seen_ids),
        "source_events_checked": event_count,
        "feature_values_checked": feature_values_checked,
        "mismatch_count": len(mismatches),
        "mismatches_sample": mismatches[:20],
        "production_feature_pipeline_tested": False,
        "real_user_audit_status": "not_completed",
        "scope_note": (
            "Synthetic source events and expected features are validated "
            "in isolation. This does not validate production ingestion or "
            "real-user feature accuracy."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Regenerate the deterministic fixture before validating it.",
    )
    args = parser.parse_args()

    output_dir = Path(__file__).resolve().parent
    fixture_path = output_dir / FIXTURE_NAME
    report_path = output_dir / REPORT_NAME

    if args.regenerate or not fixture_path.exists():
        fixture = generate_fixture()
        fixture_path.write_text(
            json.dumps(fixture, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    else:
        fixture = json.loads(
            fixture_path.read_text(encoding="utf-8")
        )

    report = validate_fixture(fixture)
    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2))
    print(f"\nFixture: {fixture_path}")
    print(f"Report:  {report_path}")

    return 0 if report["status"] == "synthetic_pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())