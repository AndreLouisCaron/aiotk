# -*- coding: utf-8 -*-


import sys


class AsyncExitStack(object):
    """Rollback stack for asynchronous context managers.

    This context manager provides the following features over direct use of
    ``contextlib.ExitStack``:

    - supports asynchronous context managers (in addition to regular context
      managers).

    .. versionadded: 0.2

    """

    def __init__(self):
        self._stack = []

    async def __aenter__(self):
        """No-op."""
        assert self._stack == []
        return self

    async def __aexit__(self, etype, exc, tb):
        """Pop all context managers from the rollback stack.

        :param context: context manager or asynchronous context manager.
        :returns: True if one of the context managers in the stack suppressed
         the exception by returning a ``True`` value from its ``__exit__`` or
         ``__aexit__`` method.
        :exception: If any context manager in the stack raises an exception
         from its ``__exit__`` or ``__aexit__`` method, this exception will
         replace the original exception for context managers lower in the stack
         and will eventually be propagated to the caller.

        """
        changed = False
        for context in reversed(self._stack):
            suppress = False
            try:
                if hasattr(context, '__aexit__'):
                    suppress = await context.__aexit__(etype, exc, tb)
                if hasattr(context, '__exit__'):
                    suppress = context.__exit__(etype, exc, tb)
                if suppress:
                    etype, exc, tb = (None, None, None)
                    changed = True
            except:
                etype, exc, tb = sys.exc_info()
                changed = True
        if changed:
            if (etype, exc, tb) == (None, None, None):
                return True
            raise exc

    async def enter_context(self, context):
        """Push an (asynchronous) context manager onto the rollback stack.

        :param context: context manager or asynchronous context manager.
        :return: The return value of the context manager's ``__enter__`` or
         ``__aenter__`` method.

        """
        if hasattr(context, '__aenter__'):
            r = await context.__aenter__()
        else:
            r = context.__enter__()
        self._stack.append(context)
        return r
