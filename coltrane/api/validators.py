import abc
import re
from coltrane.api import exceptions

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
        if type(doc) is not dict:
            raise RuntimeError('Document [%s] is not dict type.' % doc)

        self.doc = doc
        self.forbidden_fields = forbidden_fields
        self.next_validator = next_validator

    def validate(self):
        """
        Public method for performing validation.
        Here is all logic of the delegating responsibilities to the next validator
        and raising Exception if there are any of forbidden fields in the document.
        """
        found_fields = self._forbidden_fields_from_doc(self.doc)
        if self.next_validator:
            new_fields = self.next_validator._forbidden_fields_from_doc(self.doc)
            found_fields.extend([f for f in new_fields if f not in found_fields])

        if len(found_fields):
            raise exceptions.InvalidDocumentFieldsError(
                exceptions.InvalidDocumentFieldsError.FORBIDDEN_FIELDS_MSG % ','.join(found_fields))

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
        return fields

        
class RecursiveValidator(ForbiddenFieldsValidator):
    """
    Finds all forbidden fields from top to deepest embedded.
    """
    def _forbidden_fields_from_doc(self, doc):
        found_fields = []
        for key in doc:
            if key in self.forbidden_fields:
                found_fields.append(key)
            else:
                embed_doc = doc[key]
                if type(embed_doc) is dict:
                    new_fields = self._forbidden_fields_from_doc(embed_doc)
                    found_fields.extend([f for f in new_fields if f not in found_fields])
        return found_fields


class KeyValidator(Validator):
    key_re = re.compile(r'^\w[\w-]*$')
    
    def __init__(self, data, error_class=None):
        self.error_class = exceptions.InvalidKeyNameError
        if error_class:
            self.error_class = error_class
            
        if data is not None and type(data) not in (list, tuple, dict):
            self.data = (data,)
        else:
            self.data = data

    def validate(self):
        if self.data is None:
            return
        found_keys = self._wrong_keys(self.data)
        if len(found_keys):
            raise self.error_class('Document key has invalid format [%s]' % ','.join(found_keys))

    def _wrong_keys(self, keys):
        found_keys = set()
        for k in self.data:
            if not re.match(self.key_re, k):
                found_keys.add(k)
        return found_keys


class KeyDocumentValidator(KeyValidator):

    def _wrong_keys(self, doc):
        found_keys = set()
        for k in doc:
            if not re.match(self.key_re, k):
                found_keys.add(k)
            if type(doc[k]) == dict:
                res = self._wrong_keys(doc[k])
                found_keys = found_keys.union(res)
        return found_keys

    
class KeyFilterValidator(KeyValidator):
    key_re = re.compile(r'^[\w$][\w\.-]*$')
    
    def __init__(self, filter, error_class=None):
        super(KeyFilterValidator, self).__init__(filter, error_class)


class KeyUpdateValidator(KeyValidator):
    key_re = re.compile(r'^\w[\w\.-]*$')
    
    def __init__(self, update_doc, error_class=None):
        super(KeyUpdateValidator, self).__init__(update_doc, error_class)
        
