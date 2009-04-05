import unittest

import grok.testing

from megrok import rdb

metadata = rdb.MetaData()
rdb.metadata(metadata)

class Polymorphic(unittest.TestCase):
    def setUp(self):
        grok.testing.grok('megrok.rdb.meta')
        from megrok.rdb.testing import configureEngine
        engine = configureEngine()

        from sqlalchemy.sql import text
        conn = engine.connect()
        s = text('''
            create table content (
                id integer,
                type char(50),
                primary key (id))
        ''')
        result = conn.execute(s)
        s = text('''
           create table person (
             id integer,
             name char(50),
             FOREIGN KEY(id) REFERENCES content (id)
             )
        ''')
        result = conn.execute(s)
        x = conn.execute
        x('INSERT INTO content VALUES (1, "person")')
        x('INSERT INTO person VALUES (1, "Bob")')
        x('INSERT INTO content VALUES (2, "content")')

    def test_polymorphic_reflection(self):
        """
        Could test basic attributes being set but this integration test
        ensures it continues to work with SQLAlchemy.
        """

        class Content(rdb.Model):
            rdb.reflected()
            rdb.polymorphic_on(table='content', column='type')
            rdb.polymorphic_identity('content')

        class Person(Content):
            rdb.tablename('person')
            rdb.reflected()
            rdb.inherits(Content)
            rdb.polymorphic_identity('person')

        grok.testing.grok_component('Content', Content)
        grok.testing.grok_component('Person', Person)

        # this has to be called after classes are grokked
        rdb.setupDatabase(metadata)
        session = rdb.Session()
        
        results = session.query(Content).all()

        assert results
        assert isinstance(results[0], Person)
        # a Person has a name
        assert results[0].name == 'Bob'
        
        assert isinstance(results[1], Content)
        # Content does not have a name
        assert not hasattr(results[1], 'name')
        
    def test_polymorphic_declarative(self):
        """
        Test that non-reflected works
        """
        assert "I am broken!"

def suite():
    return unittest.makeSuite(Polymorphic)

