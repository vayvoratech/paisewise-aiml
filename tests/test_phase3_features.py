from app.services.portfolio_diversification_service import PortfolioDiversificationService
from app.services.churn_model_service import ChurnModelService
from app.services.news_context_service import NewsContextService


def test_diversification_service():
    result = PortfolioDiversificationService().analyze([
        {"symbol": "A", "sector": "IT", "current_value": 50},
        {"symbol": "B", "sector": "Banking", "current_value": 30},
        {"symbol": "C", "sector": "Pharma", "current_value": 20},
    ])
    assert 0 <= result["diversification_score"] <= 100
    assert result["concentrated_bets"] == ["A"]


def test_churn_model_training(tmp_path):
    output = tmp_path / "model.pkl"
    metrics = ChurnModelService().train("data/churn/churn_training_dataset.csv", str(output))
    assert output.exists()
    assert 0 <= metrics["auc_roc"] <= 1
    assert 0 <= metrics["top_20_precision"] <= 1


def test_news_enrichment_without_external_calls():
    service = NewsContextService()
    result = service.enrich([{"title": "Technology growth is strong", "description": "Positive results"}])
    assert result[0]["sector"] in service.SECTORS or result[0]["sector"] == "Other"
    assert "sentiment" in result[0]
