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
    DEFAULT_BUCKET = 'default'


class ext_fields(Enum):
    DOCUMENT_ID = '_id'
    BUCKET      = '_bucket'
    CREATED_AT  = '_created'

#Convenient shortcuts
int = int_fields
ext = ext_fields

# internal constants
_DICT_TYPE = type(dict())
_DOCUMENT_ID_FORMAT = '{app_id}|{user_id}|{bucket}|{document_id}'

# PyMongo variables
_con = mongodb.connection
_db = _con.test_database # for prototype purposes only
_entities = _db.entities


def create(app_id, user_id, ip_address, document,
           bucket=int_fields.DEFAULT_BUCKET):
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
        
        Returns id of inserted entity """

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

    document_to_save = _get_cleaned_document(document)
    # check if an id is already exists, if it isn't - generate new
    if int_fields.DOCUMENT_ID in document:
        id = _generate_internal_id(app_id, user_id,
                                   document[int_fields.DOCUMENT_ID],
                                   bucket)
        criteria = _generate_criteria(app_id, user_id, id, bucket)
        if _entities.find_one(criteria):
            raise InvalidDocumentIdError('document id already exists')
    else:
        id = _generate_internal_id(app_id, user_id, uuid4(), bucket)

    # add required fields to document
    document_to_save[int_fields.DOCUMENT_ID] = id
    document_to_save[int_fields.APP_ID] = app_id
    document_to_save[int_fields.USER_ID] = user_id
    document_to_save[int_fields.CREATED_AT] = datetime.utcnow()
    document_to_save[int_fields.IP_ADDRESS] = ip_address
    document_to_save[int_fields.BUCKET] = bucket
    document_to_save[int_fields.DELETED] = False

    _entities.insert(document_to_save)

    return _get_public_id(document_to_save[int_fields.DOCUMENT_ID])


def read(app_id, user_id, document_id, bucket=int_fields.DEFAULT_BUCKET):
    """ Read operation for CRUD service.
        Parameters:
        app_id: String, application id
        user_id: String, user id
        document_id: String, document id
        bucket: String, type of document
        
        Returns founded document or None if object not found """

    # validations
    if app_id is None:
        raise InvalidAppIdError('app_id must be not null')
    if user_id is None:
        raise InvalidUserIdError('user_id must be not null')
    if document_id is None:
        raise InvalidDocumentIdError('document_id must be not null')

    # logic
    id = _generate_internal_id(app_id, user_id, document_id, bucket)
    criteria = _generate_criteria(app_id, user_id, id, bucket)
    result = _entities.find_one(criteria)
    if result is None:
        return None

    return _get_external_document(result)


def update(app_id, user_id, ip_address, document, bucket=int_fields.DEFAULT_BUCKET):
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
    if document['_id'] is None:
        raise InvalidDocumentIdError(
            'Id of entity for update cannot be null')
    if type(document) is not _DICT_TYPE:
        raise InvalidDocumentError('document must be instance of dict type')

    # check user access to this document
    _check_exists(app_id, user_id, document[int_fields.DOCUMENT_ID], bucket)

    document_to_update = _get_cleaned_document(document)
    document_to_update[int_fields.IP_ADDRESS]=ip_address
    document_to_update[int_fields.UPDATED_AT]=datetime.utcnow()

    id = _generate_internal_id(app_id, user_id, document[int_fields.DOCUMENT_ID],
                               bucket)
    
    _entities.update({'_id': id}, {'$set': document_to_update}, safe=True)


def delete(app_id, user_id, ip_address, document_id,
           bucket=int_fields.DEFAULT_BUCKET):
    """ Delete operation for CRUD.
        Parameters:
        app_id: String, application id
        user_id: String, user id
        document_id: String, document id
        bucket: String, type of entity """

    # validations
    if app_id is None:
        raise InvalidAppIdError('app_id must be not null')
    if user_id is None:
        raise InvalidUserIdError('user_id must be not null')
    if document_id is None:
        raise InvalidDocumentIdError('document_id must be not null')

    # logic
    # check user access to this document
    _check_exists(app_id, user_id, document_id, bucket)

    internal_id = _generate_internal_id(app_id, user_id, document_id, bucket)
    _entities.update({'_id': internal_id},
                     {'$set': {int_fields.DELETED:True,
                               int_fields.IP_ADDRESS:ip_address,
                               int_fields.UPDATED_AT:datetime.utcnow()}})


def _check_exists(app_id, user_id, document_id, bucket):
    entity = read(app_id, user_id, document_id, bucket)
    if entity is None:
        raise InvalidDocumentIdError(id=document_id)


def _generate_internal_id(app_id, user_id, document_id, bucket):
    return _DOCUMENT_ID_FORMAT.format(app_id=app_id, user_id=user_id,
                                      bucket=bucket, document_id=document_id)


def _get_public_id(internal_id):
    return '|'.join(substr for substr in internal_id.split('|')[3:])


def _generate_criteria(app_id, user_id, document_id, bucket):
    #Why we need all those fields? DOCUMENT_ID is already uniquely identifies document
    return  {
        int_fields.APP_ID: str(app_id),
        int_fields.USER_ID: str(user_id),
        int_fields.BUCKET: str(bucket),
        int_fields.DOCUMENT_ID: document_id,
        int_fields.DELETED: False,
    }


def _get_external_document(document):
    external = _get_cleaned_document(document)
    external[ext_fields.DOCUMENT_ID] = _get_public_id(document[int_fields.DOCUMENT_ID])
    external[ext_fields.BUCKET]      = document[int_fields.BUCKET]
    external[ext_fields.CREATED_AT]  = document[int_fields.CREATED_AT]

    return external

def _get_cleaned_document(document):
    return {k: v for k, v in document.items()
                if not k in int_fields.values()}