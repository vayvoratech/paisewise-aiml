from services.stock_discovery import discover_stocks


def test_level_below_five_returns_no_stocks():
    result = discover_stocks("1", "beginner", 4, ["it"])
    assert result["stocks"] == []


def test_beginner_excludes_fno_and_penny():
    result = discover_stocks("1", "beginner", 5, ["it"])
    assert len(result["stocks"]) <= 5
    assert all(item["is_penny"] == "false" for item in result["stocks"])
    assert all(item["is_fno"] == "false" for item in result["stocks"])


def test_it_learning_surfaces_it_stocks():
    result = discover_stocks("1", "moderate", 5, ["it", "sector_performance"])
    assert result["stocks"]
    assert result["stocks"][0]["sector"] == "IT"


def test_advanced_can_see_fno_examples():
    result = discover_stocks("1", "advanced", 8, ["banking_sector_basics"])
    assert len(result["stocks"]) == 5
