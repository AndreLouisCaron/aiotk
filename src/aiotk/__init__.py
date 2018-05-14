# -*- coding: utf-8 -*-


import asyncio

from ._cancel import (
    cancel,
    cancel_all,
    follow_through,
    wait_until_cancelled,
)
from .mempipe import mempipe
from .monkey import monkey_patch
from ._io import reader
from .posix import UnixSocketServer
from .stack import AsyncExitStack, EnsureDone
from .tcp import TCPServer, tcp_server
from ._udp import udp_server
from .testing import mock_subprocess
from .ctrlc import handle_ctrlc
from ._pool import PoolClosed, TaskPool
from ._sched import PeriodicTask


def run_until_complete(coro, loop=None):
    """Run a task through to completion.

    The ``.run_until_complete()`` method on asyncio event loop objects does not
    finish tasks when it receives a SIGINT/CTRL-C.  The method simply raises a
    ``KeyboardInterrupt`` exception and this usually results in warnings about
    unfinished tasks plus some "event loop closed" ``RuntimeError`` exceptions
    in pending tasks.

    This is a really annoying default behavior and this function aims at
    replacing that behavior with something that ensures the task actually runs
    through to completion.  When the ``KeyboardInterrupt`` exception is caught,
    the task is canceled and resumed to give it a chance to clean up properly.

    .. versionadded: 0.4

    """

    loop = loop or asyncio.get_event_loop()
    task = loop.create_task(coro)
    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        task.cancel()
        try:
            loop.run_until_complete(task)
        except asyncio.CancelledError:
            return None
    return task.result()


__all__ = [
    'AsyncExitStack',
    'cancel',
    'cancel_all',
    'EnsureDone',
    'follow_through',
    'handle_ctrlc',
    'mempipe',
    'mock_subprocess',
    'monkey_patch',
    'PeriodicTask',
    'PoolClosed',
    'reader',
    'run_until_complete',
    'TaskPool',
    'TCPServer',
    'tcp_server',
    'udp_server',
    'UnixSocketServer',
    'wait_until_cancelled',
]
