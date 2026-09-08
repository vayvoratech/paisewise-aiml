import schedule
import time

from churn_retraining_pipeline import run_churn_retraining


# ============================================================
# CONFIGURATION
# ============================================================

# ------------------------------------------------------------
# True  = run immediately for testing
#
# False = use monthly schedule
# ------------------------------------------------------------

TEST_MODE = True


# ============================================================
# RETRAINING JOB
# ============================================================

def monthly_retraining_job():

    print("\n" + "=" * 60)

    print(
        "STARTING SCHEDULED CHURN RETRAINING"
    )

    print("=" * 60)

    try:

        run_churn_retraining()

        print(
            "\nScheduled retraining finished successfully."
        )

    except Exception as e:

        print(
            "\nScheduled retraining failed."
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
        "PAISEWISE CHURN MODEL SCHEDULER"
    )

    print("=" * 60)

    print(
        "\nTEST MODE ENABLED."
    )

    print(
        "Running churn retraining immediately..."
    )

    print(
        "This does NOT wait for the 1st of the month."
    )

    # --------------------------------------------------------
    # Run immediately
    # --------------------------------------------------------

    monthly_retraining_job()

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
        "PAISEWISE CHURN MODEL SCHEDULER"
    )

    print("=" * 60)

    print(
        "\nPRODUCTION MODE ENABLED."
    )

    print(
        "Schedule: 1st day of every month at 3:00 AM"
    )

    # ========================================================
    # CHECK FIRST DAY
    # ========================================================

    def check_first_day():

        current_day = time.localtime().tm_mday

        if current_day == 1:

            monthly_retraining_job()

        else:

            print(
                "\nToday is not the first day."
            )

            print(
                "Retraining skipped."
            )

    # ========================================================
    # SCHEDULE
    # ========================================================

    schedule.every().day.at(

        "03:00"

    ).do(

        check_first_day

    )

    # ========================================================
    # SCHEDULER LOOP
    # ========================================================

    while True:

        schedule.run_pending()

        time.sleep(30)