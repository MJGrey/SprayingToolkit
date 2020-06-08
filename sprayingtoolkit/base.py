import logging
import asyncio
from sprayingtoolkit.models import HostingLocation
from sprayingtoolkit.utils.time import countdown_timer
from sprayingtoolkit.utils.credentials import automatic_cred_generator

log = logging.getLogger("atomizer.base.basesprayer")


class BaseSprayer:
    def __init__(self):
        self.hosting_location = HostingLocation.O365
        self.interval = "1:00:00"

    async def _username_producer(self, queue, usernames):
        while True:
            try:
                async for user in automatic_cred_generator(usernames):
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
            except asyncio.QueueEmpty:
                break
            else:
                queue.task_done()

    async def _worker(self, username_queue, password_queue):
        while True:
            try:
                password = await password_queue.get()
                tasks = [
                    self.auth(user, password)
                    if self.hosting_location == HostingLocation.internal
                    else self.auth_o365(user, password)
                    async for user in self._queue_iterator(username_queue)
                ]

                await asyncio.gather(*tasks)

                password_queue.task_done()
                await countdown_timer(self.interval)
            except asyncio.CancelledError:
                log.debug("Worker task has been cancelled")
                break

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

        try:
            await password_queue.join()
        except asyncio.CancelledError:
            log.debug("Cancelling spray")
        finally:
            worker_task.cancel()
            user_producer_task.cancel()
            await asyncio.gather(user_producer_task, worker_task)

    async def shutdown(self):
        raise NotImplementedError

    async def auth(self, username, password):
        raise NotImplementedError

    async def auth_o365(self, username, password):
        raise NotImplementedError
