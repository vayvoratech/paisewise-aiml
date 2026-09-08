from app.services.lesson_personalization import (
    analyse_completion_patterns,
    classify_lesson_difficulty,
    classify_user_lesson_difficulties,
    needs_prerequisite_review,
    get_next_lesson,
    build_user_learning_profile,
    generate_learning_path,
)


def test_completion_patterns_finds_highest_drop_off_first():
    rows = [
        {"lesson_name": "resistance", "completed": True},
        {"lesson_name": "resistance", "completed": True},
        {"lesson_name": "volume", "completed": True},
        {"lesson_name": "volume", "completed": False},
        {"lesson_name": "volume", "completed": False},
    ]

    report = analyse_completion_patterns(rows)

    assert report[0]["lesson_name"] == "volume"
    assert report[0]["drop_off_rate"] > report[1]["drop_off_rate"]


def test_classify_lesson_difficulty_buckets():
    assert classify_lesson_difficulty(85) == "easy"
    assert classify_lesson_difficulty(65) == "medium"
    assert classify_lesson_difficulty(40) == "hard"


def test_classify_user_lesson_difficulties_averages_multiple_attempts():
    attempts = [
        {"quiz_name": "volume", "score": 90},
        {"quiz_name": "volume", "score": 70},
    ]

    result = classify_user_lesson_difficulties(attempts)

    # average of 90 and 70 is 80, which is "easy" (>= 80)
    assert result["volume"] == "easy"


def test_needs_prerequisite_review_below_threshold():
    prerequisite = needs_prerequisite_review(quiz_score=50, lesson_name="52_week_high_low")
    assert prerequisite == "resistance"


def test_needs_prerequisite_review_above_threshold_returns_none():
    prerequisite = needs_prerequisite_review(quiz_score=75, lesson_name="52_week_high_low")
    assert prerequisite is None


def test_get_next_lesson_respects_prerequisites():
    completed = ["resistance", "volume"]
    scores = {"resistance": 80, "volume": 80}

    next_lesson = get_next_lesson(completed, scores)

    # pe_ratio has no prerequisites and comes before 52_week_high_low
    # in curriculum order, so it should be recommended next
    assert next_lesson == "pe_ratio"


def test_get_next_lesson_sends_back_to_prerequisite_on_weak_score():
    completed = ["resistance", "volume", "52_week_high_low"]
    scores = {"resistance": 80, "volume": 80, "52_week_high_low": 40}

    next_lesson = get_next_lesson(completed, scores)

    assert next_lesson == "resistance"


def test_build_user_learning_profile_flags_slow_learner():
    quiz_attempts = [
        {"quiz_name": "resistance", "score": 50},
        {"quiz_name": "resistance", "score": 60},
        {"quiz_name": "resistance", "score": 70},
    ]
    sessions = [
        {"time_of_day": "evening", "lesson_format": "visual"},
        {"time_of_day": "evening", "lesson_format": "text"},
    ]

    profile = build_user_learning_profile(quiz_attempts, sessions)

    assert profile["slow_learner"] is True
    assert profile["preferred_time_of_day"] == "evening"


def test_generate_learning_path_returns_three_lessons():
    completed = []
    scores = {}

    path = generate_learning_path(completed, scores, path_length=3)

    assert len(path) == 3
    assert len(set(path)) == 3  # no duplicate lessons in the path
