# -*- coding: utf-8 -*-


import asyncio


_DEFAULT_LIMIT = 2 ** 16


class _MemoryTransport(asyncio.Transport):
    """Direct connection between a StreamWriter and StreamReader."""

    def __init__(self, reader, limit):
        super().__init__()
        self._reader = reader
        self._limit = limit

    def write(self, data):
        self._reader.feed_data(data)

    def write_eof(self):
        self._reader.feed_eof()


def mempipe(loop=None, limit=_DEFAULT_LIMIT):
    """In-memory pipe, returns a ``(reader, writer)`` pair.

    .. versionadded:: 0.1
    """

    loop = loop or asyncio.get_event_loop()

    reader = asyncio.StreamReader(loop=loop, limit=limit)
    writer = asyncio.StreamWriter(
        transport=_MemoryTransport(reader, limit=limit),
        protocol=asyncio.StreamReaderProtocol(reader, loop=loop),
        reader=reader,
        loop=loop,
    )
    return reader, writer
