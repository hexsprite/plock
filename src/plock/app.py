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

class Content(rdb.Model):
    rdb.polymorphic_on('content', 'type')
    __polymorphic_identity__ = 'content'
    rdb.reflected()

# interesting, PlockContainer has to come before Content or else we get the Content view.
class Folder(PlockContainer, Content):
    __table_args__ = dict(useexisting=True) #rdb.tableargs(useexisting=True)
    rdb.tablename('content')
    rdb.reflected()
    __polymorphic_inherits__ = Content  #rdb.inherits(Content)
    # TODO, be polymorphic on more than one value?
    __polymorphic_identity__ = u'ATBTreeFolderPeer' #rdb.identity()

class Plock(grok.Application, PlockContainer):
    def __init__(self, *args, **kwargs):
        super(Plock, self).__init__(*args, **kwargs)
        self.content_id = None
        
    # def query(self):
    #     return self._query().filter_by(container_id=None)
    #     
    # def dbget(self, key):
    #     # we need this because we filter out only the objects in our container by query()
    #     return self._query().filter_by(id=key, container_id=None).first()

class ATDocument(Content):
    rdb.tablename('atdocument')
    rdb.reflected()
    __polymorphic_inherits__ = Content  #rdb.inherits(Content)
    __polymorphic_identity__ = 'ATDocumentPeer'

class ContentIndex(grok.View):
    grok.context(Content)
    grok.name('index')

    def render(self):
        return "My title is %s" % self.context.title

class Index(grok.View):
    grok.context(PlockContainer)
    
    def contents(self):
        return self.context.values()
