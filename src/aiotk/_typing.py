# -*- coding: utf-8 -*-


from typing import Any, List
from typing_extensions import Protocol


class Server(Protocol):
    """Asyncio event loop does not publish an interface for server objects."""

    def close(self) -> None:
        ...

    async def wait_closed(self) -> None:
        ...


class SocketServer(Server):
    """Asyncio event loop does not publish an interface for server objects."""

    @property
    def sockets(self) -> List[Any]:
        ...
