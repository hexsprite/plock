"""
ORM-managed objects such as collection attributes and the items in them should
have an ILocation so it is easy to generate a URL for them.

Let's first grok things::

  >>> from grok.testing import grok
  >>> grok('megrok.rdb.meta')
  >>> grok(__name__)

We need to set up an engine::

  >>> from megrok.rdb.testing import configureEngine
  >>> engine = configureEngine()
  
We now need to reflect the tables in our database to our classes::

  >>> rdb.setupDatabase(metadata)

Let's start using the database now::

  >>> session = rdb.Session()
  >>> philosophy = Department(name='Philosophy')
  >>> session.add(philosophy)

An unconnected object has ``__name__`` and ``__parent__`` of None::

  >>> print philosophy.__name__
  None
  >>> print philosophy.__parent__
  None

The ``courses`` attribute of ``philosophy`` however does have a
``__name__`` and ``__parent__``::

  >>> philosophy.courses.__name__
  u'courses'
  >>> philosophy.courses.__parent__ is philosophy
  True

Let's create some objects to put in the ``courses`` attribute of
``philosophy``:

  >>> logic = Course(name='Logic')
  >>> ethics = Course(name='Ethics')
  >>> metaphysics = Course(name='Metaphysics')
  >>> session.add_all([logic, ethics, metaphysics])

At this stage these object are also unconnected, so have ``__name__``
and ``__parent__`` of None::

  >>> print logic.__name__
  None
  >>> print logic.__parent__
  None

Let's now add them to the courses container::

  >>> philosophy.courses.set(logic)
  >>> philosophy.courses.set(ethics)
  >>> philosophy.courses.set(metaphysics)

They now should have the proper parents::

  >>> philosophy.courses['1'].__name__
  u'1'
  >>> philosophy.courses['1'].__parent__ is philosophy.courses
  True
  
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
