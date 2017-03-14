# -*- coding: utf-8 -*-


import asyncio
import inspect
import os
import signal as _signal
import sys
import traceback

from contextlib import contextmanager
from itertools import count
from unittest import mock

from .mempipe import mempipe


def call_with_minimal_args(f, **kwds):
    spec = inspect.signature(f)
    kwds = {
        k: kwds[k] for k, p in spec.parameters.items()
        if p.kind != inspect.Parameter.VAR_KEYWORD
    }
    return f(**kwds)


class OutputStreamAdapter(object):
    """StreamWriter that wraps a file-like object."""

    def __init__(self, stream):
        self._stream = stream

    def write(self, data):
        assert isinstance(data, bytes)
        self._stream.write(data.decode('utf-8'))

    def writelines(self, lines):
        for line in lines:
            self._stream.write(line.decode('utf-8'))
            self._stream.write('\n')

    def can_write_eof(self):
        return True

    # TODO: test this without closing the "real" sys.stdout!
    def write_eof(self):
        # self._stream.close()
        pass

    async def drain(self):
        self._stream.flush()


class Process(object):
    """Mock for ``asyncio.subprocess.Process``."""

    def __init__(self, *, pid, run, argv=[], env=None, kwds={},
                 stdin=None, stdout=None, stderr=None, limit=None, loop=None):

        self._loop = loop or asyncio.get_event_loop()
        self._pid = pid

        # Handle standard input redirection.
        if stdin == asyncio.subprocess.PIPE:
            stdin, self._stdin = mempipe(limit=limit, loop=loop)
        else:
            # TODO: wrap `sys.stdin` in a `StreamReader`.
            stdin, self._stdin = None, None

        # Handle standard output redirection.
        if stdout == asyncio.subprocess.PIPE:
            self._stdout, stdout = mempipe(limit=limit, loop=loop)
        else:
            stdout = stdout or sys.stdout
            self._stdout, stdout = None, OutputStreamAdapter(stdout)

        # Handle standard error redirection.
        if stderr == asyncio.subprocess.PIPE:
            self._stderr, stderr = mempipe(limit=limit, loop=loop)
        else:
            stderr = stderr or sys.stderr
            self._stderr, stderr = None, OutputStreamAdapter(stderr)

        # Mock signal handling.
        self._signals = asyncio.Queue()

        # Start the application-defined process simulation.
        self._done = asyncio.Event(loop=loop)
        self._task = self._loop.create_task(self._run_wrapper(
            run,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            signals=self._signals,
            env=env or {k: v for k, v in os.environ.items()},
            argv=argv,
            kwds=kwds,
        ))

        # Keep a reference to the streams, we'll need them later.
        self._w_stdout = stdout
        self._w_stderr = stderr

        # Process exit code is undefined until the simulation completes.
        self._returncode = None

    async def _run_wrapper(self, run, *, stdout, stderr, **kwds):
        try:
            return await call_with_minimal_args(
                run, stdout=stdout, stderr=stderr, **kwds
            )
        except asyncio.CancelledError:
            return 1
        finally:
            await stdout.drain()
            await stderr.drain()
            self._done.set()

    @property
    def pid(self):
        return self._pid

    @property
    def stdin(self):
        return self._stdin

    @property
    def stdout(self):
        return self._stdout

    @property
    def stderr(self):
        return self._stderr

    async def wait(self):
        await asyncio.wait({self._task})
        await self._done.wait()
        e = self._task.exception()
        if e is None:
            r = self._task.result()
            if r is None:
                r = 0
            self._returncode = r
        else:
            # Format traceback and send it to stderr (as if it had been printed
            # in the child process' output).
            self._w_stderr.writelines(
                line.encode('utf-8')
                for line in traceback.format_exception(
                    e.__class__, e, e.__traceback__
                )
            )
            self._returncode = 1
        self._w_stdout.write_eof()
        self._w_stderr.write_eof()
        return self._returncode

    async def communicate(self, input=None):
        if self._stdin:
            self._stdin.write(input)
            self._stdin.write_eof()
        await self.wait()
        stdout = None
        if self._stdout:
            stdout = await self._stdout.read()
        stderr = None
        if self._stderr:
            stderr = await self._stderr.read()
        return stdout, stderr

    def send_signal(self, signal):
        self._signals.put_nowait(signal)

    def terminate(self):
        self._task.cancel()

    def kill(self):
        if sys.platform == 'win32':
            self.terminate()
        else:
            # NOTE: for a real process, we'd send SIGKILL, which would then be
            #       passed as SIGINT to the application, but we don't have a
            #       kernel to make that substution here.
            self.send_signal(_signal.SIGINT)

    @property
    def returncode(self):
        return self._returncode


@contextmanager
def mock_subprocess(run, loop=None):
    """Calls ``run()`` instead of spawning a sub-process.

    :param run: A coroutine function that simulates the sub-process.  Can
     return ``None`` or ``0`` to simulate successful process execution or a
     non-zero error code to simulate sub-process terminate with a non-zero exit
     code.  If an exception is raised, the result is 1 (non-zero).  This
     function can accept a variable number of arguments, see below.

    Dependency injection is used with the ``run()`` coroutine function to pass
    only arguments that are declared in the function's signature.  Omit all but
    the arguments you intend to use.  Here are all the available arguments:

    - ``argv``: a list of strings passed as positional arguments to
      ``asyncio.create_subprocess_exec()``.
    - ``stdin``: an ``asyncio.StreamReader`` instance.  When output is not
      redirected, this reads from the "real" ``sys.stdin``.
    - ``stdout``: an ``asyncio.StreamWriter`` instance.  When output is not
      redirected, this writes to the "real" ``sys.stdout``.
    - ``stderr``: an ``asyncio.StreamWriter`` instance.  When output is not
      redirected, this writes to the "real" ``sys.stderr``.
    - ``env``: a ``dict`` containing environment variables passed to
      ``asyncio.create_subprocess_exec()``.
    - ``signals``: an ``asyncio.Queue`` object that receives integers passed to
      ``asyncio.Process.send_signal()``.
    - ``kwds``: extra keyword arguments passed to
      ``asyncio.create_subprocess_exec()``.

    .. versionadded: 0.1

    """

    loop = loop or asyncio.get_event_loop()

    pid = count(start=1)

    def create_subprocess_exec(*args, stdin=None, stdout=None, env=None,
                               stderr=None, loop=None, limit=None, **kwds):
        """Mock for ``asyncio.create_subprocess_exec()``."""
        loop = loop or asyncio.get_event_loop()
        f = asyncio.Future()
        process = Process(
            pid=next(pid),
            run=run,
            loop=loop,
            argv=list(args),
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            env=env,
            limit=limit,
            kwds=kwds,
        )
        loop.call_soon(f.set_result, process)
        return f

    with mock.patch('asyncio.create_subprocess_exec', create_subprocess_exec):
        yield
