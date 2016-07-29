# -*- coding: utf-8 -*-


import asyncio


class TCPServer(object):
    """Asynchronous context manager to accept TCP connections.

    .. versionadded: 0.2
    """

    def __init__(self, host, port, callback, loop=None):
        self._callback = callback
        self._host = host
        self._port = port
        self._loop = loop or asyncio.get_event_loop()
        self._sessions = set()
        self._server = None

    @property
    def host(self):
        """."""
        return self._host

    @property
    def port(self):
        """."""
        return self._port

    async def __aenter__(self):
        self.start()
        await self.wait_started()
        return self

    async def __aexit__(self, *args):
        self.close()
        await self.wait_closed()

    def start(self):
        if self._server:
            raise Exception('Already running.')
        self._server = self._loop.create_task(asyncio.start_server(
            self._client_connected, host=self._host, port=self._port,
        ))

    # NOTE: start is synchronous, so we can't await in there.
    async def wait_started(self):
        if not self._server:
            raise Exception('Not started.')
        if isinstance(self._server, asyncio.Future):
            self._server = await self._server

    # NOTE: cancel pending sessions immediately.
    def close(self):
        if not self._server:
            return
        if isinstance(self._server, asyncio.Future):
            raise Exception('Starting.')
        self._server.close()
        for session in self._sessions:
            session.cancel()

    # NOTES:
    # - caller can retry if they hit the timeout;
    # - not clear if we can still accept connections until
    #   ```self._server.wait_closed()` completes, so we cancel again after it
    #   does.
    async def wait_closed(self, timeout=None):
        if not self._server:
            return
        await self._server.wait_closed()
        for session in self._sessions:
            session.cancel()
        pending = self._sessions
        if pending:
            _, pending = await asyncio.wait(
                pending,
                return_when=asyncio.ALL_COMPLETED,
                timeout=timeout,
            )
        if pending:
            raise asyncio.TimeoutError()
        assert not self._sessions

    # NOTE: not closing writer here leaks connection.
    async def _client_wrapper(self, reader, writer):
        try:
            return await self._callback(
                reader=reader, writer=writer,
            )
        except asyncio.CancelledError:
            pass
        finally:
            writer.close()

    # NOTE: exception here leaks connection.
    def _client_connected(self, reader, writer):
        s = self._loop.create_task(
            self._client_wrapper(reader, writer)
        )
        s.add_done_callback(self._sessions.remove)
        self._sessions.add(s)
