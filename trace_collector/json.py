from flask.json import JSONEncoder

class Serializable(object):
  pass

class TraceCollectorJSONEncoder(JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Serializable):
      return obj.serialize()
    return super(TraceCollectorJSONEncoder, self).default(obj)
