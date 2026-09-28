"""
Task 14 - Model and AI Component Evaluation

Runs:
1. Existing five Task 7 component evaluation tests
2. Existing fraud-model benchmark:
   - Logistic Regression
   - Random Forest
   - HistGradientBoosting

Results are saved under:
    task14_evaluation_results/
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

OUTPUT_DIR = PROJECT_ROOT / "task14_evaluation_results"

TEST_FILES = [
    PROJECT_ROOT / "tests" / "test_topic_quality_evaluation.py",
    PROJECT_ROOT / "tests" / "test_churn_explainability_evaluation.py",
    PROJECT_ROOT / "tests" / "test_rag_quality_evaluation.py",
    PROJECT_ROOT / "tests" / "test_news_sentiment_quality_evaluation.py",
    PROJECT_ROOT / "tests" / "test_portfolio_health_quality_evaluation.py",
]

BENCHMARK_FILE = (
    PROJECT_ROOT
    / "scripts"
    / "benchmark_fraud_models.py"
)


def run_command(args: list[str]) -> tuple[int, str]:
    """
    Run a command from the Vayvora project root.
    """

    result = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    return result.returncode, result.stdout


def parse_fraud_metrics(
    text: str,
) -> dict[str, dict[str, float]]:

    model_names = [
        "Logistic Regression",
        "Random Forest",
        "HistGradientBoosting",
    ]

    metrics: dict[str, dict[str, float]] = {}

    current_model = None

    for line in text.splitlines():

        line = line.strip()

        if line in model_names:
            current_model = line
            metrics[current_model] = {}
            continue

        if current_model is None:
            continue

        if ":" not in line:
            continue

        key, value = line.split(
            ":",
            1,
        )

        key = (
            key.strip()
            .lower()
            .replace("-", "_")
        )

        value = value.strip()

        if key in {
            "accuracy",
            "precision",
            "recall",
            "f1",
            "roc_auc",
        }:
            try:
                metrics[current_model][key] = float(
                    value
                )
            except ValueError:
                pass

    return metrics


def main() -> int:

    print("=" * 70)
    print(
        "TASK 14 - MODEL AND AI COMPONENT EVALUATION"
    )
    print("=" * 70)

    OUTPUT_DIR.mkdir(
        exist_ok=True
    )

    # ---------------------------------------------------------
    # Validate required files
    # ---------------------------------------------------------

    required_files = [
        *TEST_FILES,
        BENCHMARK_FILE,
    ]

    missing_files = [
        str(path)
        for path in required_files
        if not path.exists()
    ]

    if missing_files:

        print()
        print(
            "ERROR: Required files are missing:"
        )

        for file in missing_files:
            print(
                f"  {file}"
            )

        return 1

    # ---------------------------------------------------------
    # 1. Run Task 7 component tests
    # ---------------------------------------------------------

    print()
    print(
        "[1/2] Running Task 7 component evaluations..."
    )
    print()

    pytest_command = [
        sys.executable,
        "-m",
        "pytest",
        *[
            str(path)
            for path in TEST_FILES
        ],
        "-v",
    ]

    test_return_code, test_output = run_command(
        pytest_command
    )

    print(test_output)

    # ---------------------------------------------------------
    # 2. Run fraud model benchmark
    # ---------------------------------------------------------

    print()
    print(
        "[2/2] Running fraud model benchmark..."
    )
    print()

    benchmark_command = [
        sys.executable,
        str(BENCHMARK_FILE),
    ]

    benchmark_return_code, benchmark_output = (
        run_command(
            benchmark_command
        )
    )

    print(benchmark_output)

    # ---------------------------------------------------------
    # Parse fraud metrics
    # ---------------------------------------------------------

    fraud_metrics = parse_fraud_metrics(
        benchmark_output
    )

    # ---------------------------------------------------------
    # Build evidence object
    # ---------------------------------------------------------

    evidence = {
        "generated_at": datetime.now().isoformat(
            timespec="seconds"
        ),
        "python_executable": sys.executable,

        "task7_component_evaluation": {
            "return_code": test_return_code,
            "test_files": [
                str(
                    path.relative_to(
                        PROJECT_ROOT
                    )
                )
                for path in TEST_FILES
            ],
            "raw_output": test_output,
        },

        "fraud_model_benchmark": {
            "return_code": benchmark_return_code,
            "benchmark_file": str(
                BENCHMARK_FILE.relative_to(
                    PROJECT_ROOT
                )
            ),
            "metrics": fraud_metrics,
            "raw_output": benchmark_output,
            "dataset_note": (
                "Synthetic development data; "
                "results are not production validation."
            ),
        },
    }

    # ---------------------------------------------------------
    # Save JSON evidence
    # ---------------------------------------------------------

    json_path = (
        OUTPUT_DIR
        / "task14_evaluation_evidence.json"
    )

    json_path.write_text(
        json.dumps(
            evidence,
            indent=2,
        ),
        encoding="utf-8",
    )

    # ---------------------------------------------------------
    # Build Markdown summary
    # ---------------------------------------------------------

    passed = (
        "20 passed"
        in test_output
    )

    markdown = []

    markdown.append(
        "# Task 14 - Evaluation Summary"
    )

    markdown.append("")

    markdown.append(
        "## Task 7 AI Component Evaluation"
    )

    markdown.append("")

    if passed:
        markdown.append(
            "**Result: 20/20 tests passed.**"
        )
    else:
        markdown.append(
            "**Result: See raw pytest output.**"
        )

    markdown.append("")

    markdown.append(
        "## Fraud Model Benchmark"
    )

    markdown.append("")

    markdown.append(
        "| Model | Accuracy | Precision | "
        "Recall | F1 | ROC-AUC |"
    )

    markdown.append(
        "|---|---:|---:|---:|---:|---:|"
    )

    model_order = [
        "Logistic Regression",
        "Random Forest",
        "HistGradientBoosting",
    ]

    for model_name in model_order:

        values = fraud_metrics.get(
            model_name,
            {},
        )

        markdown.append(
            f"| {model_name} | "
            f"{values.get('accuracy', 'N/A')} | "
            f"{values.get('precision', 'N/A')} | "
            f"{values.get('recall', 'N/A')} | "
            f"{values.get('f1', 'N/A')} | "
            f"{values.get('roc_auc', 'N/A')} |"
        )

    markdown.append("")

    markdown.append(
        "> The fraud benchmark uses synthetic "
        "development data. These results are "
        "not production validation."
    )

    markdown.append("")

    markdown.append(
        "## Evidence"
    )

    markdown.append("")

    markdown.append(
        "The complete pytest and benchmark output "
        "is preserved in "
        "`task14_evaluation_evidence.json`."
    )

    markdown_path = (
        OUTPUT_DIR
        / "task14_evaluation_summary.md"
    )

    markdown_path.write_text(
        "\n".join(markdown),
        encoding="utf-8",
    )

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "TASK 14 EVALUATION COMPLETE"
    )
    print("=" * 70)

    print()
    print(
        f"Evidence JSON: {json_path}"
    )

    print(
        f"Summary Markdown: {markdown_path}"
    )

    if (
        test_return_code == 0
        and benchmark_return_code == 0
    ):
        print()
        print(
            "STATUS: SUCCESS"
        )
        return 0

    print()
    print(
        "STATUS: FAILED"
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )