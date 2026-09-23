import schedule
import time

from fund_retraining_pipeline import run_fund_retraining


# ============================================================
# CONFIGURATION
# ============================================================

# True  = run immediately for testing
# False = use Sunday 2:00 AM schedule

TEST_MODE = True


# ============================================================
# WEEKLY RETRAINING JOB
# ============================================================

def weekly_retraining_job():

    print("\n" + "=" * 60)

    print(
        "STARTING SCHEDULED FUND RETRAINING"
    )

    print("=" * 60)

    try:

        run_fund_retraining()

        print(
            "\nScheduled fund retraining "
            "finished successfully."
        )

    except Exception as e:

        print(
            "\nScheduled fund retraining failed."
        )

        print(
            "Error:",
            e
        )


# ============================================================
# TEST MODE
# ============================================================

if TEST_MODE:

    print("=" * 60)

    print(
        "PAISEWISE FUND MODEL SCHEDULER"
    )

    print("=" * 60)

    print(
        "\nTEST MODE ENABLED."
    )

    print(
        "Running fund retraining immediately..."
    )

    print(
        "This does NOT wait for Sunday 2:00 AM."
    )

    weekly_retraining_job()

    print(
        "\nTest completed successfully."
    )

    print(
        "Change TEST_MODE = False "
        "for production scheduling."
    )


# ============================================================
# PRODUCTION MODE
# ============================================================

else:

    print("=" * 60)

    print(
        "PAISEWISE FUND MODEL SCHEDULER"
    )

    print("=" * 60)

    print(
        "\nPRODUCTION MODE ENABLED."
    )

    print(
        "Schedule: Every Sunday at 2:00 AM"
    )

    # --------------------------------------------------------
    # Schedule weekly retraining
    # --------------------------------------------------------

    schedule.every().sunday.at(
        "02:00"
    ).do(
        weekly_retraining_job
    )

    # --------------------------------------------------------
    # Keep scheduler running
    # --------------------------------------------------------

    while True:

        schedule.run_pending()

        time.sleep(30)