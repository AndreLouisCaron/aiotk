.. -*- coding: utf-8 -*-

#################
  API reference
#################

Contents:

- :py:func:`aiotk.mempipe`
- :py:class:`aiotk.UnixSocketServer`

Details
=======

.. autofunction:: aiotk.mempipe

.. autoclass:: aiotk.UnixSocketServer

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
