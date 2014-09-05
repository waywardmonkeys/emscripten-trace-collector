from trace_collector import events

class LogMessageView(object):
  def __init__(self):
    self.entries = []

  def update(self, entry, session):
    if entry[0] == events.LOG_MESSAGE:
      t = entry[1:]
      t.append(session.context)
      self.entries.append(t)
