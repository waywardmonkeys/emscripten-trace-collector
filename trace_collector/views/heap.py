from trace_collector import events, json

EVENT_ALLOCATE = 'allocate'
EVENT_FREE = 'free'
EVENT_REALLOCATE = 'reallocate'

class HeapView(object):
  def __init__(self):
    self.EVENT_ID = 0
    self.entries = []
    self.entries_by_address = {}
    self.memory_errors = []
    self.allocated_memory = 0

  def next_event_id(self):
    self.EVENT_ID = self.EVENT_ID + 1
    return self.EVENT_ID

  def update(self, entry, session):
    if entry[0] == events.ALLOCATE:
      address = entry[2]
      size = entry[3]
      he = HeapEntry(session.FRAME_ID, self.next_event_id(), EVENT_ALLOCATE, entry[1], address, size, session.context)
      self.allocated_memory = self.allocated_memory + size
      he.allocated_memory = self.allocated_memory
      self.entries.append(he)
      self.entries_by_address[address] = he
    elif entry[0] == events.REALLOCATE:
      # XXX: IMPLEMENT
      pass
    elif entry[0] == events.FREE:
      timestamp = entry[1]
      address = entry[2]
      freeEntry = HeapEntry(session.FRAME_ID, self.next_event_id(), EVENT_FREE, timestamp, address, 0, session.context)
      self.entries.append(freeEntry)
      oldEntry = self.entries_by_address.get(address)
      if oldEntry:
        freeEntry.size = oldEntry.size
        oldEntry.lifetime = timestamp - oldEntry.timestamp
        freeEntry.lifetime = oldEntry.lifetime
        oldEntry.matching_event_id = freeEntry.event_id
        freeEntry.matching_event_id = oldEntry.event_id
        freeEntry.type = oldEntry.type
        del self.entries_by_address[address]
        self.allocated_memory = self.allocated_memory - freeEntry.size
        freeEntry.allocated_memory = self.allocated_memory
      else:
        self.memory_errors.append(["Invalid free", timestamp, address])
    elif entry[0] == events.ANNOTATE_TYPE:
      he = self.entries_by_address.get(entry[1])
      if he:
        he.type = entry[2]
      else:
        print 'NO ADDRESS MAPPING FOUND FOR %s TO ANNOTATE TYPE "%s"' % (entry[1], entry[2])

  def size_for_address(self, address):
    entry = self.entries_by_address.get(address)
    if entry:
      return entry.size
    return 0

  def heap_layout(self):
    allocations = self.entries_by_address.values()
    holes = []
    if len(allocations) > 1:
      allocations.sort(lambda x,y: cmp(x.address, y.address))
      lastAllocationEnd = allocations[0].address
      for allocation in allocations:
        allocationStart = allocation.address
        if lastAllocationEnd < allocationStart:
          holes.append([lastAllocationEnd, allocationStart - lastAllocationEnd])
        lastAllocationEnd = allocationStart + allocation.size
    return {
      'all_allocations': [e for e in self.entries if e.event == EVENT_ALLOCATE],
      'live_allocations': allocations,
      'holes': holes
    }

class HeapEntry(json.Serializable):
  __slots__ = [
    'frame_id', 'event_id', 'event', 'timestamp', 'address', 'size', 'type',
    'context', 'lifetime', 'matching_event_id', 'allocated_memory'
  ]
  def __init__(self, frame_id, event_id, event, timestamp, address, size, context):
    self.frame_id = frame_id
    self.event_id = event_id
    self.event = event
    self.timestamp = timestamp
    self.address = address
    self.size = size
    self.type = None
    self.context = context
    self.lifetime = None
    self.matching_event_id = None
    self.allocated_memory = 0

  def serialize(self):
    return {
      'frame_id': self.frame_id,
      'event_id': self.event_id,
      'event': self.event,
      'timestamp': self.timestamp,
      'address': self.address,
      'size': self.size,
      'type': self.type,
      'context': self.context.full_name,
      'lifetime': self.lifetime,
      'matching_event_id': self.matching_event_id,
      'allocated_memory': self.allocated_memory
    }
