.. -*- coding: utf-8 -*-

##############
  Change log
##############

* :feature:`-` Added support for calling :py:func:`aiotk.run_until_complete` to
  allow with pre-created `asyncio.Task` objects.

* :release:`0.4.0 <2017-03-14>`
* :feature:`-` Adds :py:func:`aiotk.reader`.
* :feature:`-` Adds :py:func:`aiotk.udp_server`.
* :feature:`-` Adds :py:func:`aiotk.udp_socket`.
* :feature:`-` Adds :py:func:`aiotk.run_until_complete`.

* :release:`0.3.0 <2017-03-14>`
* :feature:`-` Adds :py:class:`aiotk.TaskPool`.
* :feature:`-` Adds :py:class:`aiotk.EnsureDone`.
* :feature:`-` Adds :py:func:`aiotk.tcp_server`.
* :feature:`-` Adds :py:func:`aiotk.wait_until_cancelled`.
* :feature:`-` Adds :py:func:`aiotk.follow_through`.
* :feature:`-` Adds :py:func:`aiotk.cancel_all`.
* :feature:`-` Adds :py:func:`aiotk.cancel`.

* :release:`0.2.0 <2016-09-15>`
* :feature:`-` Adds :py:class:`aiotk.AsyncExitStack`.
* :feature:`-` Adds :py:func:`aiotk.handle_ctrlc`.
* :feature:`-` Adds :py:class:`aiotk.TCPServer`.

* :release:`0.1.0 <2016-07-28>`
* :feature:`-` Adds :py:func:`aiotk.mempipe`.
* :feature:`-` Adds :py:class:`aiotk.UnixSocketServer`.
* :feature:`-` Adds :py:func:`aiotk.monkey_patch`.
* :feature:`-` Adds :py:func:`aiotk.mock_subprocess`.
