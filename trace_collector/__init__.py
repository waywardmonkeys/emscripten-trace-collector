import os
from flask import Flask, render_template, send_from_directory
from trace_collector import json

app = Flask(__name__)
app.json_encoder = json.TraceCollectorJSONEncoder

import trace_collector.api
import trace_collector.ui


@app.route('/favicon.ico')
def favicon():
  return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.errorhandler(404)
def page_not_found(error):
  return render_template('errors/404.html'), 404
