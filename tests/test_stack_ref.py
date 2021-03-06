# -*- coding: utf-8 -*-


# This files contains characterization tests for ``contextlib.ExitStack``.  The
# idea is to diff these tests with those for our own ``AsyncExitStack`` in the
# hope of showing how good our asynchronous counterpart is.


import pytest

from contextlib import ExitStack
from unittest import mock


class AutoClose(object):
    """Example synchronous context manager."""

    def __init__(self, h, v=None, suppress=False):
        self._h = h
        self._v = v
        self._suppress = suppress

    def __enter__(self):
        return self._v

    def __exit__(self, etype, val, tb):
        self._h.close(etype, val, tb)
        return self._suppress


def test_exit_stack_noop():
    with ExitStack():
        pass


def test_exit_stack():

    handle = mock.MagicMock()
    with ExitStack() as stack:
        stack.enter_context(AutoClose(handle))
    handle.close.assert_called_once_with(None, None, None)


def test_exit_stack_exception_propagate():

    h1 = mock.MagicMock()
    h2 = mock.MagicMock()
    v1 = mock.MagicMock()
    v2 = mock.MagicMock()
    error = ValueError('FUUU')

    with pytest.raises(ValueError) as exc:
        with ExitStack() as stack:
            v = stack.enter_context(AutoClose(h1, v=v1))
            assert v is v1
            v = stack.enter_context(AutoClose(h2, v=v2))
            assert v is v2
            raise error
    assert exc.value is error

    h2.close.assert_called_once_with(ValueError, error, mock.ANY)
    h1.close.assert_called_once_with(ValueError, error, mock.ANY)


def test_exit_stack_exception_suppress():

    h1 = mock.MagicMock()
    h2 = mock.MagicMock()
    error = ValueError('FUUU')

    with ExitStack() as stack:
        stack.enter_context(AutoClose(h1))
        stack.enter_context(AutoClose(h2, suppress=True))
        raise error

    h2.close.assert_called_once_with(ValueError, error, mock.ANY)
    h1.close.assert_called_once_with(None, None, None)


def test_exit_stack_exception_substitution():

    h1 = mock.MagicMock()
    h2 = mock.MagicMock()
    e1 = ValueError('FUUU')
    e2 = KeyError('oops')

    class FailingAutoClose(object):
        """."""

        def __init__(self, h):
            self._h = h

        def __enter__(self):
            return self

        def __exit__(self, etype, val, tb):
            assert etype is ValueError
            assert val is e1
            assert tb
            self._h.close(etype, val, tb)
            raise e2

    with pytest.raises(KeyError) as exc:
        with ExitStack() as stack:
            stack.enter_context(AutoClose(h1))
            stack.enter_context(FailingAutoClose(h2))
            raise e1
    assert exc.value is e2

    h2.close.assert_called_once_with(ValueError, e1, mock.ANY)
    h1.close.assert_called_once_with(KeyError, e2, mock.ANY)
