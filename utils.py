from UserDict import DictMixin

class attrdict(dict):
    """A dict whose items can also be accessed as member variables.

    >>> d = attrdict(a=1, b=2)
    >>> d['c'] = 3
    >>> print d.a, d.b, d.c
    1 2 3
    >>> d.b = 10
    >>> print d['b']
    10

    # but be careful, it's easy to hide methods
    >>> print d.get('c')
    3
    >>> d['get'] = 4
    >>> print d.get('a')
    Traceback (most recent call last):
    TypeError: 'int' object is not callable
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self


class EnumMetaclass(type, DictMixin):
    """ EnumMetaclass
        Lets you define an enum metaclass
        Usage:
        Enum = EnumMetaclass("Enum", (), {})
        class fields(Enum):
            APP_ID  = '__app_id__'
            USER_ID = '__user_id__'
            BUCKET  = '__bucket__'

        print Fields['OLOLO']

        for field in Fields.keys():
            print field
    """

    def __new__(mcs, classname, bases, classDict):

        enum_values = {}

        for k,v in classDict.items():
            if not k.startswith('__'):
                enum_values[k] = v

        for k in enum_values:
            del classDict[k]

        classDict['_enum_values'] = enum_values

        return type.__new__(mcs, classname, bases, classDict)


    def __iter__(self):
        for name, value in self._enum_values.items():
            yield name

    def __getitem__(self, item):
        return self._enum_values[item]

    def __getattr__(self, name):
        try:
            return self._enum_values[name]
        except KeyError:
            # Otherwise, just let the normal machinery do its job.
            return type.__getattribute__(self, name)

    def __setattr__(self, name, value):
        # Don't allow setting of EnumValue. They are immutable.
        if name in self._enum_values:
            raise AttributeError("can't set attribute")
        type.__setattr__(self, name, value)

    def keys(self):
        return self._enum_values.keys()


Enum = EnumMetaclass("Enum", (), {})
