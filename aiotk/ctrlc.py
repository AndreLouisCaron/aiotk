# -*- coding: utf-8 -*-


import asyncio
import contextlib
import signal


@contextlib.contextmanager
def handle_ctrlc(f, loop=None):
    """Context manager that schedules a callback when SIGINT is received.

    :param f: future to fulfill when SIGINT is received.  Will only be set
     once even if SIGINT is received multiple times.
    :param loop: event loop (defaults to global event loop).

    """

    loop = loop or asyncio.get_event_loop()

    def handler():
        if not f.done():
            f.set_result(None)

    loop.add_signal_handler(signal.SIGINT, handler)
    try:
        yield
    finally:
        loop.remove_signal_handler(signal.SIGINT)
