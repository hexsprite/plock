class locatedproperty(property):
    """A property that locates whatever is returned.

    This is useful to create properties that fulfill the ILocation protocol
    and therefore have a __parent__ and a __name__. Use it like this:

    @locatedproperty
    def whatever(self):
        return Something()

    now obj.whatever will have a __parent__ set to obj and a __name__
    set to 'whatever'.

    It's quite possible we'll find a nicer spelling for this
    eventually for the purposes of megrok.rdb, but this works for now.
    """
    
    def __init__(self, f):
        super(locatedproperty, self).__init__(f)
        self.__name__ = f.__name__

    def __get__(self, obj, type=None):
        value = super(locatedproperty, self).__get__(obj, type)
        value.__parent__ = obj
        value.__name__ = self.__name__
        return value
