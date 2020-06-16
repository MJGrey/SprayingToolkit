import logging
import asyncio
import random
from sprayingtoolkit.models import HostingLocation, SprayStats, SprayState
from sprayingtoolkit.utils.time import CountdownTimer
from sprayingtoolkit.utils.credentials import automatic_cred_generator

log = logging.getLogger("atomizer.base")


class BaseSprayer:
    def __init__(self):
        self._interval: str = "1:00:00"
        self._interval_jitter: int = "0:00:00"
        self._auth_coros = {
            HostingLocation.internal: self.auth,
            HostingLocation.O365: self.auth_o365
        }

        self.results = []
        self.auth_jitter: int = 0
        self.hosting_location: HostingLocation = HostingLocation.O365
        self.stats: SprayState = SprayStats()
        self.state: SprayState = SprayState.CONFIGURED
        self.countdown_timer = CountdownTimer(self._interval, self._interval_jitter)

    @property
    def interval(self):
        return str(self._interval)

    @interval.setter
    def interval(self, value):
        self._interval = value
        self.countdown_timer = CountdownTimer(self._interval, self._interval_jitter)

    @property
    def interval_jitter(self):
        return str(self._interval_jitter)

    @interval_jitter.setter
    def interval_jitter(self, value):
        self._interval_jitter = value
        self.countdown_timer = CountdownTimer(self._interval, self._interval_jitter)

    async def _task_watch(self):
        while True:
            try:
                if str(self.countdown_timer) == "0:00:00":
                    log.info(
                        f"{self.__class__.__name__} - total: {self.stats.inputs}, done: {self.stats.execs}, pending: {self.stats.pending}"
                    )
                    await asyncio.sleep(5)
                else:
                    print(f"time until next spray: {self.countdown_timer}", end='\r')
                    await asyncio.sleep(0.01)
            except asyncio.CancelledError:
                log.debug("Task watcher has been cancelled")
                break

    async def _username_producer(self, queue, usernames):
        while True:
            try:
                self.stats.inputs = 0
                async for user in automatic_cred_generator(usernames):
                    self.stats.inputs += 1
                    queue.put_nowait(user)
                await queue.join()
            except asyncio.CancelledError:
                log.debug("Username producer task has been cancelled")
                break

    async def _password_producer(self, queue, passwords):
        async for passw in automatic_cred_generator(passwords):
            queue.put_nowait(passw)

    async def _queue_iterator(self, queue):
        while True:
            try:
                item = queue.get_nowait()
                yield item
            except (asyncio.QueueEmpty, asyncio.CancelledError):
                break
            else:
                queue.task_done()

    async def _worker(self, username_queue, password_queue):
        self.state = SprayState.STARTED
        while True:
            try:
                self.stats = SprayStats()
                password = await password_queue.get()
                tasks = [
                    self._spray(user, password)
                    async for user in self._queue_iterator(username_queue)
                ]

                self.results.extend(
                    await asyncio.gather(*tasks)
                )

                password_queue.task_done()
                await self.countdown_timer.wait()
            except asyncio.CancelledError:
                log.debug("Worker task has been cancelled")
                break

    async def _spray(self, username, password):
        await asyncio.sleep(
            random.randint(0, self.auth_jitter)
        )

        result = await self._auth_coros[self.hosting_location](username, password)
        self.stats.execs += 1

        log.info(f"{username} - valid: {result['valid']} reason: {result['reason']}")

        return {
            'username': username,
            'password': password,
            **result
        }

    async def start(self, usernames, passwords):
        username_queue = asyncio.Queue()
        password_queue = asyncio.Queue()

        user_producer_task = asyncio.create_task(
            self._username_producer(username_queue, usernames)
        )

        asyncio.create_task(self._password_producer(password_queue, passwords))

        while username_queue.qsize() == 0:
            await asyncio.sleep(0.1)

        worker_task = asyncio.create_task(self._worker(username_queue, password_queue))
        watcher_task = asyncio.create_task(self._task_watch())

        try:
            await password_queue.join()
            self.state = SprayState.DONE
        except asyncio.CancelledError:
            self.state = SprayState.STOPPED
            log.debug("Cancelling spray")
        finally:
            worker_task.cancel()
            user_producer_task.cancel()
            watcher_task.cancel()
            await asyncio.gather(user_producer_task, worker_task, watcher_task)

        return self.results

    async def shutdown(self):
        raise NotImplementedError

    async def auth(self, username, password):
        raise NotImplementedError

    async def auth_o365(self, username, password):
        raise NotImplementedError


class BaseValidator:
    def __init__(self):
        self.interval = "1:00:00"

    async def start(self, usernames):
        try:
            tasks = [
                self.validate(user)
                async for user in automatic_cred_generator(usernames)
            ]

            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            log.debug("Cancelling validator")

    async def shutdown(self):
        raise NotImplementedError
    
    async def validate(self, username):
        raise NotImplementedError
