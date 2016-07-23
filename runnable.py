import threading, time

class PnuRunnable ():
    def __init__ (self, update_interval=None):
        if update_interval is None:
            raise ValueError('missing interval')

        self._update_interval = update_interval
        self._next_tick = 0

    def _repeat (self, func, interval):
        self._next_tick += interval
        now = time.time()

        threading.Timer(
            self._next_tick - now,
            self._repeat,
            [ func, interval ]
        ).start()

    def run (self):
        self._next_tick = time.time()
        self._repeat(self.update, self._update_interval)
