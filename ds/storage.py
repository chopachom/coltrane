__author__ = 'nik'

from extensions import mongodb
from uuid import uuid4
from datetime import datetime
from errors import *
from utils import attrdict, Enum



class int_fields(Enum):
    APP_ID  = '__app_id__'
    USER_ID = '__user_id__'
    BUCKET  = '__bucket__'
    DOCUMENT_ID = '_id'
    DELETED     = '__deleted__'
    CREATED_AT  = '__created_at__'
    UPDATED_AT  = '__updated_at__'
    IP_ADDRESS  = '__ip_address__'

class ext_fields(Enum):
    DOCUMENT_KEY = '_key'
    BUCKET      = '_bucket'
    CREATED_AT  = '_created'

#Convenient shortcuts
int = int_fields
ext = ext_fields

# internal constants
_DICT_TYPE = type(dict())
_DOCUMENT_ID_FORMAT = '{app_id}|{user_id}|{bucket}|{document_key}'

# PyMongo variables
_con = mongodb.connection
_db = _con.test_database # for prototype purposes only
_entities = _db.entities


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
        raise InvalidDocumentError('document must be not null')
    if type(document) is not _DICT_TYPE:
        raise InvalidDocumentError('document must be instance of dict type')
    for k in document.keys():
        if k in int_fields.values():
            raise InvalidDocumentError(
                'document contains not allowed key ' + k)

    # check if a key is already exists, if it isn't - generate new
    if ext_fields.DOCUMENT_KEY in document:
        document_id = _generate_document_id(app_id, user_id,
                                   document[ext_fields.DOCUMENT_KEY],
                                   bucket)
        if _is_document_exists(id):
            raise InvalidDocumentKeyError('document id already exists', id=document_id)
    else:
        document_id = _generate_document_id(app_id, user_id, uuid4(), bucket)

    # add required fields to document
    document[int_fields.DOCUMENT_ID] = document_id
    document[int_fields.APP_ID] = app_id
    document[int_fields.USER_ID] = user_id
    document[int_fields.CREATED_AT] = datetime.utcnow()
    document[int_fields.IP_ADDRESS] = ip_address
    document[int_fields.BUCKET] = bucket
    document[int_fields.DELETED] = False

    _entities.insert(document)

    return _extract_document_key_from_document_id(document_id)

def find_all(app_id, user_id, bucket):
    if app_id is None:
        raise InvalidAppIdError('app_id must be not null')
    if user_id is None:
        raise InvalidUserIdError('user_id must be not null')
    criteria = _generate_criteria(app_id, user_id, bucket)
    documents = _entities.find(criteria)

    return map(_get_external_document_view, documents)

def read(app_id, user_id, document_key, bucket):
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
    if document_key is None:
        raise InvalidDocumentKeyError('document_key must be not null')

    # logic
    id = _generate_document_id(app_id, user_id, document_key, bucket)
    result = _entities.find_one({'_id': id})
    if result is None:
        return None

    return _get_external_document_view(result)


def update(app_id, user_id, ip_address, document, bucket):
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
        raise InvalidDocumentError('Entity for update cannot be null')
    if type(document) is not _DICT_TYPE:
        raise InvalidDocumentError('document must be instance of dict type')
    if document['_key'] is None:
        raise InvalidDocumentKeyError('Key of entity for update cannot be null')

    # check user access to this document
    document_id = _generate_document_id(app_id, user_id, document[ext_fields.DOCUMENT_KEY],
                               bucket)
    raise_error_if_document_not_exists(document_id)

    document_to_update = _get_cleaned_document_from_internal_fields(document)
    document_to_update[int_fields.IP_ADDRESS] = ip_address
    document_to_update[int_fields.UPDATED_AT] = datetime.utcnow()

    id = _generate_document_id(app_id, user_id, document[int_fields.DOCUMENT_ID],
                               bucket)
    
    _entities.update({'_id': id}, {'$set': document_to_update})

def delete_all(app_id, user_id, ip_address, bucket):
    # validations
    if app_id is None:
        raise InvalidAppIdError('app_id must be not null')
    if user_id is None:
        raise InvalidUserIdError('user_id must be not null')

    criteria = _generate_criteria(app_id, user_id, bucket)
    _entities.update(criteria, {'$set': _get_delete_fields_dict(ip_address)})
    

def delete(app_id, user_id, ip_address, document_key, bucket):
    """ Delete operation for CRUD.
        Parameters:
        app_id: String, application id
        user_id: String, user id
        document_key: String, document key
        bucket: String, type of entity """

    # validations
    if app_id is None:
        raise InvalidAppIdError('app_id must be not null')
    if user_id is None:
        raise InvalidUserIdError('user_id must be not null')
    if document_key is None:
        raise InvalidDocumentKeyError('document_key must be not null')

    # logic
    document_id = _generate_document_id(app_id, user_id, document_key,
                               bucket)
    # check user access to this document
    raise_error_if_document_not_exists(document_id)

    internal_id = _generate_document_id(app_id, user_id, document_key, bucket)
    _entities.update({'_id': internal_id},
                     {'$set': _get_delete_fields_dict(ip_address)})


def _is_document_exists(document_id):
    """ This function checks whether db contains document with specified id or not.
           Parameters:
           document_id: String, document id.
           Returns: True if document is exists with specified id and False if not."""

    # query document with one field (_id) to decrease network traffic. It is necessary fields minimum.
    if type(document_id) != str:
        raise RuntimeError("You must pass only string object as a document id.")
    
    found_id =  _entities.find_one({'_id': document_id}, fields=['_id'])
    if found_id is None:
        return False
    else:
        return True

def _generate_document_id(app_id, user_id, document_key, bucket):
    return _DOCUMENT_ID_FORMAT.format(app_id=app_id, user_id=user_id,
                                      bucket=bucket, document_key=document_key)


def _extract_document_key_from_document_id(internal_id):
    return '|'.join(substr for substr in internal_id.split('|')[3:])


def _generate_criteria(app_id, user_id, bucket, document_id=None):
    criteria = {
        int_fields.APP_ID: str(app_id),
        int_fields.USER_ID: str(user_id),
        int_fields.BUCKET: str(bucket),
        int_fields.DELETED: False,
    }
    if document_id:
        criteria[int_fields.DOCUMENT_ID] = document_id

    return criteria

def _get_delete_fields_dict(ip_address):
    delete_dict = {int_fields.DELETED:True,
                   int_fields.IP_ADDRESS:ip_address,
                   int_fields.UPDATED_AT:datetime.utcnow()}
    return delete_dict

def _get_external_document_view(document):
    external = _get_cleaned_document_from_internal_fields(document)
    external[ext_fields.DOCUMENT_KEY] = _extract_document_key_from_document_id(document[int_fields.DOCUMENT_ID])
    external[ext_fields.BUCKET]      = document[int_fields.BUCKET]
    external[ext_fields.CREATED_AT]  = document[int_fields.CREATED_AT]

    return external

def _get_cleaned_document_from_internal_fields(document):
    return {k: v for k, v in document.items()
                if not k in int_fields.values()}

def raise_error_if_document_not_exists(document_id):
    if _is_document_exists(document_id) == False:
        raise InvalidDocumentKeyError(id=document_id)
