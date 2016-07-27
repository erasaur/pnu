import threading, time
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class PnuRunnable ():
    def __init__ (self, update_interval=None):
        self._update_interval = update_interval

    def update (self):
        print('num threads: ', threading.active_count())

    # by default, just run update method in loop
    def run (self):
        self.run_interval(self.update)

    # run a function once in a separate thread
    def run_once (self, func, *args):
        threading.Thread(target=func, args=args).start()

    # run a function in an interval in a separate thread
    def run_interval (self, func=None, update_interval=None):
        if update_interval is None and self._update_interval is None:
            raise ValueError("missing interval")

        if func is None:
            raise ValueError("missing func")

        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            func,
            'interval',
            seconds=self._update_interval
        )
        scheduler.start()

