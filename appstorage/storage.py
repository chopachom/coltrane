import copy

__author__ = 'nik'

import json
#TODO: unbind from api extensions
from api.extensions import mongodb
from uuid import uuid4
from datetime import datetime
from errors import *
from utils import Enum

class int_fields(Enum):
    APP_ID      = '__app_id__'
    USER_ID     = '__user_id__'
    BUCKET      = '__bucket__'
    ID          = '_id'
    DELETED     = '__deleted__'
    CREATED_AT  = '__created_at__'
    UPDATED_AT  = '__updated_at__'
    IP_ADDRESS  = '__ip_address__'

class ext_fields(Enum):
    KEY         = '_key'
    BUCKET      = '_bucket'
    CREATED_AT  = '_created'


# internal constants
_DICT_TYPE = type(dict())
_DOCUMENT_ID_FORMAT = '{app_id}|{user_id}|{bucket}|{document_key}'

# PyMongo variables
#_con = mongodb.connection
#_db = _con.test_database # for prototype purposes only
#_entities = _db.entities
_entities = lambda : mongodb.connection.test_database.entities

def create(app_id, user_id, ip_address, document, bucket):
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
    if app_id is None:
        raise InvalidAppIdError('app_id must be not null')
    if user_id is None:
        raise InvalidUserIdError('user_id must be not null')
    if document is None:
        raise InvalidDocumentError('Document must be not null')
    if type(document) is not _DICT_TYPE:
        raise InvalidDocumentError('Document must be instance of dict type')
    

    # check if a key is already exists, if it isn't - generate new
    if ext_fields.KEY in document:
        document_id = _document_id(app_id, user_id, bucket,
                                   document[ext_fields.KEY])
        criteria = {int_fields.ID: document_id}
        if _is_document_exists(criteria):
            raise InvalidDocumentKeyError('Document with key [%s] already exists' % document[ext_fields.KEY])
    else:
        document_id = _document_id(app_id, user_id, bucket, uuid4())

    document = _filter_ext_fields(document)
    # add required fields to document
    document[int_fields.ID] = document_id
    document[int_fields.APP_ID] = app_id
    document[int_fields.USER_ID] = user_id
    document[int_fields.CREATED_AT] = datetime.utcnow()
    document[int_fields.IP_ADDRESS] = ip_address
    document[int_fields.BUCKET] = bucket
    document[int_fields.DELETED] = False

    _entities().insert(document)

    return _document_key(document_id)


def get_by_key(app_id, user_id, bucket, key):
    """ Read operation for CRUD service.
        Parameters:
        app_id: String, application id
        user_id: String, user id
        document_key: String, document key
        bucket: String, type of document
        
        Returns founded document or None if object not found """

    # validations
    if app_id is None:
        raise InvalidAppIdError('app_id must be not null')
    if user_id is None:
        raise InvalidUserIdError('user_id must be not null')
    if key is None:
        raise InvalidDocumentKeyError('document_key must be not null')

    # logic

    document_id = _document_id(app_id, user_id, bucket, key)
    res = _entities().find_one({int_fields.ID: document_id, int_fields.DELETED: False})
    if res is None:
        return None

    return _external_document(res)


def get_by_filter(app_id, user_id, bucket, filter_opts=None):
    if app_id is None:
        raise InvalidAppIdError('app_id must be not null')
    if user_id is None:
        raise InvalidUserIdError('user_id must be not null')
    
    criteria = _generate_criteria(app_id, user_id, bucket, filter_opts=filter_opts)

    _delete_redundant_opts(criteria)
        
    documents = list(_entities().find(criteria))
    return map(_external_document, documents)


def update_by_key(app_id, user_id, ip_address, bucket, document, key):
    if key is None:
        raise InvalidDocumentKeyError('document_key must be not null')
    update_by_filter(app_id, user_id, ip_address, bucket, document, {ext_fields.KEY: key})


def update_by_filter(app_id, user_id, ip_address, bucket, document, filter_opts=None):
    """ Update operation for CRUD.
        Parameters:
        app_id: String, application id
        user_id: String, user id
        document: Dict, document with given _id will be updated in db
        bucket: String, document type """

    # validations
    if app_id is None:
        raise InvalidAppIdError('app_id must be not null')
    if user_id is None:
        raise InvalidUserIdError('user_id must be not null')
    if document is None:
        raise InvalidDocumentError('Document for update cannot be null')
    if type(document) is not _DICT_TYPE:
        raise InvalidDocumentError('Document must be instance of dict type')

    criteria = _generate_criteria(app_id, user_id, bucket, filter_opts=filter_opts)

    # if update document by key
    # (we only should search by __id and __deleted)
    _delete_redundant_opts(criteria)

    document_to_update = _filter_int_fields(_filter_ext_fields(document))
    document_to_update[int_fields.IP_ADDRESS] = ip_address
    document_to_update[int_fields.UPDATED_AT] = datetime.utcnow()
    _entities().update(criteria, {'$set': document_to_update}, multi=True)


def delete_by_key(app_id, user_id, ip_address, bucket, key):
    if key is None:
        raise InvalidDocumentKeyError('document_key must be not null')
    delete_by_filter(app_id, user_id, ip_address, bucket, {ext_fields.KEY: key})


def delete_by_filter(app_id, user_id, ip_address, bucket, filter_opts=None):
    # validations
    if app_id is None:
        raise InvalidAppIdError('app_id must be not null')
    if user_id is None:
        raise InvalidUserIdError('user_id must be not null')

    criteria = _generate_criteria(app_id, user_id, bucket, filter_opts=filter_opts)

    _delete_redundant_opts(criteria)
        
    _entities().update(
        criteria, {'$set': _fields_for_update_on_delete(ip_address)}, multi=True
    )
    


def is_document_exists(app_id, user_id, bucket, criteria=None):
    """ Function for the external performing
    """
    criteria = copy.deepcopy(criteria)
    res_criteria = _generate_criteria(app_id, user_id, bucket)
    if criteria:
        if type(criteria) is not dict:
            raise RuntimeError("Criteria object must be dict type.")
        if  ext_fields.KEY in criteria:
            document_id = _document_id(app_id, user_id, bucket, criteria[ext_fields.KEY])
            res_criteria[int_fields.ID] = document_id

            del criteria[ext_fields.KEY]  # it is harmful field when iterating in the for loop bellow
            # as we have _id search criteria no use search by app_id, user_id and bucket
            del res_criteria[int_fields.APP_ID]
            del res_criteria[int_fields.USER_ID]
            del res_criteria[int_fields.BUCKET]
        for key in criteria.keys():
            if key not in int_fields:
                res_criteria[key] = criteria[key]

    return _is_document_exists(res_criteria)


def _is_document_exists(criteria):
    """ Function for the internal performing
        This function checks whether db contains document with specified id.
           Parameters:
           document_id: String, document id.
           Returns: True if document is exists with specified id and False if not."""

    if not criteria:
        raise RuntimeError('Criteria object must not be None')

    # query document with one field (_id) to decrease network traffic. It is necessary fields minimum.
    found =  _entities().find_one(criteria,  fields=['_id'])
    if found:
        return True
    else:
        return False


def _document_id(app_id, user_id, bucket, document_key):
    return _DOCUMENT_ID_FORMAT.format(app_id=app_id, user_id=user_id,
                                      bucket=bucket, document_key=document_key)


def _document_key(internal_id):
    return '|'.join(substr for substr in internal_id.split('|')[3:])


def _generate_criteria(app_id, user_id, bucket, document_id=None, filter_opts=None):
    criteria = {
        int_fields.APP_ID: str(app_id),
        int_fields.USER_ID: str(user_id),
        int_fields.BUCKET: str(bucket),
        int_fields.DELETED: False,
    }
    if document_id:
        criteria[int_fields.ID] = document_id

    if filter_opts:
        filter_opts = _from_external_to_internal(filter_opts, app_id, user_id, bucket)
        for opt_key in filter_opts.keys():
            criteria[opt_key] = filter_opts[opt_key]

    return criteria


def _delete_redundant_opts(criteria):
    if int_fields.ID in criteria:
        del criteria[int_fields.APP_ID]
        del criteria[int_fields.USER_ID]
        del criteria[int_fields.BUCKET]


def _fields_for_update_on_delete(ip_address):
    dict = {int_fields.DELETED:True,
                   int_fields.IP_ADDRESS:ip_address,
                   int_fields.UPDATED_AT:datetime.utcnow()}
    return dict

def _external_document(document):
    if not document:
        return None

    external = _filter_int_fields(document)
    external[ext_fields.KEY] = _document_key(document[int_fields.ID])
    external[ext_fields.BUCKET]      = document[int_fields.BUCKET]
    external[ext_fields.CREATED_AT]  = document[int_fields.CREATED_AT]

    return external

def _filter_int_fields(document):
    """
    Filter out all internal fields
    """
    return {k: v for k, v in document.items()
                if not k in int_fields.values()}

def _filter_ext_fields(document):
    """
    Filter out all external fields
    """
    return {k: v for k, v in document.items()
                if not k in ext_fields.values()}

def _from_external_to_internal(doc, app_id, user_id, bucket):
    """
    Convert document from external view to the internal.
    Deletes any internal fields at start.
    If document contains external fields, convert its values to the internal fields.
    """
    internal = {}
    doc = _filter_int_fields(doc)
    for key in doc:
        if key not in ext_fields.values():
            internal[key] = doc[key]
        else:
            if key == ext_fields.BUCKET:
                internal[int_fields.BUCKET] = doc[key]
            elif key == ext_fields.CREATED_AT:
                internal[int_fields.CREATED_AT] = doc[key]
            elif key == ext_fields.KEY:
                document_key = doc[key]
                document_id = _document_id(app_id, user_id, bucket, document_key)
                internal[int_fields.ID] = document_id
    return internal

def _assert_exists(bucket, criteria, document_key=None):
    if not _is_document_exists(criteria):
        if document_key:
            raise DocumentNotFoundError(message=DocumentNotFoundError.DOCUMENT_BY_KEY,
                                        key=document_key, bucket=bucket)
        else:
            raise DocumentNotFoundError(criteria=json.dumps(criteria), bucket=bucket)
