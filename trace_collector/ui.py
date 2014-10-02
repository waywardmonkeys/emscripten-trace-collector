from flask import abort, render_template
from trace_collector import app, sessions


@app.route('/')
def index():
  ss = sessions.session_list()
  for s in ss:
    s.update_cached_data()
  return render_template('index.html', sessions=ss)

@app.route('/session/<sessionID>/')
def session_overview(sessionID):
  session = sessions.session(sessionID)
  if session:
    return render_template('session/index.html', session=session,
                           summary=session.get_view('summary'),
                           memory_layout=session.get_view('memory_layout'))
  else:
    abort(404)

@app.route('/session/<sessionID>/heap/events/')
def session_heap_events(sessionID):
  session = sessions.session(sessionID)
  if session:
    return render_template('session/heap/events.html', session=session)
  else:
    abort(404)

@app.route('/session/<sessionID>/heap/size/')
def session_heap_size(sessionID):
  session = sessions.session(sessionID)
  if session:
    return render_template('session/heap/size.html', session=session)
  else:
    abort(404)

@app.route('/session/<sessionID>/heap/type/')
def session_heap_type(sessionID):
  session = sessions.session(sessionID)
  if session:
    return render_template('session/heap/type.html', session=session)
  else:
    abort(404)

@app.route('/session/<sessionID>/heap/fragmentation/')
def session_heap_fragmentation(sessionID):
  session = sessions.session(sessionID)
  if session:
    return render_template('session/heap/fragmentation.html', session=session)
  else:
    abort(404)

@app.route('/session/<sessionID>/execution/')
def session_execution_contexts(sessionID):
  session = sessions.session(sessionID)
  if session:
    return render_template('session/execution.html', session=session)
  else:
    abort(404)

@app.route('/session/<sessionID>/log_messages/')
def session_log_messages(sessionID):
  session = sessions.session(sessionID)
  if session:
    return render_template('session/log_messages.html', session=session,
                           log_messages=session.get_view('log_messages'))
  else:
    abort(404)

@app.route('/session/<sessionID>/frames/')
def session_frames(sessionID):
  session = sessions.session(sessionID)
  if session:
    return render_template('session/frames.html', session=session)
  else:
    abort(404)

@app.route('/session/<sessionID>/errors/')
def session_errors(sessionID):
  session = sessions.session(sessionID)
  if session:
    return render_template('session/errors.html', session=session)
  else:
    abort(404)
