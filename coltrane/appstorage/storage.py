# -*- coding: utf-8 -*-
"""
    :Authors: - qweqwe
              - pasha
              - dreambrother
"""

import re
from datetime import datetime
from uuid import uuid4
from functools import wraps
from hashlib import sha1

from coltrane.appstorage.exceptions import *
from coltrane.utils import Enum



class intf(Enum):
    ID          = '_id'
    APP_ID      = '__app_id__'
    USER_ID     = '__user_id__'
    BUCKET      = '__bucket__'
    HASHID      = '__hashid__'
    DELETED     = '__deleted__'
    CREATED_AT  = '__created_at__'
    UPDATED_AT  = '__updated_at__'
    IP_ADDRESS  = '__ip_address__'


class extf(Enum):
    KEY         = '_key'
    BUCKET      = '_bucket'
    CREATED_AT  = '_created'


# internal constants
DICT_TYPE = type(dict())
DOCUMENT_ID_FORMAT = '{app_id}|{user_id}|{bucket}|{deleted}|{document_key}'


def verify_tokens(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        app_id = args[1]
        user_id = args[2]
        if app_id is None:
            raise InvalidAppIdError('app_id must be not null')
        if user_id is None:
            raise InvalidUserIdError('user_id must be not null')
        return f(*args, **kwargs)
    return wrapper


class AppdataStorage(object):

    def __init__(self, entities):
        """
            :param entities: MongoDB collection object
        """
        self.entities = entities

    @verify_tokens
    def create(self, app_id, user_id, bucket, ip_address, document):
        """ Create operation for CRUD.
         Saves entity to db in this format:
         {
             app_id: $app_id,
             user_id: $user_id,
             bucket: $bucket,
             _id: $id
             $document
         }
         $document saves in root of document.
         Function creations new id and set it to _id field, when _id is not filled in user document.
         If user document's _id already exists, InvalidDocumentIdError will be raised.
         Parameters:
         app_id: String, application id
         user_id: String, user id
         document: Dict, user document
         bucket: String, document type (bucket)

         Returns key of inserted entity """

        # validations
        if document is None:
            raise InvalidDocumentError('Document must be not null')
        if type(document) is not DICT_TYPE:
            raise InvalidDocumentError('Document must be instance of dict type')


        # check if a key is already exists, if it isn't - generate new
        if extf.KEY in document:
            document_id = _internal_id(app_id, user_id, bucket, 0,
                                       document[extf.KEY])
        else:
            document_id = _internal_id(app_id, user_id, bucket, 0, uuid4())

        document = _from_external_to_internal(app_id, user_id, bucket,
            _filter_int_fields(_filter_ext_fields(document))
        )
        # add required fields to document
        document[intf.ID] = document_id
        document[intf.APP_ID] = app_id
        document[intf.USER_ID] = user_id
        document[intf.BUCKET] = bucket
        # adding str(False) to hashid means that document isn't deleted
        document[intf.HASHID] = sha1(app_id+user_id+bucket+str(False)).hexdigest()
        document[intf.CREATED_AT] = datetime.utcnow()
        document[intf.IP_ADDRESS] = ip_address
        document[intf.DELETED] = False

        self.entities.insert(document)

        return _external_key(document[intf.ID])


    @verify_tokens
    def get(self, app_id, user_id, bucket, key):
        """ Read operation for CRUD service.
         Parameters:
         app_id: String, application id
         user_id: String, user id
         document_key: String, document key
         bucket: String, type of document

         Returns founded document or None if object not found """

        # validations
        if key is None:
            raise InvalidDocumentKeyError('Document key must be not null')

        # logic

        document_id = _internal_id(app_id, user_id, bucket, 0, key)
        res = self.entities.find_one({intf.ID: document_id, intf.DELETED: False})
        if res is None:
            return None

        return _to_external(res)


    @verify_tokens
    def find(self, app_id, user_id, bucket, filter_opts=None,
             skip=0, limit=1000):

        criteria = _generate_criteria(app_id, user_id, bucket, filter_opts=filter_opts)

        opt_criteria = {}
        if skip < 0:
            raise RuntimeError("offset parameter must not be less then 0")
        if limit <= 0:
            raise RuntimeError("limit parameter must be greater then 0")
        opt_criteria['skip']  = skip
        opt_criteria['limit'] = limit

        documents = list(self.entities.find(criteria, **opt_criteria))
        return map(_to_external, documents)


    @verify_tokens
    def update(self, app_id, user_id, bucket, ip_address, document,
                key=None, filter_opts=None):
        """ Update operation for CRUD.
            Parameters:
            app_id: String, application id
            user_id: String, user id
            document: Dict, document with given _id will be updated in db
            bucket: String, document type """

        # validations
        if document is None:
            raise InvalidDocumentError('Document for update cannot be null')
        if type(document) is not DICT_TYPE:
            raise InvalidDocumentError('Document must be instance of dict type')

        document =  _from_external_to_internal(app_id, user_id, bucket, document)

        if key:
            criteria = _generate_criteria(app_id, user_id, bucket,
                                          filter_opts={extf.KEY: key})
        else:
            criteria = _generate_criteria(app_id, user_id, bucket,
                                          filter_opts=filter_opts)

        document[intf.IP_ADDRESS] = ip_address
        document[intf.UPDATED_AT] = datetime.utcnow()
        self.entities.update(criteria, {'$set': document}, multi=True, safe=True)


    @verify_tokens
    def delete(self, app_id, user_id, bucket, ip_address,
               key=None, filter_opts=None):
        if key:
            criteria = _generate_criteria(app_id, user_id, bucket,
                                          filter_opts={extf.KEY: key})
        else:
            criteria = _generate_criteria(app_id, user_id, bucket,
                                          filter_opts=filter_opts)
        self.entities.update(criteria, {
            '$set': {
                intf.HASHID: sha1(app_id+user_id+bucket+str(True)).hexdigest(),
                intf.DELETED:True,
                intf.IP_ADDRESS:ip_address,
                intf.UPDATED_AT:datetime.utcnow()
            }
        }, multi=True)


    #TODO: REFUCK this FUNC
    def is_document_exists(self, app_id, user_id, bucket, criteria=None):
        """ Function for the external performing
        """
        if criteria and extf.KEY in criteria:
            doc_id = _internal_id(app_id, user_id, bucket, 0, criteria[extf.KEY])
            if len(criteria) == 1:
                return self._is_document_exists({intf.ID: doc_id})
            kwargs = dict(document_id=doc_id)
        else:
            kwargs = dict(filter_opts=criteria)
        res_criteria = _generate_criteria(app_id, user_id, bucket,**kwargs)
        return self._is_document_exists(res_criteria)


    def _is_document_exists(self, criteria):
         """ Function for the internal performing
             This function checks whether db contains document with specified id.
                Parameters:
                document_id: String, document id.
                Returns: True if document is exists with specified id and False if not."""

         if not criteria:
             raise RuntimeError('Criteria object must not be None')

         # query document with one field (_id) to decrease network traffic. It is necessary fields minimum.
         found =  self.entities.find_one(criteria,  fields=['_id'])
         if found:
             return True
         else:
             return False


# Utility functions below

def _internal_id(app_id, user_id, bucket, deleted, document_key):
     return DOCUMENT_ID_FORMAT.format(app_id=app_id, user_id=user_id,
                                      bucket=bucket, deleted=deleted,
                                      document_key=document_key)


def _external_key(internal_id):
    """
        Returns external _key by given internal id
        example: applolo|usrlolo|ololo|flafffnl|asdf|asd| -> flaflaffnl|asdf|asd|
    """
    return '|'.join(substr for substr in internal_id.split('|')[4:])


def _filter_int_fields(document):
    """
    Filter out all internal fields
    """
    return {k: v for k, v in document.items()
             if not k in intf.values()}


def _filter_ext_fields(document):
    """
    Filter out all external fields
    """
    return {k: v for k, v in document.items()
             if not k in extf.values()}

def _to_external(document):
    if not document:
        return None

    external = _filter_int_fields(document)
    external[extf.KEY] = _external_key(document[intf.ID])
    external[extf.BUCKET]      = document[intf.BUCKET]
    external[extf.CREATED_AT]  = document[intf.CREATED_AT]

    return external

def _to_internal(document):
    """
        Given a external document returns its internal representaions
        This function adds internal fields if corresponding external fields
        isn't present in document, i.e. it adds __created__ with new datetime
        only if _created is not present in document
    """
    # we may need to create this func in next updates


def _from_external_to_internal(app_id, user_id, bucket, doc):
    """
    Convert document from external view to the internal.
    If document contains external fields, convert its values to the internal fields.
    {<ext_1>:[{<ext_2>:10}, {'key':20}]} => {<int_1>:[{<int_2>:10}, {'key':20}]}
    """
    def _from_dict(doc):
        """
            Gets document as a parameter of dict type.
            Runs through top level keys. If object by key is dict
            type then invokes _from_doc recursively. If object by
            key is list then invokes _from_list.
        """
        internal = {}
        for key in doc:
            val = doc[key]
            if key in extf.values():
                if key == extf.BUCKET:
                    internal[intf.BUCKET] = val
                elif key == extf.CREATED_AT:
                    if isinstance(val, basestring):
                        val = try_convert_to_date(val)
                    elif type(val) == dict:
                        val = _from_dict(val)
                    internal[intf.CREATED_AT] = val
                elif key == extf.KEY:
                    document_key = val
                    document_id = _internal_id(app_id, user_id, bucket, 0, document_key)
                    internal[intf.ID] = document_id
            else:
                if type(val) == dict:
                    val = _from_dict(val)
                elif type(val) == list:
                    val = _from_list(val)
                elif isinstance(val, basestring):
                    val = try_convert_to_date(val)
                internal[key] = val
        return internal

    def _from_list(l):
        """
            Gets document as a parameter of list type.
            Runs through top level keys. If object by key is dict
            type then invokes _from_doc. If object by
            key is list then invokes _from_list recursively.
        """
        internal = []
        for val in l:
            if type(val) == list:
                val = _from_list(val)
            elif type(val) == dict:
                val = _from_dict(val)
            internal.append(val)
        return internal

    return _from_dict(doc)


def _generate_criteria(app_id, user_id, bucket, document_id=None,
                       filter_opts=None):
    if document_id:
        criteria = { intf.ID :document_id }
    else:
        criteria = {
            intf.HASHID: sha1(app_id+user_id+bucket+str(False)).hexdigest()
        }

    if filter_opts:
        filter_opts = _from_external_to_internal(app_id, user_id, bucket, filter_opts)
        if intf.ID in filter_opts:
            criteria = { intf.ID : filter_opts[intf.ID] }
        else:
            criteria.update(filter_opts)

    return criteria


reg = re.compile(r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d*))?Z?$')
def try_convert_to_date(data):
    res = re.match(reg, data)
    if res:
        val = [int(x) if x else 0 for x in res.groups()]
        return datetime(*val)
    else:
        return data
