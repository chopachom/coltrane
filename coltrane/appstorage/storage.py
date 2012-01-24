# -*- coding: utf-8 -*-
"""
    :Authors: - qweqwe
              - pasha
              - dreambrother
"""

from datetime import datetime
from uuid import uuid4
from functools import wraps
from hashlib import sha1
from coltrane.appstorage import _external_key, _internal_id, intf, extf, reservedf, atomic_operations
from coltrane.appstorage.datatypes import BaseType
from coltrane.appstorage.typeconverters import get_external_converter, try_get_geopoint_external_converter, get_internal_converter

from .exceptions import *


# internal constants
DICT_TYPE = type(dict())

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
        # check if a key is already exists, if it isn't - generate new
        if extf.KEY not in document:
            document[extf.KEY] = uuid4()

        document = _from_external_to_internal(app_id, user_id, bucket, document)
        # add required fields to document
        document[intf.APP_ID] = app_id
        document[intf.USER_ID] = user_id
        # adding str(False) to hashid means that document isn't deleted
        document[intf.HASHID] = sha1(app_id+user_id+bucket+str(False)).hexdigest()
        document[intf.IP_ADDRESS] = ip_address
        document[intf.DELETED] = False

        document[reservedf.BUCKET] = bucket
        document[reservedf.CREATED_AT] = datetime.utcnow()

        id = document[intf.ID]
        removed_doc_criteria = {
            intf.ID: id,
            intf.DELETED: True
        }
        if self._is_document_exists(removed_doc_criteria):
            # if removed doc with same id exists - update it
            del document[intf.ID]
            self.entities.update(removed_doc_criteria, {'$set': document}, multi=False)
        else:
            self.entities.insert(document)

        return _external_key(id)


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
             sort=None, skip=0, limit=1000, count=False):

        criteria = _generate_criteria(app_id, user_id, bucket, filter_opts=filter_opts)

        opt_criteria = {}
        if skip < 0:
            raise RuntimeError("offset parameter must not be less then 0")
        if limit < 0:
            raise RuntimeError("limit parameter must be greater then 0")
        opt_criteria['skip']  = skip
        opt_criteria['limit'] = limit
        opt_criteria['sort'] = sort

        cursor = self.entities.find(criteria, **opt_criteria)
        if count:
            return cursor.count(with_limit_and_skip=True)
        else:
            documents = list(cursor)
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
        document[reservedf.UPDATED_AT] = datetime.utcnow()

        update = self._make_doc_for_update(document)

        self.entities.update(criteria, update, multi=True, safe=True)


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
                reservedf.UPDATED_AT:datetime.utcnow()
            }
        }, multi=True)


    def is_document_exists(self, app_id, user_id, bucket, filter_opts=None):
        """ Function for the external performing
        """
        criteria = _generate_criteria(app_id, user_id, bucket, filter_opts)
        return self._is_document_exists(criteria)

    def _make_doc_for_update(self, document):
        update = {}
        for k, v in document.items():
            if k in atomic_operations:
                values = update.setdefault(k, {})
                values.update(v)
            else:
                values = update.setdefault('$set', {})
                values.update({k: v})
        return update

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
    external = _from_internal_to_external(external)
    external[extf.KEY] = _external_key(document[intf.ID])

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
    def _convert_custom_type(key, val):
        converter = get_internal_converter(val)
        key, val = converter.to_internal(key, val, app_id, user_id)
        return key, val

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
            if key == extf.KEY:
                document_key = val
                document_id = _internal_id(app_id, user_id, bucket, 0, document_key)
                internal[intf.ID] = document_id
            else:
                if type(val) == dict:
                    val = _from_dict(val)
                elif type(val) == list:
                    val = _from_list(val)
                elif isinstance(val, BaseType):
                    key, val = _convert_custom_type(key, val)
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
            if isinstance(val, BaseType):
                _, val = _convert_custom_type(None, val)
            if type(val) == list:
                val = _from_list(val)
            elif type(val) == dict:
                val = _from_dict(val)
            internal.append(val)
        return internal

    return _from_dict(doc)


def _from_internal_to_external(doc):
    """
    Convert document from internal view to the external.
    If document contains external fields/data types, convert its values to the internal fields/types.
    {<int_1>:[{<int_2>:10}, {'key':20}]} => {<ext_1>:[{<ext_2>:10}, {'key':20}]}
    """
    def _from_dict(doc):
        external = {}
        for key in doc:
            val = doc[key]
            converter = None
            if type(val) == dict:
                # due to absence internal data type for geo point
                # we need to check every type whether it can be geo data.
                # Key of geo data starts with special prefix.
                converter = try_get_geopoint_external_converter(key)
                if not converter:
                    val = _from_dict(val)
            elif type(val) == list:
                val = _from_list(val)
            else:
                # val type is not dict, not list, and most likely it is internal data type
                converter = get_external_converter(val)
            if converter:
                key, val = converter.to_external(key, val)
            external[key] = val
        return external

    def _from_list(l):
        internal = []
        for val in l:
            if type(val) == list:
                val = _from_list(val)
            elif type(val) == dict:
                val = _from_dict(val)
            else:
                # val type is not dict, not list, and most likely it is internal data type
                converter = get_external_converter(val)
                if converter:
                    _, val = converter.to_external(None, val)
            internal.append(val)
        return internal

    return _from_dict(doc)




def _generate_criteria(app_id, user_id, bucket, filter_opts=None):
    """ Generates criteria object for searching or filtering in mongodb"""

    criteria = {intf.HASHID: sha1(app_id + user_id + bucket + str(False)).hexdigest()}

    if filter_opts:
        filter_opts = _from_external_to_internal(app_id, user_id, bucket, filter_opts)
        if intf.ID in filter_opts:
            del criteria[intf.HASHID]
        criteria.update(filter_opts)

    return criteria

