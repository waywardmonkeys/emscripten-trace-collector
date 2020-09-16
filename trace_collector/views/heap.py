from trace_collector import events, json
import csv
from io import StringIO

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
      he = HeapEntry(self.next_event_id(), session.FRAME_ID, EVENT_ALLOCATE, entry[1], address, size, session.context)
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
      freeEntry = HeapEntry(self.next_event_id(), session.FRAME_ID, EVENT_FREE, timestamp, address, 0, session.context)
      self.entries.append(freeEntry)
      oldEntry = self.entries_by_address.get(address)
      if oldEntry:
        freeEntry.size = oldEntry.size
        oldEntry.lifetime = timestamp - oldEntry.timestamp
        freeEntry.lifetime = oldEntry.lifetime
        oldEntry.matching_event_id = freeEntry.id
        freeEntry.matching_event_id = oldEntry.id
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
        print('NO ADDRESS MAPPING FOUND FOR %s TO ANNOTATE TYPE "%s"' % (entry[1], entry[2]))
    elif entry[0] == events.ASSOCIATE_STORAGE_SIZE:
      he = self.entries_by_address.get(entry[1])
      if he:
        he.associated_storage_size = entry[2]
      else:
        print('NO ADDRESS MAPPING FOUND FOR %s TO ASSOCIATE STORAGE SIZE "%s"' % (entry[1], entry[2]))

  def size_for_address(self, address):
    entry = self.entries_by_address.get(address)
    if entry:
      return entry.size
    return 0

  def heap_allocation_data_by_type(self, format=None):
    type_data = {}
    allocation_entries = [e for e in self.entries if e.event == EVENT_ALLOCATE]
    id = 0
    for e in allocation_entries:
      d = type_data.setdefault(e.type, {
        'id': 0,
        'type': e.type,
        'count_all': 0,
        'count_live': 0,
        'total_bytes_all': 0,
        'total_bytes_live': 0,
        'total_storage_size_all': 0,
        'total_storage_size_live': 0
      })
      if not d['id']:
        d['id'] = id
        id += 1
      d['count_all'] += 1
      d['total_bytes_all'] += e.size
      d['total_storage_size_all'] += e.associated_storage_size
      if not e.matching_event_id:
        d['count_live'] += 1
        d['total_bytes_live'] += e.size
        d['total_storage_size_live'] += e.associated_storage_size
    def avg(total, count):
      if count > 0:
        return int(total / float(count))
      else:
        return 0
    for d in type_data.values():
      d['average_bytes_all'] = avg(d['total_bytes_all'], d['count_all'])
      d['average_bytes_live'] = avg(d['total_bytes_live'], d['count_live'])
      d['average_storage_size_all'] = avg(d['total_storage_size_all'], d['count_all'])
      d['average_storage_size_live'] = avg(d['total_storage_size_live'], d['count_live'])
    types = type_data.values()
    # Use negation to reverse the sort
    types.sort(lambda x,y: cmp(-x['count_all'], -y['count_all']))
    if format == 'csv':
      csv_data = StringIO.StringIO()
      fields = [
        'id',
        'type',
        'count_all',
        'count_live',
        'total_bytes_all',
        'total_bytes_live',
        'average_bytes_all',
        'average_bytes_live',
        'total_storage_size_all',
        'total_storage_size_live',
        'average_storage_size_all',
        'average_storage_size_live',
      ]
      writer = csv.DictWriter(csv_data, fields)
      writer.writeheader()
      for d in types:
        writer.writerow(d)
      return csv_data.getvalue()
    return types

  def heap_allocation_data_by_size(self):
    size_data = {}
    allocation_entries = [e for e in self.entries if e.event == EVENT_ALLOCATE]
    for e in allocation_entries:
      d = size_data.setdefault(e.size, {
        'id': e.size,
        'size': e.size,
        'count_all': 0,
        'count_live': 0,
        'bytes_all': 0,
        'bytes_live': 0
      })
      d['count_all'] += 1
      d['bytes_all'] += e.size
      if not e.matching_event_id:
        d['count_live'] += 1
        d['bytes_live'] += e.size
    sizes = size_data.values()
    sizes_sorted = sorted(sizes, cmp=lambda x,y: cmp(x['size'], y['size']))
    return sizes

  def heap_fragmentation_data(self):
    allocations = self.entries_by_address.values()
    holes = []
    lastAllocationEnd = 0
    if len(allocations) > 1:
      allocations.sort(lambda x,y: cmp(x.address, y.address))
      lastAllocationEnd = allocations[0].address
      for allocation in allocations:
        allocationStart = allocation.address
        if lastAllocationEnd < allocationStart:
          holes.append([lastAllocationEnd, allocationStart - lastAllocationEnd])
        lastAllocationEnd = allocationStart + allocation.size
    hole_data = {}
    total_hole_size = 0
    for hole in holes:
      hole_size = hole[1]
      total_hole_size += hole_size
      d = hole_data.setdefault(hole_size, {
        'id': hole_size,
        'size': hole_size,
        'count': 0,
        'bytes': 0
      })
      d['count'] += 1
      d['bytes'] += hole_size
    holes = hole_data.values()
    holes.sort(lambda x,y: cmp(x['size'], y['size']))
    return {
      'holes': holes,
      'fragmentation_percentage': (total_hole_size / float(lastAllocationEnd)) * 100,
      'total_hole_size': total_hole_size,
      'last_allocation_top': lastAllocationEnd
    }

class HeapEntry(json.Serializable):
  __slots__ = [
    'id', 'frame_id', 'event', 'timestamp', 'address', 'size', 'type',
    'context', 'lifetime', 'matching_event_id', 'allocated_memory',
    'associated_storage_size'
  ]
  def __init__(self, id, frame_id, event, timestamp, address, size, context):
    self.id = id
    self.frame_id = frame_id
    self.event = event
    self.timestamp = timestamp
    self.address = address
    self.size = size
    self.type = None
    self.context = context
    self.lifetime = None
    self.matching_event_id = None
    self.allocated_memory = 0
    self.associated_storage_size = 0

  def serialize(self):
    return {
      'id': self.id,
      'frame_id': self.frame_id,
      'event': self.event,
      'timestamp': self.timestamp,
      'address': self.address,
      'size': self.size,
      'type': self.type,
      'context': self.context.full_name,
      'lifetime': self.lifetime,
      'matching_event_id': self.matching_event_id,
      'allocated_memory': self.allocated_memory,
      'associated_storage_size': self.associated_storage_size
    }
