import asyncio
import json
import string
import random
import inspect
import logging
import functools
import threading

log = logging.getLogger("atomizer.utils.common")
log.setLevel(logging.DEBUG)

def beautify_json(obj) -> str:
    return "\n" + json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))

def gen_random_string(length: int = 5, only_letters: bool = False) -> str:
    char_set = (string.ascii_lowercase + string.digits) if not only_letters else string.ascii_lowercase
    return ''.join(random.sample(char_set, int(length)))

def coro(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper


# Stolen from https://github.com/w1z2g3/syncasync/blob/master/syncasync.py
class SyncToAsync:
    """
    Utility class which turns a synchronous callable into an awaitable that
    runs in a threadpool. It also sets a threadlocal inside the thread so
    calls to AsyncToSync can escape it.
    """

    threadlocal = threading.local()

    def __init__(self, func):
        self.func = func

    async def __call__(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(
            None,
            functools.partial(self.thread_handler, loop, *args, **kwargs),
        )
        return await asyncio.wait_for(future, timeout=None)

    def __get__(self, parent, objtype):
        """
        Include self for methods
        """
        return functools.partial(self.__call__, parent)

    def thread_handler(self, loop, *args, **kwargs):
        """
        Wraps the sync application with exception handling.
        """
        # Set the threadlocal for AsyncToSync
        self.threadlocal.main_event_loop = loop
        # Run the function
        return self.func(*args, **kwargs)

make_async = SyncToAsync
