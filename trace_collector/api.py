import os
from flask import abort, jsonify, make_response, request, send_from_directory
from trace_collector import app, sessions
from trace_collector.decorators import crossdomain


@app.route('/worker.js', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*', headers=['Content-Type', 'If-Modified-Since'])
def workerjs():
  return send_from_directory(os.path.join(app.root_path, 'static'),
                             'worker.js', mimetype='text/javascript')


@app.route('/api/v1/upload', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers=['Content-Type', 'If-Modified-Since'])
def upload_data():
  data = request.json
  sessionID = data[0]
  dataVersion = data[1]
  if dataVersion == 1:
    for entry in data[2]:
      sessions.add_entry(sessionID, entry)
    return jsonify([])
  else:
    print('WRONG DATA VERSION: %s' % dataVersion)
    abort(500)


@app.route('/api/v1/sessions')
@crossdomain(origin='*')
def session_index():
  return jsonify(data=sessions.session_list())


@app.route('/api/v1/session/<sessionID>/heap/events/')
@crossdomain(origin='*')
def session_heap_events_api(sessionID):
  session = sessions.session(sessionID)
  if session:
    return jsonify(data=session.get_view('heap').entries)
  else:
    abort(404)

@app.route('/api/v1/session/<sessionID>/heap/by_type/')
@crossdomain(origin='*')
def session_heap_by_type_api(sessionID):
  session = sessions.session(sessionID)
  if session:
    if request.args.get('format') == 'csv':
      csv_data = session.get_view('heap').heap_allocation_data_by_type(format='csv')
      response = make_response(csv_data)
      response.headers["Content-Disposition"] = "attachment; filename=by_type_%s.csv" % sessionID
      return response
    else:
      return jsonify({
       'data': session.get_view('heap').heap_allocation_data_by_type()
      })
  else:
    abort(404)

@app.route('/api/v1/session/<sessionID>/heap/by_size/')
@crossdomain(origin='*')
def session_heap_by_size_api(sessionID):
  session = sessions.session(sessionID)
  if session:
    return jsonify({
     'data': session.get_view('heap').heap_allocation_data_by_size()
    })
  else:
    abort(404)

@app.route('/api/v1/session/<sessionID>/heap/fragmentation/')
@crossdomain(origin='*')
def session_heap_fragmentation_api(sessionID):
  session = sessions.session(sessionID)
  if session:
    return jsonify({
     'data': session.get_view('heap').heap_fragmentation_data()
    })
  else:
    abort(404)

@app.route('/api/v1/session/<sessionID>/execution/')
@crossdomain(origin='*')
def session_execution_contexts_api(sessionID):
  session = sessions.session(sessionID)
  if session:
    return jsonify({
     'data': session.get_flattened_context_data()
    })
  else:
    abort(404)
