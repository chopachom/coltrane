import abc
import re
from coltrane.rest import exceptions

__author__ = 'Pasha'

class Validator(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def validate(self, **kwargs):
        raise NotImplementedError("This function must be performed in subclasses")

    @abc.abstractmethod
    def _wrong_data(self, doc=None):
        """
        Returns invalid data (fields or values) of document.
        Developer should invoke this method in subclasses.
        """
        raise NotImplementedError("This function must be performed in subclasses")


    def _from_list(self, l):
        """
            It is used for processing list object type.
            Passed object must be list type only.
            This method should be invoked in subclasses.
        """
        found_fields = set()
        for v in l:
            if type(v) == list:
                new_fields = self._from_list(v)
            elif type(v) == dict:
                new_fields = self._wrong_data(v)
            else:
                continue
            if new_fields:
                found_fields = found_fields.union(new_fields)
        return found_fields
    

class ForbiddenFieldsValidator(Validator):
    """
    Base class for validators.
    Validators are used to verify document structure, they should rise errors
    if any of forbidden fields were found in document
    Validators are used in chain (implementation of pattern Chain of Responsibilities).
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, doc, forbidden_fields, next_validator=None):
        """
        Base constructor for validators.
        Parameters:
        doc - document for validation
        forbidden_fields - fields validation is going on
        next_validator - (object of any subclass of Validator).
            The next validator in the chain after current validator.
        """

        self.doc = doc
        self.forbidden_fields = forbidden_fields
        self.next_validator = next_validator

    def validate(self):
        """
        Public method for performing validation.
        Here is all logic of the delegating responsibilities to the next validator
        and raising Exception if there are any of forbidden fields in the document.
        """
        found_fields = set()
        validator = self
        while validator:
            found_new = validator._wrong_data(validator.doc)
            found_fields = found_fields.union(found_new)
            validator = validator.next_validator

        if len(found_fields):
            raise exceptions.InvalidDocumentFieldsError(
                exceptions.InvalidDocumentFieldsError.FORBIDDEN_FIELDS_MSG %
                ','.join(found_fields))


class SimpleValidator(ForbiddenFieldsValidator):
    """
    Finds forbidden fields only in top level of document.
    """
    def _wrong_data(self, doc):
        fields = [key for key in doc if key in self.forbidden_fields]
        return set(fields)

        
class RecursiveValidator(ForbiddenFieldsValidator):
    """
    Finds all forbidden fields from top to deepest embedded.
    """
    def _wrong_data(self, doc):
        found_fields = set()
        for key in doc:
            if key in self.forbidden_fields:
                found_fields.add(key)
            embed_doc = doc[key]
            if type(embed_doc) is dict:
                new_fields = self._wrong_data(embed_doc)
            elif type(embed_doc) is list:
                new_fields = self._from_list(embed_doc)
            else:
                continue
            if new_fields:
                found_fields = found_fields.union(new_fields)
        return found_fields


class KeyValidator(Validator):
    """
        Base validator for _key value and for all keys names.
        Values of <v> in sample {'_key': <v>, <v>:10, <v>: {<v>:5}}
        are validated for correct value.
    """
    #Allowed: _a-bc_
    # Forbidden: __a, b__, -c, d.e
    key_re = re.compile(r'^(?!__)\w[\w-]*(?<!__)$')

    def __init__(self, data):
        self.data = data

    def validate(self, recursive=False):
        if self.data is None:
            return
        if recursive:
            found_keys = self._wrong_data(self.data)
        else:
            found_keys = self._wrong_data_simple(self.data)
        if len(found_keys):
            raise exceptions.InvalidKeyNameError(
                'Document key has invalid format [%s]' % ','.join(found_keys))


    def _wrong_data(self, doc):
        """
            Finds all invalid keys.
            Keys are checked by regexp recursively.
        """
        found_keys = set()
        for k in doc:
            if not re.match(self.key_re, k):
                found_keys.add(k)
            v = doc[k]
            if type(v) == dict:
                found = self._wrong_data(v)
            elif type(v) == list:
                found = self._from_list(v)
            else:
                continue
            if found:
                found_keys = found_keys.union(found)
        return found_keys


    def _wrong_data_simple(self, keys):
        """
            Finds all invalid keys.
            Top level keys only are checked by regexp.
        """
        found_keys = set()
        for k in keys:
            if not re.match(self.key_re, k):
                found_keys.add(k)
        return found_keys


class SaveDocumentKeysValidator(KeyValidator):
    """
        Validator for document to save.
        Allows only 0-9,a-z,A-Z,_
    """
    def __init__(self, doc):
        super(SaveDocumentKeysValidator, self).__init__(doc)

    def validate(self, recursive=True):
        super(SaveDocumentKeysValidator, self).validate(recursive)


class FilterKeysValidator(KeyValidator):
    """
        Validator for filter object.
        It allows symbols '$','.' because of filter syntax:
            filter = {'a.b.c':10, '$and':[{'b':{'$gt': 5}}, {'c':10}]}
    """
    #Allowed: _a-b.$c_
    # Forbidden: __a, b__, -c
    key_re = re.compile(r'^(?!__)[\w$][\w\.-]*(?<!__)$')
    
    def __init__(self, filter):
        super(FilterKeysValidator, self).__init__(filter)

    def validate(self, recursive=True):
        super(FilterKeysValidator, self).validate(recursive)


class UpdateDocumentKeysValidator(KeyValidator):
    """
        Document validator to update underlying document.
        It allows symbol '.' because of search mongo syntax:
            doc = {'a.b.c':10}
            It will replace <obj> in
            {'a':{'b':{'c':<obj>}}} by 10
    """
    #Allowed: _a-b.c_
    # Forbidden: __a, b__, -c
    key_re = re.compile(r'^(?!__)\w[\w\.-]*(?<!__)$')

    def __init__(self, update_doc):
        super(UpdateDocumentKeysValidator, self).__init__(update_doc)

    def validate(self, recursive=True):
        super(UpdateDocumentKeysValidator, self).validate(recursive)
        
