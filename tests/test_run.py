# -*- coding: utf-8 -*-


import asyncio
import pytest

from aiotk import run_until_complete
from unittest import mock


def test_run_until_complete_success(event_loop):
    """The return value is forwarded."""

    async def main():
        return 123

    result = run_until_complete(main(), loop=event_loop)
    assert result == 123


def test_run_until_complete_failure(event_loop):
    """Exceptions are propagated."""

    error = Exception('FUUU')

    async def main():
        raise error

    with pytest.raises(Exception) as exc:
        print(run_until_complete(main(), loop=event_loop))
    assert exc.value is error


def test_run_until_complete_interrupted(event_loop):
    """Task is cancelled on ``KeyboardInterrupt`` exception."""

    async def main():
        raise Exception('Should not have been called!')

    task = mock.MagicMock()
    del task.result

    with mock.patch.object(event_loop, 'create_task') as spawn:
        spawn.side_effect = [task]
        with mock.patch.object(event_loop, 'run_until_complete') as run:
            run.side_effect = [
                KeyboardInterrupt(),
                asyncio.CancelledError(),
            ]
            result = run_until_complete(main(), loop=event_loop)
            assert result is None

    # Should have been called twice.
    assert run.call_count == 2


def test_run_until_complete_interrupted_override(event_loop):
    """Task finishes despite ``KeyboardInterrupt`` exception."""

    async def main():
        raise Exception('Should not have been called!')

    task = mock.MagicMock()
    task.result.side_effect = [123]

    with mock.patch.object(event_loop, 'create_task') as spawn:
        spawn.side_effect = [task]
        with mock.patch.object(event_loop, 'run_until_complete') as run:
            run.side_effect = [
                KeyboardInterrupt(),
                None,
            ]
            result = run_until_complete(main(), loop=event_loop)
            assert result is 123

    # Should have been called twice.
    assert run.call_count == 2
