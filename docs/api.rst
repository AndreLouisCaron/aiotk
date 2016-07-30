.. -*- coding: utf-8 -*-

#################
  API reference
#################


General utilities
=================

Streams
-------

.. autofunction:: aiotk.mempipe

   .. testcode::

      import asyncio
      from aiotk import mempipe

      async def demo():
          reader, writer = mempipe()
          writer.write('Hello, world!\n'.encode('utf-8'))
          rep = await reader.readline()
          print(rep.decode('utf-8').strip())
          writer.close()

      asyncio.get_event_loop().run_until_complete(demo())

   .. testoutput::

      Hello, world!


Testing
=======

Subprocesses
------------

.. autofunction:: aiotk.mock_subprocess

   .. testcode::

      import aiotk

      async def echo(stdin, stdout):
          line = await stdin.readline()
          while line:
              stdout.write(line)
              line = await stdin.readline()

      async def demo():
          with aiotk.mock_subprocess(echo):
              process = await asyncio.create_subprocess_exec(
                  stdin=asyncio.subprocess.PIPE,
                  stdout=asyncio.subprocess.PIPE,
              )
              stdout, stderr = await asyncio.wait_for(
                  process.communicate(input=b'Hello, world!\n'), timeout=5.0
              )
              assert stderr is None
              print(stdout.decode('utf-8').strip())

      asyncio.get_event_loop().run_until_complete(demo())

   .. testoutput::

      Hello, world!


Compatibility helpers
=====================

asyncio backports
-----------------

.. autofunction:: aiotk.monkey_patch

   .. testcode::

      import asyncio
      import aiotk

      aiotk.monkey_patch()

      async def demo():
          reader, writer = mempipe()
          writer.write('Hello, world!'.encode('utf-8'))
          rep = await reader.readuntil(b'!')
          print(rep.decode('utf-8'))
          writer.close()

      asyncio.get_event_loop().run_until_complete(demo())

   .. testoutput::

      Hello, world!


Network facilities
==================


UNIX socket server
------------------

.. autoclass:: aiotk.UnixSocketServer
   :members:

   .. testcode::

      import asyncio

      from aiotk import UnixSocketServer

      async def echo(reader, writer):
          chunk = await reader.read(256)
          while chunk:
              writer.write(chunk)
              chunk = await reader.read(256)

      async def demo():
          path = './echo.sock'
          async with UnixSocketServer(path, echo):
              reader, writer = await asyncio.open_unix_connection(path)
              writer.write('Hello, world!\n'.encode('utf-8'))
              rep = await reader.readline()
              print(rep.decode('utf-8').strip())
              writer.close()

      asyncio.get_event_loop().run_until_complete(demo())

   .. testoutput::

      Hello, world!


TCP socket server
-----------------

.. autoclass:: aiotk.TCPServer
   :members:

   .. testcode::

      import asyncio
      import random

      from aiotk import TCPServer

      async def echo(reader, writer):
          chunk = await reader.read(256)
          while chunk:
              writer.write(chunk)
              chunk = await reader.read(256)

      async def demo():
          host = '127.0.0.1'
          port = random.randint(49152, 65535)
          async with TCPServer(host, port, echo):
              reader, writer = await asyncio.open_connection(host, port)
              writer.write('Hello, world!\n'.encode('utf-8'))
              rep = await reader.readline()
              print(rep.decode('utf-8').strip())
              writer.close()

      asyncio.get_event_loop().run_until_complete(demo())

   .. testoutput::

      Hello, world!
