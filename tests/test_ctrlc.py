# -*- coding: utf-8 -*-


import asyncio
import os
import pytest
import signal
import sys

from aiotk import handle_ctrlc
from unittest import mock


if sys.platform == 'win32':
    from ctypes import windll

    GenerateConsoleCtrlEvent = windll.kernel32.GenerateConsoleCtrlEvent
    CTRL_C_EVENT = 0

    def send_ctrlc():
        if GenerateConsoleCtrlEvent(CTRL_C_EVENT, 0) == 0:
            raise WindowsError()
else:
    def send_ctrlc():
        os.kill(os.getpid(), signal.SIGINT)


@pytest.mark.asyncio
async def test_ctrlc(event_loop):
    done = asyncio.Future()
    with handle_ctrlc(done, loop=event_loop):
        send_ctrlc()
        await asyncio.wait_for(done, timeout=1.0)
    assert done.result() is None


@pytest.mark.asyncio
async def test_ctrlc_idempotent(event_loop):
    done = asyncio.Future()
    with handle_ctrlc(done, loop=event_loop):
        send_ctrlc()
        await asyncio.wait_for(done, timeout=1.0)
        send_ctrlc()
        send_ctrlc()
        # NOTE: sleep to yield control to event loop, so it can invoke our
        #       signal handler.
        await asyncio.sleep(0.001)
    assert done.result() is None


@pytest.mark.win32
@pytest.mark.asyncio
async def test_ctrlc_install_handler_failure(event_loop):

    def mock_SetConsoleCtrlHandler(_, add):
        if add is 1:
            return 0
        return 1

    with mock.patch('ctypes.windll.kernel32.SetConsoleCtrlHandler') as install:
        install.side_effect = mock_SetConsoleCtrlHandler
        done = asyncio.Future()
        with pytest.raises(WindowsError) as exc:
            with handle_ctrlc(done, loop=event_loop):
                pytest.fail('Handler install should not succeed.')
        assert install.call_count == 1
    assert not done.done()


@pytest.mark.win32
@pytest.mark.asyncio
async def test_ctrlc_remove_handler_failure(event_loop):

    def mock_SetConsoleCtrlHandler(_, add):
        if add is 0:
            return 0
        return 1

    with mock.patch('ctypes.windll.kernel32.SetConsoleCtrlHandler') as install:
        install.side_effect = mock_SetConsoleCtrlHandler
        done = asyncio.Future()
        with pytest.raises(WindowsError) as exc:
            with handle_ctrlc(done, loop=event_loop):
                pass
            pytest.fail('Handler removal should not succeed.')
        assert install.call_count == 2
    assert not done.done()
