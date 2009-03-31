import grok
from megrok import rdb

from zope.location.location import located

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import relation

from z3c.saconfig import EngineFactory, GloballyScopedSession
from z3c.saconfig.interfaces import IEngineFactory, IEngineCreatedEvent

TEST_DSN = 'sqlite:////tmp/contentmirror.db'
engine_factory = EngineFactory(TEST_DSN)
scoped_session = GloballyScopedSession()
grok.global_utility(engine_factory, direct=True)
grok.global_utility(scoped_session, direct=True)

# we set up the SQLAlchemy metadata object to which we'll associate all the
# SQLAlchemy-backed objects
metadata = rdb.MetaData()
# we declare to megrok.rdb that all SQLAlchemy-managed mapped instances
# are associated with this metadata. This directive can also be used
# on a per rdb.Model subclass basis
rdb.metadata(metadata)
# we make sure that when the engine is created we set up the metadata for it
@grok.subscribe(IEngineCreatedEvent)
def setUpDatabase(event):
    rdb.setupDatabase(metadata)

class Folder(rdb.QueryContainer):
    def _query(self):
        session = rdb.Session()
        return session.query(Content)
    
    def query(self):
        session = rdb.Session()
        return session.query(Content).filter_by(container_id=self.content_id)

    def convert(self, value):
        # if the result is folderish type then return a new container
        # otherwise a content type
        # possibly
        if value.portal_type.endswith('Folder'):
            session = rdb.Session()
            value = session.query(FolderContainer).get(value.content_id)
        else:
            pass
        return value
            
    def keyfunc(self, value):
        """
        Given the value (object) return the id
        """
        return value.id
        
    def dbget(self, key):
        # we need this because we filter out only the objects in our container by query()
        return self._query().filter_by(id=key, container_id=self.content_id).first()

class Content(rdb.Model):
    __table_args__ = dict()
    rdb.reflected()

class FolderContainer(Folder, rdb.Model):
    __table_args__ = dict(useexisting=True)
    rdb.tablename('content')
    rdb.reflected()

class Contentmirrorgrok(grok.Application, Folder):
    def _query(self):
        session = rdb.Session()
        return session.query(Content)

    def query(self):
        return self._query().filter_by(container_id=None)
        
    def dbget(self, key):
        # we need this because we filter out only the objects in our container by query()
        return self._query().filter_by(id=key, container_id=None).first()

class ContentIndex(grok.View):
    grok.context(Content)
    grok.name('index')
    
    def render(self):
        return "My title is %s" % self.context.title
    
class Index(grok.View):
    grok.context(Folder)
    
    def contents(self):
        return self.context.values()
