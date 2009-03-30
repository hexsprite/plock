import unittest
import doctest
from zope.testing import cleanup
from zope.testing import module
import zope.component.eventtesting
from zope import component
from megrok import rdb
    
from z3c.saconfig.interfaces import IEngineFactory, IScopedSession

from megrok.rdb.tests import tableargs

def moduleSetUp(test):
    # using zope.testing.module.setUp to work around
    # __module__ being '__builtin__' by default
    module.setUp(test, '__main__')
    
def moduleTearDown(test):
    # make sure scope func is empty before we tear down component architecture
    rdb.Session.remove()
    
    module.tearDown(test)
    cleanup.cleanUp()
    
def zopeSetUp(test):
    zope.component.eventtesting.setUp(test)

def zopeTearDown(test):
    rdb.Session.remove()
    cleanup.cleanUp()
    
def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    globs = {}
    
    suite = unittest.TestSuite()
    
    suite.addTest(doctest.DocFileSuite(
        '../README.txt',
        optionflags=optionflags,
        setUp=moduleSetUp,
        tearDown=moduleTearDown,
        globs=globs))
    suite.addTest(doctest.DocTestSuite(
        'megrok.rdb.tests.creation',
        setUp=zopeSetUp,
        tearDown=zopeTearDown,
        optionflags=optionflags))
    suite.addTest(doctest.DocTestSuite(
        'megrok.rdb.tests.reflection',
        setUp=zopeSetUp,
        tearDown=zopeTearDown,
        optionflags=optionflags))
    suite.addTest(doctest.DocTestSuite(
        'megrok.rdb.tests.location',
        setUp=zopeSetUp,
        tearDown=zopeTearDown,
        optionflags=optionflags))
    suite.addTest(doctest.DocFileSuite(
        '../schema.txt',
        optionflags=optionflags,
        ))
    suite.addTest(tableargs.suite())
    return suite
