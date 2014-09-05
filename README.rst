Trace Collector Server
======================

A server for collecting tracing data from emscripten-compiled
applications including memory profiling information.

Getting Started
---------------

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
