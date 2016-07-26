import threading, time
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class PnuRunnable ():
    def __init__ (self, update_interval=None):
        if update_interval is None:
            raise ValueError("missing interval")

        self._update_interval = update_interval

    def update (self): # no-op
        print('num threads: ', threading.active_count())

    def run (self):
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            self.update,
            'interval',
            seconds=self._update_interval
        )
        scheduler.start()

