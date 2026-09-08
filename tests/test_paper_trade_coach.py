from app.services.paper_trade_coach import evaluate_trade, extract_trade_context


def test_trade_context_extracts_required_fields():
    context = extract_trade_context(
        {
            "symbol": "ABC",
            "side": "BUY",
            "price": 100,
            "quantity": 10,
        },
        {
            "sector": "IT",
            "52_week_high": 120,
            "52_week_low": 70,
            "volume": 1000,
            "average_volume": 900,
        },
        [{"lesson_name": "volume", "completed": True}],
    )

    assert context["symbol"] == "ABC"
    assert context["sector"] == "IT"
    assert context["52_week_high"] == 120
    assert context["average_volume"] == 900


def test_trade_evaluation_marks_missing_learning_as_needs_review():
    context = extract_trade_context(
        {"symbol": "ABC", "side": "BUY", "price": 118, "quantity": 10},
        {
            "52_week_high": 120,
            "52_week_low": 70,
            "volume": 500,
            "average_volume": 1000,
        },
        [],
    )

    result = evaluate_trade(context)

    assert result["decision"] == "needs_review"
    assert result["score"] < 70


def test_sector_studied_check_passes_when_lesson_matches_sector():
    context = extract_trade_context(
        {"symbol": "ABC", "side": "BUY", "price": 100, "quantity": 10},
        {
            "sector": "Banking",
            "52_week_high": 120,
            "52_week_low": 70,
            "volume": 1000,
            "average_volume": 900,
        },
        [
            {"lesson_name": "resistance", "completed": True},
            {"lesson_name": "volume", "completed": True},
            {"lesson_name": "banking sector basics", "completed": True},
        ],
    )

    result = evaluate_trade(context)
    sector_check = next(
        item for item in result["checks"] if item["criterion"] == "Sector studied"
    )

    assert sector_check["passed"] is True


def test_sector_studied_check_fails_when_no_matching_lesson():
    context = extract_trade_context(
        {"symbol": "ABC", "side": "BUY", "price": 100, "quantity": 10},
        {
            "sector": "Pharma",
            "52_week_high": 120,
            "52_week_low": 70,
            "volume": 1000,
            "average_volume": 900,
        },
        [
            {"lesson_name": "resistance", "completed": True},
            {"lesson_name": "volume", "completed": True},
        ],
    )

    result = evaluate_trade(context)
    sector_check = next(
        item for item in result["checks"] if item["criterion"] == "Sector studied"
    )

    assert sector_check["passed"] is False
