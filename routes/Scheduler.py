from apscheduler.schedulers.background import BackgroundScheduler
from .BankOfKoreaHandler import IndexBokData

def StartScheduler():
    Scheduler = BackgroundScheduler()
    Scheduler.add_job(func=IndexBokData, trigger="cron", minute='*/1', id="IndexBokDataJob")
    Scheduler.start()
