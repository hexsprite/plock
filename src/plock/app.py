import grok
from megrok import rdb

from z3c.saconfig import EngineFactory, GloballyScopedSession
from z3c.saconfig.interfaces import IEngineCreatedEvent

# TODO: move to some better config
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

class Content(rdb.Model):
    """
    XXX not sure if polymorphic_identity is needed here
    """
    rdb.tablename('content')
    rdb.polymorphic_on('content', 'type')
    rdb.polymorphic_identity('content')
    rdb.reflected()

# interesting, PlockContainer has to come before Content or else we get the Content view.
class PlockContainer(rdb.QueryContainer):
    def _query(self):
        session = rdb.Session()
        return session.query(Content)
    
    def query(self):
        session = rdb.Session()
        return session.query(Content).filter_by(container_id=self.content_id)

    def keyfunc(self, value):
        """
        Given the value (object) return the id
        """
        return value.id
        
    def dbget(self, key):
        # we need this because we filter out only the objects in our container by query()
        return self._query().filter_by(id=key, container_id=self.content_id).first()
        
class Folder(PlockContainer, Content):
    # rdb.tableargs(useexisting=True)
    rdb.tablename('content')
    rdb.reflected()
    rdb.inherits(Content)
    # TODO, be polymorphic on more than one value? eg 'ATFolderPeer'
    rdb.polymorphic_identity('ATBTreeFolderPeer')

class Plock(grok.Application, PlockContainer):
    content_id = None
        
class ATDocument(Content):
    rdb.tablename('atdocument')
    rdb.reflected()
    rdb.inherits(Content)
    rdb.polymorphic_identity('ATDocumentPeer')

class ContentIndex(grok.View):
    grok.context(Content)
    grok.name('index')

    def render(self):
        return "My title is %s" % self.context.title

class Index(grok.View):
    grok.context(PlockContainer)
    
    def contents(self):
        return self.context.values()
