import asyncio
import logging
import random
from datetime import datetime
from datetime import timedelta, tzinfo

log = logging.getLogger("atomizer.utils.time")

# https://stackoverflow.com/questions/19654578/python-utc-datetime-objects-iso-format-doesnt-include-z-zulu-or-zero-offset
# I have no clue what I'm doing here
class simple_utc(tzinfo):
    def tzname(self, **kwargs):
        return "UTC"

    def utcoffset(self, dt):
        return timedelta(0)


def get_utc_time():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

# https://codereview.stackexchange.com/questions/199743/countdown-timer-in-python
class CountdownTimer:
    def __init__(self, interval: str, jitter_interval: str = "0:00:00"):
        self.interval = datetime.strptime(interval, "%H:%M:%S")
        self.jitter_interval = datetime.strptime(jitter_interval, "%H:%M:%S")
        self.remaining = timedelta(seconds=0)

    async def wait(self, now: datetime = datetime.now):
        delta = timedelta(
            hours=int(self.interval.hour),
            minutes=int(self.interval.minute),
            seconds=int(self.interval.second)
        )

        jitter_delta = timedelta(
            hours=int(self.jitter_interval.hour),
            minutes=int(self.jitter_interval.minute),
            seconds=int(self.jitter_interval.second)
        )

        jitter = random.randint(0, int(jitter_delta.total_seconds()))
        time_to_wait = int(delta.total_seconds() + jitter)

        log.debug(f"Waiting for {self.interval.time()} (+ jitter: {timedelta(seconds=jitter)})")

        target = now()
        for remaining in range(time_to_wait, 1, -1):
            target += timedelta(seconds=1)
            self.remaining = timedelta(seconds=remaining)
            sleep_duration = (target - now()).total_seconds()
            await asyncio.sleep(sleep_duration)

        self.remaining = timedelta(seconds=0)

    def __str__(self):
        return str(self.remaining)
