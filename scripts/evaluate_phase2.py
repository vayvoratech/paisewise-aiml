"""Week 15 evaluation across all five Phase 2 model/features."""
from pathlib import Path
import sys
import json
import random
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.fund_recommendation import get_top_recommendations
from app.services.lesson_personalization import build_user_learning_profile, generate_learning_path
from app.services.fraud_detection import evaluate_fraud_event
from app.services.sip_coach import coach_sip
from app.services.stock_discovery import discover_stocks

REPORT = ROOT / "reports" / "phase2_model_evaluation.md"


def sample_funds():
    funds = []
    for i in range(30):
        funds.append({
            "scheme_name": f"Sample Fund {i+1}", "amc_name": f"AMC {i%8}",
            "category": ["large cap", "debt", "hybrid", "index"][i % 4],
            "sub_category": "", "scheme_type": "open ended", "risk_level": ["low", "moderate", "high"][i % 3],
            "returns_1y": 6 + i % 15, "returns_3y": 7 + i % 12, "returns_5y": 8 + i % 10,
            "expense_ratio": 0.5 + (i % 8) * 0.1, "fund_size_cr": 1000 + i * 100,
            "min_lumpsum": 1000, "is_tax_saver": False,
        })
    return funds


def time_call(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    return result, (time.perf_counter() - start) * 1000


def evaluate_funds():
    results = []
    funds = sample_funds()
    for i in range(30):
        _, ms = time_call(get_top_recommendations, funds, ["beginner", "moderate", "advanced"][i % 3], 2 + i % 8, 5000 + i * 1000, ["house", "retirement", "education"][i % 3])
        results.append(ms)
    return {"cases": 30, "avg_ms": round(sum(results) / len(results), 2), "max_ms": round(max(results), 2)}


def evaluate_fraud():
    random.seed(42)
    flagged = 0
    for _ in range(50):
        event = {
            "device_changed": random.random() < 0.15,
            "location_changed": random.random() < 0.10,
            "time_since_registration": random.randint(1, 1000),
            "order_value": random.choice([1000, 5000, 10000, 60000, 100000]),
            "orders_last_30min": random.randint(0, 15),
            "failed_mpin_count_24hr": random.randint(0, 5),
            "login_count_today": random.randint(0, 5),
        }
        flagged += int(evaluate_fraud_event(event)["is_anomaly"])
    return {"cases": 50, "flagged_cases": flagged}


def evaluate_lessons():
    results = []
    for i in range(10):
        attempts = [{"quiz_name": "volume", "score": 45 + i * 5}, {"quiz_name": "resistance", "score": 70 + i * 2}]
        sessions = [{"time_of_day": "evening", "lesson_format": "video"}]
        profile = build_user_learning_profile(attempts, sessions)
        path = generate_learning_path(["resistance"], {"resistance": 75}, 3)
        results.append((profile, path))
    return {"profiles": 10, "paths_generated": sum(bool(x[1]) for x in results)}


def evaluate_sip():
    statuses = []
    for i in range(20):
        result = coach_sip({
            "userId": str(i + 1), "monthlySIP": 5000 + i * 500,
            "targetAmount": 300000 + i * 25000, "currentAmount": i * 10000,
            "monthsRemaining": 12 + i, "expectedAnnualReturn": 10.0,
        })
        statuses.append(result["status"])
    return {"scenarios": 20, "statuses": sorted(set(statuses))}


def evaluate_stocks():
    counts = []
    for i in range(15):
        result = discover_stocks(str(i + 1), ["beginner", "moderate", "advanced"][i % 3], 5 + i % 6, ["it", "banking", "pharma"][i % 3])
        counts.append(len(result["stocks"]))
    return {"profiles": 15, "min_stocks_returned": min(counts), "max_stocks_returned": max(counts)}


def main():
    report = {
        "fund_recommender": evaluate_funds(),
        "fraud_detector": evaluate_fraud(),
        "lesson_personalizer": evaluate_lessons(),
        "sip_coach": evaluate_sip(),
        "stock_discovery": evaluate_stocks(),
    }
    REPORT.parent.mkdir(exist_ok=True)
    lines = ["# Phase 2 Week 15 Model Evaluation", "", "| Component | Required cases | Result |", "|---|---:|---|"]
    lines.append(f"| Fund recommender | 30 profiles | avg {report['fund_recommender']['avg_ms']} ms, max {report['fund_recommender']['max_ms']} ms |")
    lines.append(f"| Fraud detector | 50 scenarios | {report['fraud_detector']['flagged_cases']} flagged |")
    lines.append(f"| Lesson personalizer | 10 profiles | {report['lesson_personalizer']['paths_generated']} paths generated |")
    lines.append(f"| SIP coach | 20 scenarios | statuses: {', '.join(report['sip_coach']['statuses'])} |")
    lines.append(f"| Stock discovery | 15 profiles | {report['stock_discovery']['min_stocks_returned']}-{report['stock_discovery']['max_stocks_returned']} stocks returned |")
    lines += ["", "## Notes", "- Evaluation uses deterministic synthetic profiles/scenarios.", "- It checks implementation behavior and latency locally; external Spring Boot, Kafka, Redis, PostgreSQL and deployment verification still require the environment to be running."]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Report saved to {REPORT}")


if __name__ == "__main__":
    main()
