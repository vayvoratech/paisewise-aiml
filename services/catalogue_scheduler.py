from apscheduler.schedulers.background import BackgroundScheduler

from services.fund_catalogue import refresh_catalogue


scheduler = BackgroundScheduler()


def start_catalogue_scheduler():

    scheduler.add_job(
        refresh_catalogue,
        trigger="interval",
        hours=4,
        id="fund_catalogue_refresh",
        replace_existing=True
    )

    scheduler.start()

    print("Fund catalogue scheduler started")