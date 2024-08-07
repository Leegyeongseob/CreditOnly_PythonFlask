import sys
import os
from apscheduler.schedulers.background import BackgroundScheduler
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from BankOfKoreaHandler import index_data as index_bok_data

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=index_bok_data, trigger="cron", minute='*/1', id="index_data_job")
    scheduler.start()
