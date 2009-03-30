"""
A model by default also defines a relationa l database table in Python
(as opposed to reflecting it from the database schema).

Let's first grok things::

  >>> from grok.testing import grok
  >>> grok('megrok.rdb.meta')
  >>> grok(__name__)

We need to set up an engine::

  >>> from megrok.rdb.testing import configureEngine
  >>> engine = configureEngine()

When the database is set up there is an ``rdb.IDatabaseSetupEvent``
that can be hooked into to do some extra configuration. The event is
fired after all other database is completed. Here we just print
something so we can test whether it was fired correctly::

  >>> from zope import component
  >>> @component.adapter(rdb.IDatabaseSetupEvent)
  ... def setupHandler(event):
  ...    print 'Database setup event'
  >>> component.provideHandler(setupHandler)
  
We now need to create the tables we defined in our database::

  >>> rdb.setupDatabase(metadata)
  Database setup event

As we can see the database setup event was indeed fired.

Let's start using the database now::

  >>> session = rdb.Session()
  >>> philosophy = Department(name='Philosophy')
  >>> session.add(philosophy)
  >>> logic = Course(name='Logic')
  >>> ethics = Course(name='Ethics')
  >>> metaphysics = Course(name='Metaphysics')
  >>> session.add_all([logic, ethics, metaphysics])
  
Let's now add them to the courses container::

  >>> philosophy.courses.set(logic)
  >>> philosophy.courses.set(ethics)
  >>> philosophy.courses.set(metaphysics)

We can now verify that the courses are there::

  >>> [(course.id, course.name, course.department_id) for course in
  ... session.query(Course)]
  [(1, 'Logic', 1), (2, 'Ethics', 1), (3, 'Metaphysics', 1)]

  >>> for key, value in sorted(philosophy.courses.items()):
  ...   print key, value.name, value.department.name
  1 Logic Philosophy
  2 Ethics Philosophy
  3 Metaphysics Philosophy
"""


import grok
from megrok import rdb

from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import relation

metadata = rdb.MetaData()

rdb.metadata(metadata)

class Courses(rdb.Container):
    pass

class Department(rdb.Model):
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(50))
    courses = relation('Course', 
                       backref='department',
                       collection_class=Courses)

class Course(rdb.Model):
    id = Column('id', Integer, primary_key=True)
    department_id = Column('department_id', Integer, 
                           ForeignKey('department.id'))
    name = Column('name', String(50))

