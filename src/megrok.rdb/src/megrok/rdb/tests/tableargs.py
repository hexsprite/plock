import unittest

from megrok import rdb

import grok.testing

from sqlalchemy import Column
from sqlalchemy.types import Integer
from sqlalchemy.schema import ForeignKeyConstraint

class TableArgs(unittest.TestCase):
    def setUp(self):
        grok.testing.grok('megrok.rdb.meta')

    def test_no_tableargs(self):
        class MyClass(rdb.Model):
            rdb.metadata(rdb.MetaData())
            id = Column(Integer, primary_key=True)
            
        grok.testing.grok_component('MyClass', MyClass)
        self.assert_(not hasattr(MyClass, '__table_args__'))
    
    def test_empty_tableargs(self):
        class MyClass(rdb.Model):
            rdb.metadata(rdb.MetaData())
            id = Column(Integer, primary_key=True)
            rdb.tableargs()
    
        grok.testing.grok_component('MyClass', MyClass)
        self.assert_(not hasattr(MyClass, '__table_args__'))

    def test_non_keyword_tableargs(self):
        class MyClass(rdb.Model):
            rdb.metadata(rdb.MetaData())
            rdb.tableargs(ForeignKeyConstraint(['id'], ['whah.id']))
            id = Column(Integer, primary_key=True)
            
        grok.testing.grok_component('MyClass', MyClass)
        arg, kw = MyClass.__table_args__
        self.assert_(isinstance(arg, ForeignKeyConstraint))
        self.assertEquals({}, kw)

    def test_keyword_tableargs(self):
        class MyClass(rdb.Model):
            rdb.metadata(rdb.MetaData())
            rdb.tableargs(schema='bar')
            id = Column(Integer, primary_key=True)
            
        grok.testing.grok_component('MyClass', MyClass)
        self.assertEquals({'schema': 'bar'}, MyClass.__table_args__)

    def test_both_tableargs(self):
        class MyClass(rdb.Model):
            rdb.metadata(rdb.MetaData())
            rdb.tableargs(ForeignKeyConstraint(['id'], ['whah.id']),
                          schema='bar')
            id = Column(Integer, primary_key=True)
            
        grok.testing.grok_component('MyClass', MyClass)
        arg = MyClass.__table_args__[:-1]
        kw = MyClass.__table_args__[-1]
        self.assertEquals(1, len(arg))
        self.assert_(isinstance(arg[0], ForeignKeyConstraint))
        self.assertEquals({'schema': 'bar'}, kw)
        
def suite():
    return unittest.makeSuite(TableArgs)

