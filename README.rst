======================
Trace Collector Server
======================

A server for collecting tracing data from emscripten-compiled
applications including memory profiling information.


Running The Server
==================

Once you have set up your environment and installed the
dependencies as detailed below, you can run the server::

   python ./run-server.py

There is an optional ``gevent`` backed server which can
be used, but isn't necessary. To run this, you will need
to install the ``optional-requirements.txt``::

    pip install -r optional-requirements.txt

And then run that server::

    python ./run-gevent-server.py


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

Using virtualenv
----------------

Set up a Python virtual environment::

    virtualenv venv
    source venv/bin/activate

Install the dependencies::

    pip install -r requirements.txt

Now, whenever you open a new shell and want to get everything
ready and using the right virtualenv::

    source venv/bin/activate

Using your global Python install
--------------------------------

I really recommend that you use ``virtualenvwrapper`` instead.

If not, then install the dependencies::

    pip install -r requirements.txt

This will install the dependencies into the global / system
Python install.
