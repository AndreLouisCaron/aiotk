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
    :return: ``False`` if the task could not be canceled, else ``True``.

    """

    task.cancel()
    try:
        await asyncio.wait({task})
    except asyncio.CancelledError:
        await asyncio.wait({task})
        raise


__all__ = [
    'AsyncExitStack',
    'cancel',
    'handle_ctrlc',
    'mempipe',
    'mock_subprocess',
    'monkey_patch',
    'TCPServer',
    'UnixSocketServer',
]
