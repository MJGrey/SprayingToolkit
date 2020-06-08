import asyncio
import logging
from datetime import datetime
from datetime import timedelta, tzinfo

log = logging.getLogger("atomizer.utils")

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
async def countdown_timer(interval: str, now: datetime = datetime.now):
    dt = datetime.strptime(interval, "%H:%M:%S")
    delay = timedelta(
        hours=int(dt.hour), minutes=int(dt.minute), seconds=int(dt.second)
    )
    target = now()
    one_second_later = timedelta(seconds=1)

    for remaining in range(int(delay.total_seconds()), 0, -1):
        target += one_second_later
        print(
            f"{timedelta(seconds=remaining - 1)} remaining until next spray", end="\r"
        )
        duration = (target - now()).total_seconds()
        if duration > 0:
            await asyncio.sleep(duration)
