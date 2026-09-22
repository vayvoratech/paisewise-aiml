# ============================================================
# PaiseWise - AI Experiment Results
# Task 3: AI Experimentation & Feature Flags
# ============================================================

from collections import defaultdict

from .experiment_logger import get_experiment_logs

# ============================================================
# CALCULATE RESULTS FOR ONE EXPERIMENT
# ============================================================

def get_experiment_results(experiment_id: str):

    logs = get_experiment_logs()

    # Keep only logs belonging to this experiment
    experiment_logs = [
        log
        for log in logs
        if log.get("experiment_id") == experiment_id
    ]

    if not experiment_logs:
        return {
            "experiment_id": experiment_id,
            "total_users": 0,
            "variants": {}
        }

    # Group records by variant
    variant_logs = defaultdict(list)

    for log in experiment_logs:
        variant_id = log.get("variant_id")

        if variant_id:
            variant_logs[variant_id].append(log)

    results = {}

    # ========================================================
    # CALCULATE METRICS FOR EACH VARIANT
    # ========================================================

    for variant_id, logs_for_variant in variant_logs.items():

        user_ids = {
            log.get("user_id")
            for log in logs_for_variant
            if log.get("user_id")
        }

        # ----------------------------------------------------
        # Quality scores
        # ----------------------------------------------------

        quality_scores = [
            log.get("quality_score")
            for log in logs_for_variant
            if isinstance(log.get("quality_score"), (int, float))
        ]

        if quality_scores:
            average_quality = (
                sum(quality_scores) / len(quality_scores)
            )
        else:
            average_quality = None

        # ----------------------------------------------------
        # Success rate
        # ----------------------------------------------------

        successful_responses = sum(
            1
            for log in logs_for_variant
            if log.get("success") is True
        )

        total_responses = len(logs_for_variant)

        if total_responses > 0:
            success_rate = (
                successful_responses / total_responses
            ) * 100
        else:
            success_rate = 0

        # ----------------------------------------------------
        # Response time
        # ----------------------------------------------------

        response_times = [
            log.get("response_time_ms")
            for log in logs_for_variant
            if isinstance(log.get("response_time_ms"), (int, float))
        ]

        if response_times:
            average_response_time = (
                sum(response_times) / len(response_times)
            )
        else:
            average_response_time = None

        # ----------------------------------------------------
        # Store variant metrics
        # ----------------------------------------------------

        results[variant_id] = {
            "users": len(user_ids),
            "responses": total_responses,
            "average_quality": (
                round(average_quality, 2)
                if average_quality is not None
                else None
            ),
            "success_rate": round(success_rate, 2),
            "average_response_time_ms": (
                round(average_response_time, 2)
                if average_response_time is not None
                else None
            )
        }

    # ========================================================
    # RETURN EXPERIMENT RESULTS
    # ========================================================

    return {
        "experiment_id": experiment_id,
        "total_users": len({
            log.get("user_id")
            for log in experiment_logs
            if log.get("user_id")
        }),
        "total_responses": len(experiment_logs),
        "variants": dict(results)
    }


# ============================================================
# GET ALL EXPERIMENT RESULTS
# ============================================================

def get_all_experiment_results():

    logs = get_experiment_logs()

    experiment_ids = {
        log.get("experiment_id")
        for log in logs
        if log.get("experiment_id")
    }

    results = []

    for experiment_id in sorted(experiment_ids):

        results.append(
            get_experiment_results(experiment_id)
        )

    return results


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PaiseWise AI Experiment Results Test")
    print("=" * 60)

    experiment_id = "jargon_prompt_test_01"

    result = get_experiment_results(experiment_id)

    print("\nExperiment:")
    print(result["experiment_id"])

    print("\nTotal users:")
    print(result["total_users"])

    print("\nTotal responses:")
    print(result["total_responses"])

    print("\nVariant Metrics:")
    print("-" * 60)

    for variant_id, metrics in result["variants"].items():

        print(f"\nVariant {variant_id}")

        print(
            f"  Users: "
            f"{metrics['users']}"
        )

        print(
            f"  Responses: "
            f"{metrics['responses']}"
        )

        print(
            f"  Average Quality: "
            f"{metrics['average_quality']}"
        )

        print(
            f"  Success Rate: "
            f"{metrics['success_rate']}%"
        )

        print(
            f"  Average Response Time: "
            f"{metrics['average_response_time_ms']} ms"
        )

    print("\n" + "=" * 60)
    print("Experiment results test completed.")
    print("=" * 60)