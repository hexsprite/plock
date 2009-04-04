from zope.interface import Interface, Attribute, implements

from zope.app.container.interfaces import IContainer as IContainerBase

class IContainer(IContainerBase):
    def set(value):
        """Add a new value to the container without having to specify the key.

        Lets the container figure out an appropriate key.


        Defined by SQLAlchemy dictionary-based collections.
        """

    def remove(value):
        """Remove a value from the container, by value.

        
        Defined by SQLAlchemy dictionary-based collections.
        """

class IDatabaseSetupEvent(Interface):
    metadata = Attribute("Metadata that was just set up")

class DatabaseSetupEvent(object):
    implements(IDatabaseSetupEvent)
    
    def __init__(self, metadata):
        self.metadata = metadata
