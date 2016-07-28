# -*- coding: utf-8 -*-


import asyncio
import pytest

from aiotk import mempipe


@pytest.mark.asyncio
async def test_mempipe(event_loop):
    reader, writer = mempipe(loop=event_loop)
    writer.write(b'FUBAR')
    writer.write_eof()
    message = await asyncio.wait_for(reader.read(), timeout=5.0)
    assert message == b'FUBAR'


@pytest.mark.asyncio
async def test_mempipe_async_read(event_loop):
    reader, writer = mempipe(loop=event_loop)
    read = event_loop.create_task(reader.read())
    with pytest.raises(asyncio.TimeoutError):
        print(await asyncio.wait_for(asyncio.shield(read), timeout=0.05))
    writer.write(b'FUBAR')
    writer.write_eof()
    message = await asyncio.wait_for(read, timeout=5.0)
    assert message == b'FUBAR'


@pytest.mark.asyncio
async def test_mempipe_async_eof(event_loop):
    reader, writer = mempipe(loop=event_loop)
    writer.write(b'FUBAR')
    read = event_loop.create_task(reader.read())
    with pytest.raises(asyncio.TimeoutError):
        print(await asyncio.wait_for(asyncio.shield(read), timeout=0.05))
    writer.write_eof()
    message = await asyncio.wait_for(read, timeout=5.0)
    assert message == b'FUBAR'


@pytest.mark.asyncio
async def test_mempipe_close(event_loop):
    reader, writer = mempipe(loop=event_loop)
    writer.write(b'FUBAR')
    writer.close()
    message = await asyncio.wait_for(reader.read(), timeout=5.0)
    assert message == b'FUBAR'
