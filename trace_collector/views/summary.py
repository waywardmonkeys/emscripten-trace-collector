from trace_collector import events

class SummaryView(object):
  def __init__(self, heap_view):
    self.heap_view = heap_view
    self.total_allocated = 0
    self.total_allocations = 0
    self.current_allocated = 0
    self.current_allocations = 0
    self.peak_allocated = 0
    self.peak_allocations = 0

  def update(self, entry, session):
    if entry[0] == events.ALLOCATE:
      size = entry[3]
      self.total_allocated = self.total_allocated + size
      self.total_allocations = self.total_allocations + 1
      self.current_allocated = self.current_allocated + size
      self.current_allocations = self.current_allocations + 1
      self.peak_allocated = max(self.peak_allocated, self.current_allocated)
      self.peak_allocations = max(self.peak_allocations, self.current_allocations)
    elif entry[0] == events.REALLOCATE:
      old = self.heap_view.size_for_address(entry[2])
      new = entry[4]
      change = new - old
      self.current_allocated = self.current_allocated + change
      self.peak_allocated = max(self.peak_allocated, self.current_allocated)
    elif entry[0] == events.FREE:
      size = self.heap_view.size_for_address(entry[2])
      self.current_allocated = self.current_allocated - size
      self.current_allocations = self.current_allocations - 1
