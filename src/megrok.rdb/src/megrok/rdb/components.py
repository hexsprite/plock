from sqlalchemy.orm.collections import MappedCollection, collection
from sqlalchemy.orm.util import identity_key

from zope.interface import implements
from zope.location.interfaces import ILocation

from grokcore.component import Context
from grok.interfaces import IContainer

from megrok.rdb import directive
from z3c.saconfig import Session

class Model(Context):
    implements(ILocation)

    __parent__ = None
    __name__ = None
    
    def __init__(self, **kwargs):
        # XXX can we use the __init__ that sqlalchemy.ext.declarative sets up?
        for k in kwargs:
            if not hasattr(type(self), k):
                raise TypeError('%r is an invalid keyword argument for %s' %
                                (k, type(self).__name__))
            setattr(self, k, kwargs[k])

class LocatedModel(Model):
    implements(ILocation)

    @property
    def __parent__(self):
        return

    @property
    def __name__(self):
        return
    
def default_keyfunc(node):
    primary_keys = node.__table__.primary_key.keys()
    if len(primary_keys) == 1:
        return getattr(node, primary_keys[0])
    else:
        raise RuntimeError(
            "don't know how to do keying with composite primary keys")

class Container(MappedCollection):
    implements(IContainer, ILocation)

    __parent__ = None
    __name__ = None
    
    def __init__(self, *args, **kw):
        rdb_key = directive.key.bind().get(self)
        if rdb_key:
            keyfunc = lambda node:getattr(node, rdb_key)
        elif hasattr(self, 'keyfunc'):
            keyfunc = self.keyfunc
        else:
            keyfunc = default_keyfunc
        MappedCollection.__init__(self, keyfunc=keyfunc)

    @collection.on_link
    def on_link(self, adapter):
        if adapter is not None:
            self.__parent__ = adapter.owner_state.obj()
            self.__name__ = unicode(adapter.attr.key)
        else:
            # unlinking collection from parent
            self.__parent__ = None
            self.__name__ = None
            
    def __setitem__(self, key, item):
        key = unicode(key)
        self._receive(item, key)
        MappedCollection.__setitem__(self, key, item)

    def __delitem__(self, key):
        key = unicode(key)
        self._release(self[key])
        MappedCollection.__delitem__(self, key)
        
    def _receive(self, item, key):
        item.__name__ = key
        item.__parent__ = self

    def _release(self, item):
        del item.__name__
        del item.__parent__
    
    @collection.internally_instrumented
    @collection.appender
    def set(self, value, _sa_initiator=None):
        key = self.keyfunc(value)
        if key is None:
            session = Session()
            session.flush()
            key = self.keyfunc(value)
        self.__setitem__(key, value, _sa_initiator)

class QueryContainer(object):
    """A read-only Container backed by set of SQLAlchemy queries.

    This container is often used as the "root" object for an application.
    """
    # XXX should really only implement IReadContainer, but this requires
    # a bit of refactoring in Grok
    implements(IContainer, ILocation)

    def query(self):
        """Implement this returning the result of a query.
        """
        raise NotImplementedError

    def convert(self, value):
        """Override this to convert output of query container.
        """
        return value

    def __getitem__(self, key):
        result = self.dbget(key)
        if result is None:
            raise KeyError(key)
        result = self.convert(result)
        result.__parent__ = self
        result.__name__ = key
        return result

    def dbget(self, key):        
        return self.query().get(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
    
    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def has_key(self, key):
        return key in self

    def keys(self):
        result = []
        # XXX probably not the most efficient way to do this
        for v in self.query().all():
            result.append(self.keyfunc(v))
        return result

    def __iter__(self):
        for key in self.keys():
            yield key
    
    def values(self):
        result = []
        for v in self.query().all():
            converted = self.convert(v)
            converted.__parent__ = self
            converted.__name__ = self.keyfunc(v)
            result.append(converted)
        return result
        
    def items(self):
        result = []
        for v in self.query().all():
            converted = self.convert(v)
            converted.__parent__ = self
            key = converted.__name__ = self.keyfunc(v)
            result.append((key, converted))
        return result

    def __len__(self):
        return self.query().count()
    
    def keyfunc(self, value):
        """Get the key for this value.
        """
        # XXX this isn't very general...
        class_, key_tuple = identity_key(instance=value)
        return unicode(key_tuple[0])

