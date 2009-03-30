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
#        extend_attributes(value)
        return value
            
    def keyfunc(self, value):
            """
            Given the value (object) return the id
            """
            return value.id
            
    def dbget(self, key):
        # we need this because we filter out only the objects in our container by query()
        return self._query().filter_by(id=key, container_id=self.container_id).all()[0]


class Content(rdb.Model):
    content_id = Column('content_id', Integer, primary_key=True)
    id = Column('id', String)
    title = Column('title', String(127))
    container_id = Column('container_id', Integer)
    portal_type = Column('portal_type', String)

class FolderContainer(Folder, rdb.Model):
    rdb.tablename('content')
    rdb.reflected()

class Contentmirrorgrok(grok.Application, FolderContainer):
    def _query(self):
        session = rdb.Session()
        return session.query(Content)

    def query(self):
        return self._query().filter_by(container_id=None)
        
    def dbget(self, key):
        # we need this because we filter out only the objects in our container by query()
        return self._query().filter_by(id=key, container_id=None).all()[0]


class Index(grok.View):
    grok.context(Contentmirrorgrok)
    def contents(self):
        session = rdb.Session()
        for content in session.query(Content).all():
            yield located(content, self.context, str(content.id))
