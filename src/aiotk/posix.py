# -*- coding: utf-8 -*-


import asyncio
import os


class UnixSocketServer(object):
    """Asynchronous context manager to accept UNIX connections.

    This context manager provides the following features over direct use of
    ``asyncio.start_unix_server()``:

    - connection handlers are coroutines
    - prevent leaking connections when the writer is not properly closed by the
      connection handler
    - automatically cancel all tasks that handle connections when it's time to
      shut down
    - wait until all connections are closed before shutting down the server
      application (includes handling of a rare race condition)
    - automatically unlink the UNIX socket when shutting down (assuming the
      process does not crash)

    :param path: Path to the UNIX socket on which to listen for incoming
     connections.
    :param callback: Coroutine function that will be used to spawn a task for
     each established connection.  This coroutine must accept two positional
     arguments: ``(reader, writer)`` which allow interaction with the peer.
    :param loop: Event loop in which to run the server's asynchronous tasks.
     When ``None``, the current default event loop will be used.

    .. versionadded: 0.1

    """

    def __init__(self, path, callback, loop=None):
        self._callback = callback
        self._path = path
        self._loop = loop or asyncio.get_event_loop()
        self._sessions = set()
        self._server = None

    @property
    def path(self):
        """UNIX socket on which the server listens for incoming connections."""
        return self._path

    async def __aenter__(self):
        self.start()
        await self.wait_started()
        return self

    async def __aexit__(self, *args):
        self.close()
        await self.wait_closed()

    def start(self):
        """Start accepting connections.

        Only use this method if you are not using the server as an asynchronous
        context manager.

        See:

        - :py:meth:`aiotk.TCPServer.wait_started`
        - :py:meth:`aiotk.TCPServer.close`
        """
        if self._server:
            raise Exception('Already running.')
        self._server = self._loop.create_task(asyncio.start_unix_server(
            self._client_connected, path=self._path,
        ))

    # NOTE: start is synchronous, so we can't await in there.
    async def wait_started(self):
        """Wait until the server is ready to accept connections.

        See:

        - :py:meth:`aiotk.TCPServer.start`
        - :py:meth:`aiotk.TCPServer.close`
        """
        if not self._server:
            raise Exception('Not started.')
        if isinstance(self._server, asyncio.Future):
            self._server = await self._server

    # NOTE: cancel pending sessions immediately.
    def close(self):
        """Stop accepting connections.

        .. note::

           Since connections may still be pending in the kernel's TCP stack at
           the time where you call this, it's possible that new connections
           seem to get established after you signal your intent to stop
           accepting connections.

        See:

        - :py:meth:`aiotk.TCPServer.wait_started`
        - :py:meth:`aiotk.TCPServer.wait_closed`

        """
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
        """Wait until all connections are closed.

        See:

        - :py:meth:`aiotk.TCPServer.wait_started`
        - :py:meth:`aiotk.TCPServer.wait_closed`
        """
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
        if os.path.exists(self._path):
            os.unlink(self._path)

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
