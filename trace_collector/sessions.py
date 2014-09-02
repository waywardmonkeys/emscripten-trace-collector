from trace_collector import events
from trace_collector.views import heap, memory_layout, summary, log_messages


SESSIONS = {}


def add_entry(sessionID, entry):
  session = SESSIONS.get(sessionID, None)
  if not session:
    session = Session(sessionID)
    SESSIONS[sessionID] = session
  session.update(entry)


def session_list():
  return sorted(SESSIONS.values(), key=lambda s: s.sessionID)


def session(sessionID):
  return SESSIONS.get(sessionID)


class Session(object):
  def __init__(self, sessionID):
    self.FRAME_ID = 0
    self.sessionID = sessionID
    self.name = sessionID
    self.application = 'unknown'
    self.username = 'unknown'
    self.currentFrame = None
    self.frames = []
    self.entries = []
    self.errors = []
    self.views = {}
    self.heapView = heap.HeapView()
    self.views['memory_layout'] = memory_layout.MemoryLayoutView()
    self.views['summary'] = summary.SummaryView(self.heapView)
    self.views['log_messages'] = log_messages.LogMessageView()
    self.context = ContextNode(None, 'Root')
    ## Cached data ##
    self.peak_allocated = 0


  def next_frame_id(self):
    self.FRAME_ID = self.FRAME_ID + 1
    return self.FRAME_ID


  def update(self, entry):
    ### Some configuration options ... ###
    if entry[0] == events.APPLICATION_NAME:
      self.application = entry[1]
      return
    if entry[0] == events.SESSION_NAME:
      self.name = entry[1]
    if entry[0] == events.USER_NAME:
      self.username = entry[1]
      return
    self.entries.append(entry)
    ### Update context ###
    if entry[0] == events.ENTER_CONTEXT:
      self.context = self.context.get_child(entry[2])
      self.context.enter(entry[1])
    elif entry[0] == events.EXIT_CONTEXT:
      self.context.exit(entry[1])
      self.context = self.context.parent
    else:
      self.context.update(entry, self.heapView)
    ### Record errors ###
    if entry[0] == events.REPORT_ERROR:
      self.errors.append(SessionError(entry[1], entry[2], entry[3]))
      return
    ### Update per-frame data ###
    if entry[0] == events.FRAME_END:
      self.currentFrame.complete(entry[1])
      self.frames.append(self.currentFrame)
      self.currentFrame = None
    elif entry[0] == events.FRAME_START:
      if self.currentFrame is not None:
        print 'self.currentFrame is not None!'
        self.currentFrame.complete(entry[1])
        self.frames.append(self.currentFrame)
      self.currentFrame = SessionFrame(self.next_frame_id(), entry[1])
    elif self.currentFrame:
      self.currentFrame.update(entry, self.heapView)
    ### Update views ###
    # We have to update the heap before the others as they
    # may query it. Unless it is a 'fr' event, in which case
    # we need to do it after we update the other views.
    if entry[0] != events.FREE:
      self.heapView.update(entry, self)
    for view in self.views.values():
      view.update(entry, self)
    if entry[0] == events.FREE:
      self.heapView.update(entry, self)


  def get_view(self, viewName):
    if viewName == 'heap':
      return self.heapView
    return self.views.get(viewName, None)


  def update_cached_data(self):
    self.peak_allocated = self.get_view('summary').peak_allocated


class SessionError(object):
  __slots__ = ['timestamp', 'error', 'callstack']
  def __init__(self, timestamp, error, callstack):
    self.timestamp = timestamp
    self.error = error
    self.callstack = callstack

class SessionFrame(object):
  __slots__ = [
    'frame_id', 'start', 'end', 'duration', 'alloc_count',
    'alloc_bytes', 'free_count', 'free_bytes',
    'delta_bytes'
  ]
  def __init__(self, frame_id, timestamp):
    self.frame_id = frame_id
    self.start = timestamp
    self.end = 0
    self.duration = 0
    self.alloc_count = 0
    self.alloc_bytes = 0
    self.free_count = 0
    self.free_bytes = 0
    self.delta_bytes = 0

  def update(self, entry, heapView):
    if entry[0] == events.ALLOCATE:
      size = entry[3]
      self.alloc_count = self.alloc_count + 1
      self.alloc_bytes = self.alloc_bytes + size
    elif entry[0] == events.REALLOCATE:
      old = heapView.size_for_address(entry[2])
      new = entry[4]
      change = new - old
      if change > 0:
        self.alloc_bytes = self.alloc_bytes + change
      else:
        self.free_bytes = self.free_bytes + -(change)
    elif entry[0] == events.FREE:
      size = heapView.size_for_address(entry[2])
      self.free_count = self.free_count + 1
      self.free_bytes = self.free_bytes + size

  def complete(self, timestamp):
    self.end = timestamp
    self.duration = self.end - self.start
    self.delta_bytes = self.alloc_bytes - self.free_bytes

class ContextNode(object):
  __slots__ = [
    'parent', 'name', 'full_name', 'children',
    'last_enter_timestamp', 'times_entered', 'total_time_elapsed',
    'alloc_count', 'alloc_bytes', 'free_count', 'free_bytes',
    'delta_bytes'
  ]
  def __init__(self, parent, name):
    self.parent = parent
    if parent:
      parent.children.append(self)
    self.children = []
    self.name = name
    self.full_name = self.build_full_name()
    self.last_enter_timestamp = 0
    self.times_entered = 0
    self.total_time_elapsed = 0
    self.alloc_count = 0
    self.alloc_bytes = 0
    self.free_count = 0
    self.free_bytes = 0
    self.delta_bytes = 0

  def get_child(self, name):
     for child in self.children:
       if child.name == name:
         return child
     return ContextNode(self, name)

  def enter(self, timestamp):
    self.times_entered = self.times_entered + 1
    self.last_enter_timestamp = timestamp

  def exit(self, timestamp):
    self.total_time_elapsed = self.total_time_elapsed + (timestamp - self.last_enter_timestamp)
    self.delta_bytes = self.alloc_bytes - self.free_bytes

  def update(self, entry, heapView):
    if entry[0] == events.ALLOCATE:
      size = entry[3]
      self.alloc_count = self.alloc_count + 1
      self.alloc_bytes = self.alloc_bytes + size
    elif entry[0] == events.REALLOCATE:
      old = heapView.size_for_address(entry[2])
      new = entry[4]
      change = new - old
      if change > 0:
        self.alloc_bytes = self.alloc_bytes + change
      else:
        self.free_bytes = self.free_bytes + -(change)
    elif entry[0] == events.FREE:
      size = heapView.size_for_address(entry[2])
      self.free_count = self.free_count + 1
      self.free_bytes = self.free_bytes + size

  def build_context_stack(self):
    node = self
    stack = []
    while node.parent is not None:
      stack.append(node)
      node = node.parent
    return stack

  def build_full_name(self):
    stack = self.build_context_stack()
    return ' << '.join([node.name for node in stack])
