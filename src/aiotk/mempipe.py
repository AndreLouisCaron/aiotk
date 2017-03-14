# -*- coding: utf-8 -*-


import asyncio


_DEFAULT_LIMIT = 2 ** 16


class _MemoryTransport(asyncio.Transport):
    """Direct connection between a StreamWriter and StreamReader."""

    def __init__(self, reader):
        super().__init__()
        self._reader = reader

    def write(self, data):
        self._reader.feed_data(data)

    def writelines(self, data):
        for line in data:
            self._reader.feed_data(line)
            self._reader.feed_data(b'\n')

    def write_eof(self):
        self._reader.feed_eof()

    def can_write_eof(self):
        return True

    def is_closing(self):
        return False

    def close(self):
        self.write_eof()


def mempipe(loop=None, limit=None):
    """In-memory pipe, returns a ``(reader, writer)`` pair.

    .. versionadded:: 0.1
    """

    loop = loop or asyncio.get_event_loop()
    limit = limit or _DEFAULT_LIMIT

    reader = asyncio.StreamReader(loop=loop, limit=limit)
    writer = asyncio.StreamWriter(
        transport=_MemoryTransport(reader),
        protocol=asyncio.StreamReaderProtocol(reader, loop=loop),
        reader=reader,
        loop=loop,
    )
    return reader, writer
