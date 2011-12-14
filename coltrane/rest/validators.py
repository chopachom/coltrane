import abc
import re
from coltrane.rest import exceptions

__author__ = 'Pasha'

class Validator(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def validate(self):
        raise NotImplementedError("This function must be performed in subclasses")
    

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
            found_new = validator._forbidden_fields_from_doc(validator.doc)
            found_fields = found_fields.union(found_new)
            validator = validator.next_validator

        if len(found_fields):
            raise exceptions.InvalidDocumentFieldsError(
                exceptions.InvalidDocumentFieldsError.FORBIDDEN_FIELDS_MSG %
                ','.join(found_fields))

        
    @abc.abstractmethod
    def _forbidden_fields_from_doc(self, doc=None):
        """
        Developer should invoke this method in subclasses.
        """
        raise NotImplementedError("This function must be performed in subclasses")


class SimpleValidator(ForbiddenFieldsValidator):
    """
    Finds forbidden fields only in top level of document.
    """
    def _forbidden_fields_from_doc(self, doc):
        fields = [key for key in doc if key in self.forbidden_fields]
        return set(fields)

        
class RecursiveValidator(ForbiddenFieldsValidator):
    """
    Finds all forbidden fields from top to deepest embedded.
    """
    def _forbidden_fields_from_doc(self, doc):
        found_fields = set()
        for key in doc:
            if key in self.forbidden_fields:
                found_fields.add(key)
            else:
                embed_doc = doc[key]
                if type(embed_doc) is dict:
                    new_fields = self._forbidden_fields_from_doc(embed_doc)
                    found_fields = found_fields.union(new_fields)
        return found_fields


class KeyValidator(object):
    """
        Base validator for _key value and for all keys names.
        Values of <v> in sample {'_key': <v>, <v>:10, <v>: {<v>:5}}
        are validated for correct value.
    """
#    key_re = re.compile(r'^\w[\w-]*$')
    key_re = re.compile(r'^(?!__)\w[\w-]*(?<!__)$')

    def __init__(self, data):
        self.data = data

    def validate(self, recursive=False):
        if self.data is None:
            return
        if recursive:
            found_keys = self._wrong_keys_recursively(self.data)
        else:
            found_keys = self._wrong_keys(self.data)
        if len(found_keys):
            raise exceptions.InvalidKeyNameError(
                'Document key has invalid format [%s]' % ','.join(found_keys))

    def _wrong_keys(self, keys):
        found_keys = set()
        for k in keys:
            if not re.match(self.key_re, k):
                found_keys.add(k)
        return found_keys

    def _wrong_keys_recursively(self, doc):
        found_keys = set()
        for k in doc:
            if not re.match(self.key_re, k):
                found_keys.add(k)
            if type(doc[k]) == dict:
                res = self._wrong_keys_recursively(doc[k])
                found_keys = found_keys.union(res)
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
    key_re = re.compile(r'^(?!__)\w[\w\.-]*(?<!__)$')

    def __init__(self, update_doc):
        super(UpdateDocumentKeysValidator, self).__init__(update_doc)

    def validate(self, recursive=True):
        super(UpdateDocumentKeysValidator, self).validate(recursive)
        
