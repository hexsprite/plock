==========
megrok.rdb
==========

The ``megrok.rdb`` package adds powerful relational database support
to Grok, based on the powerful SQLAlchemy_ library. It makes available
a new ``megrok.rdb.Model`` and ``megrok.rdb.Container`` which behave
much like ones in core Grok, but are instead backed by a relational
database.

.. _SQLAlchemy: http://www.sqlalchemy.org

XXX a hack to make things work in doctests. In some particular setup
this hack wasn't needed anymore, but I am unable at this time to
reestablish this combination of packages::

  >>> __file__ = 'foo'

In this document we will show you how to use ``megrok.rdb``.

``megrok.rdb`` uses SQLAlchemy's ORM system, in particular its
declarative extension, almost directly. ``megrok.rdb`` just supplies a
few special base classes and directives to make things easier, and a few
other conveniences that help with integration with Grok.

We first import the SQLAlchemy bits we'll need later::

  >>> from sqlalchemy import Column, ForeignKey
  >>> from sqlalchemy.types import Integer, String
  >>> from sqlalchemy.orm import relation

SQLAlchemy groups database schema information into a unit called
``MetaData``. The schema can be reflected from the database schema, or
can be created from a schema defined in Python. With ``megrok.rdb`` we
typically do the latter, from within the content classes that they are
mapped to using the ORM. We need to have some metadata to associate
our content classes with.

Let's set up the metadata object::

  >>> from megrok import rdb
  >>> metadata = rdb.MetaData()

Now we'll set up a few content classes. We'll have a very simple
structure where a (university) department has zero or more courses
associated with it. First we'll define a container that can contain
courses::

  >>> class Courses(rdb.Container):
  ...    pass

That's all. If the ``rdb.key`` directive is not used the key in the
container will be defined as the (possibly automatically assigned)
primary key in the database.

Now we can set up the ``Department`` class. This has the ``courses``
relation that links to its courses::

  >>> class Department(rdb.Model):
  ...   rdb.metadata(metadata)
  ...
  ...   id = Column('id', Integer, primary_key=True)
  ...   name = Column('name', String(50))
  ... 
  ...   courses = relation('Course', 
  ...                       backref='department',
  ...                       collection_class=Courses)

This is very similar to the way you'd use
``sqlalchemy.ext.declarative``, but there are a few differences::

* we inherit from ``rdb.Model`` to make this behave like a Grok model.

* We don't need to use ``__tablename__`` to set up the table name. By
  default the table name will be the class name, lowercased, but you
  can override this by using the ``rdb.tablename`` directive.

* we need to make explicit the metadata object that is used. We do
  this in the tests, though in Grok applications it's enough to use
  the ``rdb.metadata`` directive on a module-level to have all rdb
  classes automatically associated with that metadata object.

* we mark that the ``courses`` relation uses the ``Courses`` container
  class we have defined before. This is a normal SQLAlchemy feature,
  it's just we have to use it if we want to use Grok-style containers.

We finish up our database definition by defining the ``Course``
class::

  >>> class Course(rdb.Model):
  ...   rdb.metadata(metadata)
  ...
  ...   id = Column('id', Integer, primary_key=True)
  ...   department_id = Column('department_id', Integer, 
  ...                           ForeignKey('department.id'))
  ...   name = Column('name', String(50))

We see here that ``Course`` links back to the department it is in,
using a foreign key.

We need to actually grok these objects to have them fully set
up. Normally grok takes care of this automatically, but in this case
we'll need to do it manually.

First we grok this package's grokkers::

  >>> import grok.testing
  >>> grok.testing.grok('megrok.rdb.meta')

Now we can grok the components::

  >>> from grok.testing import grok_component
  >>> grok_component('Courses', Courses)
  True
  >>> grok_component('Department', Department)
  True
  >>> grok_component('Course', Course)
  True

Once we have our metadata and object relational map defined, we need
to have a database to actually put these in. While it is possible to
set up a different database per Grok application, here we will use a
single global database::

  >>> TEST_DSN = 'sqlite:///:memory:'
  >>> from z3c.saconfig import EngineFactory
  >>> from z3c.saconfig.interfaces import IEngineFactory
  >>> engine_factory = EngineFactory(TEST_DSN)

We need to supply the engine factory as a utility. Grok can do this
automatically for you using the module-level ``grok.global_utility``
directive, like this::

  grok.global_utility(engine_factory, provides=IEngineFactory, direct=True)

In the tests we'll use the component architecture directly::

  >>> from zope import component
  >>> component.provideUtility(engine_factory, provides=IEngineFactory)

Now that we've set up an engine, we can set up the SQLAlchemy session
utility::

  >>> from z3c.saconfig import GloballyScopedSession
  >>> from z3c.saconfig.interfaces import IScopedSession
  >>> scoped_session = GloballyScopedSession()

With Grok, we'd register it like this::

  grok.global_utility(scoped_session, provides=IScopedSession, direct=True)

But again we'll just register it directly for the tests::

  >>> component.provideUtility(scoped_session, provides=IScopedSession)

Let's make sure that as soon as the engine is created, we create the
appropriate metadata::

We now need to create the tables we defined in our database. We can do this
only when the engine is first created, so we set up a handler for it::

  >>> from z3c.saconfig.interfaces import IEngineCreatedEvent
  >>> @component.adapter(IEngineCreatedEvent)
  ... def engine_created(event):
  ...    rdb.setupDatabase(metadata)
  >>> component.provideHandler(engine_created)

Now all that is out the way, we can use the ``rdb.Session`` object to make
a connection to the database.
  
  >>> session = rdb.Session()

Let's now create a database structure. We have a department of philosophy::

  >>> philosophy = Department(name="Philosophy")

We need to manually add it to the database, as we haven't defined a
particular ``departments`` container in our database::

  >>> session.add(philosophy)

The philosophy department has a number of courses::

  >>> logic = Course(name="Logic")
  >>> ethics = Course(name="Ethics")
  >>> metaphysics = Course(name="Metaphysics")
  >>> session.add_all([logic, ethics, metaphysics])

We'll add them to the philosophy department's courses container. Since
we want to leave it up to the database what the key will be, we will
use the special ``set`` method that ``rdb.Container`` objects have to
add the objects::

  >>> philosophy.courses.set(logic)
  >>> philosophy.courses.set(ethics)
  >>> philosophy.courses.set(metaphysics)

We can now verify that the courses are there::

  >>> for key, value in sorted(philosophy.courses.items()):
  ...     print key, value.name, value.department.name
  1 Logic Philosophy
  2 Ethics Philosophy
  3 Metaphysics Philosophy

As you can see, the automatically generated primary key is also used
as the container key now.

The keys to the container are always integer, even if we're dealing with
a primary key::

  >>> philosophy.courses['1'].name
  'Logic'

  >>> philosophy.courses.get('1').name
  'Logic'

Custom key with ``rdb.key``
---------------------------

Let's now set up a different attribute to use as the container key.
We will use the ``name`` attribute of the course.

We'll set up the data model again, this time with a ``rdb.key`` on the
``Courses`` class::

  >>> metadata = rdb.MetaData()

  >>> class Courses(rdb.Container):
  ...    rdb.key('name')

  >>> class Department(rdb.Model):
  ...   rdb.metadata(metadata)
  ...
  ...   id = Column('id', Integer, primary_key=True)
  ...   name = Column('name', String(50))
  ... 
  ...   courses = relation('Course', 
  ...                       backref='department',
  ...                       collection_class=Courses)

  >>> class Course(rdb.Model):
  ...   rdb.metadata(metadata)
  ...
  ...   id = Column('id', Integer, primary_key=True)
  ...   department_id = Column('department_id', Integer, 
  ...                           ForeignKey('department.id'))
  ...   name = Column('name', String(50))

We grok these new classes::

  >>> grok_component('Courses', Courses)
  True
  >>> grok_component('Department', Department)
  True
  >>> grok_component('Course', Course)
  True

We don't need to change the engine, as the underlying relational
database has remained the same. Let's set up another faculty with some
departments::

  >>> physics = Department(name="Physics")
  >>> session.add(physics)
  >>> quantum = Course(name="Quantum Mechanics")
  >>> relativity = Course(name="Relativity")
  >>> high_energy = Course(name="High Energy")
  >>> session.add_all([quantum, relativity, high_energy])

We'll now add these departments to the physics faculty::

  >>> physics.courses.set(quantum)
  >>> physics.courses.set(relativity)
  >>> physics.courses.set(high_energy)

We can now verify that the courses are there, with the names as the keys::

  >>> for key, value in sorted(physics.courses.items()):
  ...     print key, value.name, value.department.name
  High Energy High Energy Physics
  Quantum Mechanics Quantum Mechanics Physics
  Relativity Relativity Physics

Custom query container
----------------------

Sometimes we want to expose objects as a (read-only) container based
on a query, not a relation. This is useful when constructing an
application and you need a "starting point", a root object that
launches into SQLAlchemy-mapped object that itself is not directly
managed by SQLAlchemy.

We can construct such a special container by subclassing from ``rdb.QueryContainer`` and implementing
the special ``query`` method::

  >>> class MyQueryContainer(rdb.QueryContainer):
  ...   def query(self):
  ...      return session.query(Department)
  >>> qc = MyQueryContainer()

Let's try some common read-only container operations, such as
``__getitem__``1::

  >>> qc['1'].name
  u'Philosophy'
  >>> qc['2'].name
  'Physics'

XXX Why the unicode difference between u'Philosophy' and 'Physics'?

``__getitem__`` with a ``KeyError``::

  >>> qc['3']
  Traceback (most recent call last):
    ...
  KeyError: '3'

``get``::

  >>> qc.get('1').name
  u'Philosophy'
  >>> qc.get('3') is None
  True
  >>> qc.get('3', 'foo')
  'foo'

``__contains__``::

  >>> '1' in qc
  True
  >>> '3' in qc
  False

``has_key``::

  >>> qc.has_key('1')
  True
  >>> qc.has_key('3')
  False

``len``::

  >>> len(qc)
  2

``values``::

  >>> sorted([v.name for v in qc.values()])
  [u'Philosophy', 'Physics']

The parents of all the values are the query container::

  >>> [v.__parent__ is qc for v in qc.values()]
  [True, True]
  >>> sorted([v.__name__ for v in qc.values()])
  [u'1', u'2']

``keys``::

  >>> sorted([key for key in qc.keys()])
  [u'1', u'2']

``items``::

  >>> sorted([(key, value.name) for (key, value) in qc.items()])
  [(u'1', u'Philosophy'), (u'2', 'Physics')]

  >>> [value.__parent__ is qc for (key, value) in qc.items()]
  [True, True]
  >>> sorted([value.__name__ for (key, value) in qc.items()])
  [u'1', u'2']

``__iter__``::
  
  >>> result = []
  >>> for key in qc:
  ...   result.append(key)
  >>> sorted(result)
  [u'1', u'2']

Converting results of QueryContainer
------------------------------------

Sometimes it's useful to convert (or modify) the output of the query
to something else before they appear in the container. You can implement
the ``convert`` method to do so. It takes the individual value resulting
from the value and should return the converted value::

  >>> class ConvertingQueryContainer(rdb.QueryContainer):
  ...   def query(self):
  ...      return session.query(Department)
  ...   def convert(self, value):
  ...      return SpecialDepartment(value.id)

  >>> class SpecialDepartment(object):
  ...    def __init__(self, id):
  ...      self.id = id

  >>> qc = ConvertingQueryContainer()

Let's now check that all values are ``SpecialDepartment``::

  >>> isinstance(qc['1'], SpecialDepartment)
  True
  >>> isinstance(qc['2'], SpecialDepartment)
  True

KeyError still works::

  >>> qc['3']
  Traceback (most recent call last):
    ...
  KeyError: '3'

``get``::

  >>> isinstance(qc.get('1'), SpecialDepartment)
  True
  >>> qc.get('3') is None
  True
  >>> qc.get('3', 'foo')
  'foo'

``values``::

  >>> [isinstance(v, SpecialDepartment) for v in qc.values()]
  [True, True]

The parents of all the values are the query container::

  >>> [v.__parent__ is qc for v in qc.values()]
  [True, True]
  >>> sorted([v.__name__ for v in qc.values()])
  [u'1', u'2']

``items``::

  >>> sorted([(key, isinstance(value, SpecialDepartment)) for (key, value) in qc.items()])
  [(u'1', True), (u'2', True)]

  >>> [value.__parent__ is qc for (key, value) in qc.items()]
  [True, True]
  >>> sorted([value.__name__ for (key, value) in qc.items()])
  [u'1', u'2']
 
Customizing QueryContainer further
----------------------------------

Sometimes it's useful to define a custom keyfunc and custom method to
retrieve the key from the database - these usually are implemented
together::

  >>> class KeyfuncQueryContainer(rdb.QueryContainer):
  ...   def query(self):
  ...      return session.query(Department)
  ...   def keyfunc(self, value):
  ...      return 'd' + unicode(value.id)
  ...   def dbget(self, key):
  ...      if not key.startswith('d'):
  ...          return None
  ...      return self.query().get(key[1:])

  >>> qc = KeyfuncQueryContainer()
  >>> qc.keys()
  [u'd1', u'd2']
  >>> qc[u'd1'].id
  1

