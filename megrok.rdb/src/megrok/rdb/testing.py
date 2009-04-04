from zope import component

from z3c.saconfig import EngineFactory
from z3c.saconfig.interfaces import IEngineFactory

from z3c.saconfig import GloballyScopedSession
from z3c.saconfig.interfaces import IScopedSession

def configureEngine(TEST_DSN='sqlite:///:memory:'):
    """Utility function for tests to set up an in-memory test database.

    Returns engine object.
    """
    engine_factory = EngineFactory(TEST_DSN)
    component.provideUtility(engine_factory, provides=IEngineFactory)

    scoped_session = GloballyScopedSession()
    component.provideUtility(scoped_session, provides=IScopedSession)
    
    return engine_factory()

