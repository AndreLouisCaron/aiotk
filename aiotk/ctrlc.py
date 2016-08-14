# -*- coding: utf-8 -*-


import asyncio
import contextlib
import signal
import sys


@contextlib.contextmanager
def handle_ctrlc(f, loop=None):
    """Context manager that fulfills a future when CTRLC-C/SIGINT is received.

    This context manager provides the following features over direct use of
    ``asyncio.add_signal_handler()``:

    - automatically removes CTRL-C/SIGINT handler on context manager exit;
    - gracefully handles multiple CTRL-C/SIGINT events (the future will only be
      set once even if CTRL-C/SIGINT is received multiple times);
    - traps CTRL-C on Windows (using Win32 API via ctypes), including proper
      support for invocation of the console control handler in a separate
      thread).

    :param f: future to fulfill when CTRL-C/SIGINT is received.
    :param loop: event loop (defaults to global event loop).

    """

    loop = loop or asyncio.get_event_loop()

    # Must be idempotent in case CTRL-C/SIGINT is received multiple times.
    def handler():
        if not f.done():
            f.set_result(None)

    if sys.platform == 'win32':  # pragma: no posix
        from ctypes import WINFUNCTYPE, windll
        from ctypes.wintypes import BOOL, DWORD

        phandler_routine = WINFUNCTYPE(BOOL, DWORD)
        SetConsoleCtrlHandler = windll.kernel32.SetConsoleCtrlHandler
        CTRL_C_EVENT = 0

        # NOTE: for some reason, it seems like this never gets included
        #       in the code coverage report (probably because it's invoked
        #       as a ctypes callback).
        @phandler_routine
        def console_ctrl_handler(event):  # pragma: no cover
            if event == CTRL_C_EVENT:
                loop.call_soon_threadsafe(handler)
                return 1
            return 0

        if SetConsoleCtrlHandler(console_ctrl_handler, 1) == 0:
            raise WindowsError()
        try:
            yield
        finally:
            if SetConsoleCtrlHandler(console_ctrl_handler, 0) == 0:
                raise WindowsError()
    else:  # pragma: no win32
        loop.add_signal_handler(signal.SIGINT, handler)
        try:
            yield
        finally:
            loop.remove_signal_handler(signal.SIGINT)
