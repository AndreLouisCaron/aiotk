# -*- coding: utf-8 -*-


import asyncio

from .mempipe import mempipe
from .monkey import monkey_patch
from .posix import UnixSocketServer
from .stack import AsyncExitStack
from .tcp import TCPServer
from .testing import mock_subprocess
from .ctrlc import handle_ctrlc


async def cancel(task):
    """Cancel a task and wait until it's done.

    **Note**: this function is a coroutine.

    Canceling a child task and returning without waiting for the child task to
    complete is a common cause of "event loop closed" ``RuntimeError``
    exceptions, especially during program shutdown.  Therefore, this becomes a
    common pattern:

    .. source-code: python

        task.cancel()
        await asyncio.wait({task})

    However, if the parent task itself is also canceled, then the
    ``asyncio.wait()`` call will be interrupted and the child task will still
    not complete.  To solve this, we must also manage to trap the
    ``asyncio.CancelledError`` exception and call ``asyncio.wait({task})``
    again and properly re-raise the ``asyncio.CancelledError`` exception.

    This is not trivial and must be done so many times in a program that
    cancels tasks that it merits a replacement API for ``task.cancel()``.

    :param task: The ``asyncio.Task`` object to cancel.

    """

    task.cancel()
    try:
        await asyncio.wait({task})
    except asyncio.CancelledError:
        await asyncio.wait({task})
        raise


async def cancel_all(tasks):
    """Cancel a set of tasks and wait until they're done.

    **Note**: this function is a coroutine.

    Canceling a set of child tasks and returning without waiting for the child
    task to complete is a common cause of "event loop closed" ``RuntimeError``
    exceptions, especially during shutdown of servers with one ore more task
    per connection.  Therefore, this becomes a common pattern:

    .. source-code: python

        for task in tasks:
            task.cancel()
        await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

    However, if the parent task itself is also canceled, then the
    ``asyncio.wait()`` call will be interrupted and one or more of the child
    tasks will still not complete.  To solve this, we must also manage to trap
    the ``asyncio.CancelledError`` exception and call ``asyncio.wait(tasks)``
    again and properly re-raise the ``asyncio.CancelledError`` exception.

    This is not trivial and must be done so many server programs that cancels
    tasks that it merits a helper.

    :param tasks: The set of ``asyncio.Task`` objects to cancel.

    """

    for task in tasks:
        task.cancel()
    try:
        await asyncio.wait(tasks)
    except asyncio.CancelledError:
        await asyncio.wait(tasks)
        raise


__all__ = [
    'AsyncExitStack',
    'cancel',
    'cancel_all',
    'handle_ctrlc',
    'mempipe',
    'mock_subprocess',
    'monkey_patch',
    'TCPServer',
    'UnixSocketServer',
]
