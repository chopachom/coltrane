from UserDict import DictMixin

def traverse(dct, f):
    def traverse_list(lst, f):
        new = []
        for obj in lst:
            res = f(None, obj)
            if res:
                obj = res[1]
            elif isinstance(obj, dict):
                obj = traverse_dict(obj, f)
            elif isinstance(obj, list):
                obj = traverse_list(obj, f)
            new.append(obj)
        return new

    def traverse_dict(dct, f):

        new = {}
        for key, value in dct.items():
            res = f(key, value)
            if res:
                new[res[0]] = res[1]
            elif isinstance(value, dict):
                new[key] = traverse_dict(value, f)
            elif isinstance(value, list):
                new[key] = traverse_list(value, f)
            else:
                new[key] = value
        return new
    return traverse_dict(dct, f)


class EnumMetaclass(type, DictMixin):
    """ EnumMetaclass
        Lets you define an enum metaclass

        Classes that use Enum class behaves like dict allowing to iterate
        though keys

        Usage:
        Enum = EnumMetaclass("Enum", (), {})
        >>> class fields(Enum):
        ... APP_ID  = '__app_id__'
        ... USER_ID = '__user_id__'
        ... BUCKET  = '__bucket__'

        >>> print fields['APP_ID']

        >>> for field in fields.keys():
        ... print field
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

    def __add__(self, obj):
        return self.values() + obj.values()


Enum = EnumMetaclass("Enum", (), {})
