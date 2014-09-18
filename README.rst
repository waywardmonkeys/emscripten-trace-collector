======================
Trace Collector Server
======================

A server for collecting tracing data from emscripten-compiled
applications including memory profiling information.

Getting Started
===============

Using virtualenvwrapper
-----------------------

This is the preferred mechanism for running this server.

If this is your first time with ``virtualenvwrapper``,
you will need to install it.

Next up, create your virtual env, from within the directory
where you cloned this GitHub repo::

    mkvirtualenv -a `pwd` -r requirements.txt emscripten-trace-collector

Now, whenever you open a new shell and want to get everything
ready and using the right virtualenv::

    workon emscripten-trace-collector

(Note that ``workon`` assumes that you've correctly installed
``virtualenvwrapper`` and added it to the startup files for
your shell.)

Now, you can run the server::

    python ./runserver.py

Or run the debug server::

    python ./debugrunserver.py


Using virtualenv
----------------

Set up a Python virtual environment::

    virtualenv venv
    source venv/bin/activate

Install the dependencies::

    pip install -r requirements.txt

Run the server::

    source venv/bin/activate
    python ./runserver.py

The server can also run in a debug mode that is useful while
developing it::

    source venv/bin/activate
    python ./debugrunserver.py


Using your global Python install
--------------------------------

I really recommend that you use ``virtualenvwrapper`` instead.

If not, then install the dependencies::

    pip install -r requirements.txt

Run the server::

    python ./runserver.py

Or run the server in debug mode::

    python ./debugrunserver.py
