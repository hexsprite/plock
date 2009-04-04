import grok
from zope.schema.interfaces import IField
from zope.interface import Interface
from zope.interface.interface import InterfaceClass
from zope.interface.interfaces import IInterface
from zope.component import getUtility
from sqlalchemy.types import String, Integer
from megrok.rdb import Model
from zope.schema import Int
from zope.schema import Text
from zope.schema import TextLine

def Fields(model):
    return grok.Fields(schema_from_model(model))

def schema_from_model(model):
    table = model.__table__
    bases = (Interface,)
    attrs = {}
    for i, column in enumerate(table.columns):
        if len(column.foreign_keys) or column.primary_key:
            continue
        field = IField(column.type)
        field.__name__ = str(column.name)
        field.title = unicode(column.name)
        field.required = not column.nullable
        attrs[column.name] = field
        field.order = i
       
    return InterfaceClass(name=model.__table__.name,
                          bases=bases,
                          attrs=attrs,
                          __doc__='Generated from metadata')

@grok.adapter(String)
@grok.implementer(IField)
def field_from_sa_string(s):
    return TextLine(__name__ = u'__dummy__',
                title = u'__dummy__')

@grok.adapter(Integer)
@grok.implementer(IField)
def field_from_sa_integer(i):
    return Int(__name__ = u'__dummy__',
                title = u'__dummy__')

