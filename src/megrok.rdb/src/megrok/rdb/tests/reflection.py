"""
A reflected model is a model that is defined by the table in the
database (as opposed to defining the database table in Python).

Let's first grok things::

  >>> from grok.testing import grok
  >>> grok('megrok.rdb.meta')
  >>> grok(__name__)

We need to set up an engine::

  >>> from megrok.rdb.testing import configureEngine
  >>> engine = configureEngine()

Let's set up the tables::

  >>> from sqlalchemy.sql import text
  >>> conn = engine.connect()
  >>> s = text('''
  ...   create table department (
  ...     id integer,
  ...     name char(50),
  ...     primary key (id))
  ... ''')
  >>> result = conn.execute(s)
  >>> s = text('''
  ...   create table course (
  ...     id integer,
  ...     name char(50),
  ...     department_id integer,
  ...     primary key (id),
  ...     foreign key (department_id) references department(id))
  ... ''')
  >>> result = conn.execute(s)
  
We now need to reflect the tables in our database to our classes::

  >>> rdb.setupDatabase(metadata)

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
    rdb.reflected()
    courses = relation('Course', 
                       backref='department',
                       collection_class=Courses)

class Course(rdb.Model):
    rdb.reflected()
