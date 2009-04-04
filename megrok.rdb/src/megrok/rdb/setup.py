from zope import component
from zope.event import notify

from sqlalchemy.orm import mapper
from sqlalchemy.ext.declarative import instrument_declarative
from sqlalchemy.schema import Table

from z3c.saconfig.interfaces import IEngineFactory
from megrok.rdb.interfaces import DatabaseSetupEvent

def setupDatabase(metadata):
    """Set up of ORM for engine in current site.

    This will:

    * reflect any reflected tables that need to be reflected from the database
      into classes.

    * create any tables in the database that haven't been yet reflected.    
    """
    reflectTables(metadata)
    createTables(metadata)
    notify(DatabaseSetupEvent(metadata))
    
def reflectTables(metadata):
    """Reflect tables into ORM.
    """
    if getattr(metadata, '_reflected_completed', False):
        # XXX thread safety?
        return
    if not getattr(metadata, '_reflected_registry', {}):
        # nothing to reflect
        return
    # first reflect database-defined schemas into metadata
    engine = Engine()
    for class_ in metadata._reflected_registry.keys():
        _reflectTableForClass(class_, metadata, engine)
    # reflect any remaining tables. This will not reload tables already loaded
    # (XXX is this necessary?)
    metadata.reflect(bind=engine)
    if not hasattr(metadata, '_decl_registry'):
        metadata._decl_registry = {}

    for class_ in sorted(metadata._reflected_registry.keys(), key=lambda a: getattr(a, '__polymorphic_inherits__', 0)):
    # for class_ in metadata._reflected_registry.keys():
        # __polymorphic_on__ = ('content', 'portal_type')
        # __polymorphic_identify__ = 'content'
        mapper_args = getattr(class_, '__mapper_args__', {})
        if hasattr(class_, '__polymorphic_on__'):
            tablename, column = class_.__polymorphic_on__
            mapper_args['polymorphic_on'] = getattr(metadata.tables[tablename].c, column)
        if hasattr(class_, '__polymorphic_identity__'):
            mapper_args['polymorphic_identity'] = class_.__polymorphic_identity__
        if hasattr(class_, '__polymorphic_inherits__'):
            mapper_args['inherits'] = class_.__polymorphic_inherits__

        if mapper_args:
            class_.__mapper_args__ = mapper_args

        import sys
        print >>sys.stderr, class_, repr(mapper_args)

        instrument_declarative(class_, metadata._decl_registry, metadata)

    # XXX thread safety?
    metadata._reflected_completed = True

def _reflectTableForClass(class_, metadata, bind):
    """Reflect an individual table defined for a class.

    This supports the special 'schema' indicator in '__table_args__',
    allowing reflection of tables not in the default schema.
    metadata.reflect() doesn't allow this in declarative mode.
    """
    reflect_opts = {'autoload': True}
    reflect_opts['autoload_with'] = bind
    conn = bind.contextual_connect()

    table_args = getattr(class_, '__table_args__', {})
    if type(table_args) is tuple:
        table_args = table_args[-1]
        if type(table_args) is not dict:
            table_args = {}
    schema = table_args.get('schema', None)
    if schema is not None:
        reflect_opts['schema'] = schema

    Table(class_.__tablename__, metadata, **reflect_opts)
        
def createTables(metadata):
    """Create class-specified tables.
    """
    engine = Engine()
    metadata.create_all(engine)

def Engine():
    """Get the engine in the current session.
    """
    engine_factory = component.getUtility(IEngineFactory)
    return engine_factory()
