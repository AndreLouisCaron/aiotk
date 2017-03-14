# -*- coding: utf-8 -*-


import asyncio
import pytest

from aiotk import cancel
from unittest import mock


@pytest.mark.asyncio
async def test_cancel_success(event_loop):
    """Child task's CancelledError exception is not propagated."""

    async def child_task(future):
        await future

    # Spawn a task that will never complete (unless cancelled).
    future = asyncio.Future(loop=event_loop)
    task = event_loop.create_task(child_task(future))

    # Cancel the task.
    assert not task.done()
    await cancel(task)
    assert task.done()
    assert task.cancelled()

    # Ensure that it was cancelled.
    with pytest.raises(asyncio.CancelledError):
        print(await task)


@pytest.mark.asyncio
async def test_cancel_despite_cancel(event_loop):
    """CancelledError exception is not propagated until the task completes."""

    task = mock.MagicMock()
    task.cancel.side_effect = [True]

    with mock.patch('asyncio.wait') as wait:
        error = asyncio.CancelledError()
        success = asyncio.Future(loop=event_loop)
        success.set_result(None)
        wait.side_effect = [
            error,
            success,
        ]
        with pytest.raises(asyncio.CancelledError) as exc:
            await cancel(task)
        assert exc.value is error

    wait.assert_called_with({task})
    assert wait.call_count == 2


@pytest.mark.asyncio
async def test_cancel_already_done(event_loop):
    """No-op on task that has already completed."""

    async def child_task(future):
        pass

    # Spawn a task that will complete immediately.
    future = asyncio.Future(loop=event_loop)
    task = event_loop.create_task(child_task(future))

    await task
    assert task.done()

    await cancel(task)
