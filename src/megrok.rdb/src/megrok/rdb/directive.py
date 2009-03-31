from martian import MarkerDirective, Directive, CLASS, CLASS_OR_MODULE, ONCE

# XXX add proper validation logic

class key(Directive):
    scope = CLASS
    store = ONCE
    default = u''

class metadata(Directive):
    scope = CLASS_OR_MODULE
    store = ONCE
    default = None

class tablename(Directive):
    scope = CLASS
    store = ONCE
    default = u''

class mapper(Directive):
    scope = CLASS
    store = ONCE
    default = u''

class reflected(MarkerDirective):
    scope = CLASS_OR_MODULE
    store = ONCE

class tableargs(Directive):
    scope = CLASS
    store = ONCE
    default = None

    def factory(self, *args, **kw):
        if args:
            return args + (kw,)
        elif kw:
            return kw
        else:
            return None
