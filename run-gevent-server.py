#! /usr/bin/env python

from trace_collector import app

if (sys.version_info > (3, 0)):
    from wsgiref.simple_server import make_server

    with make_server('', 5000, app) as httpd:
        print("Serving HTTP on port 5000...")

        # Respond to requests until process is killed
        httpd.serve_forever()

        # Alternative: serve one request, then exit
        httpd.handle_request()
else:
    from gevent.wsgi import WSGIServer

    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
