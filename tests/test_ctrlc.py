# -*- coding: utf-8 -*-


import asyncio
import os
import pytest
import signal

from aiotk import handle_ctrlc


@pytest.mark.skipif('sys.platform == "win32"')
@pytest.mark.asyncio
async def test_ctrlc(event_loop):
    done = asyncio.Future()
    with handle_ctrlc(done, loop=event_loop):
        os.kill(os.getpid(), signal.SIGINT)
        await asyncio.wait_for(done, timeout=1.0)
    assert done.result() is None


@pytest.mark.skipif('sys.platform == "win32"')
@pytest.mark.asyncio
async def test_ctrlc_idempotent(event_loop):
    done = asyncio.Future()
    with handle_ctrlc(done, loop=event_loop):
        os.kill(os.getpid(), signal.SIGINT)
        await asyncio.wait_for(done, timeout=1.0)
        os.kill(os.getpid(), signal.SIGINT)
        os.kill(os.getpid(), signal.SIGINT)
        # NOTE: sleep to yield control to event loop, so it can invoke our
        #       signal handler.
        await asyncio.sleep(0.001)
    assert done.result() is None
