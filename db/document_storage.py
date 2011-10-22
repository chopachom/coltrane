__author__ = 'nik'

from extensions import db
from app_exceptions import *
from uuid import uuid4

# protected constants
_DICT_TYPE = type(dict())
_DOCUMENT_ID_FORMAT = '{app_id}_{user_id}_{bucket}_{document_id}'

# public contstants
APP_ID_KEY = 'app_id'
USER_ID_KEY = 'user_id'
BUCKET_KEY = 'bucket'
DOCUMENT_ID_KEY = '_id'
DEFAULT_BUCKET_KEY = 'default'

# PyMongo variables
_con = db.connection
_db = _con.test_database # for prototype purposes only
_entities = _db.entities

def create(app_id, user_id, document, bucket=DEFAULT_BUCKET_KEY):
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
        If user document's _id already exists, InvalidDocumentIdException will be raised.
        Parameters:
        app_id: String, application id
        user_id: String, user id
        document: Dict, user document
        bucket: String, document type (bucket)
        
        Returns id of inserted entity """
        
    # validations
    if app_id is None: 
        raise InvalidAppIdException('app_id must be not null')
    if user_id is None:
        raise InvalidUserIdException('user_id must be not null')
    if document is None:
        raise InvalidDocumentException('document must be not null')
    if type(document) is not _DICT_TYPE:
        raise InvalidDocumentException('document must be instance of dict type')
             
    # logic
    document_to_save = {}
    # generate id
    if DOCUMENT_ID_KEY in document:
        # check if id already exists
        id = _generate_internal_id(app_id, user_id, document[DOCUMENT_ID_KEY], bucket)
        criteria = _generate_criteria(app_id, user_id, id, bucket);
        if _entities.find_one(criteria):
            raise IvalidDocumentIdException('document id already exists')
    else:
        # generate new id
        id = _generate_internal_id(app_id, user_id, uuid4(), bucket)
    
    # add required fields to document
    document_to_save[DOCUMENT_ID_KEY] = id
    document_to_save[APP_ID_KEY] = app_id
    document_to_save[USER_ID_KEY] = user_id
    document_to_save[BUCKET_KEY] = bucket
    
    # add user document values
    for k, v in document.iteritems():
        document_to_save[k] = v
    
    _entities.insert(document_to_save)
    
    return _get_public_id(document_to_save[DOCUMENT_ID_KEY])
    
def read(app_id, user_id, document_id, bucket=DEFAULT_BUCKET_KEY):
    """ Read operation for CRUD service.
        Parameters:
        app_id: String, application id
        user_id: String, user id
        document_id: String, document id
        bucket: String, type of document
        
        Returns founded document or None if object not found """
    
    # validations
    if app_id is None:
        raise InvalidAppIdException('app_id must be not null')
    if user_id is None:
        raise InvalidUserIdException('user_id must be not null')
    if document_id is None:
        raise InvalidDocumentIdException('document_id must be not null')
    
    # logic
    id = _generate_internal_id(app_id, user_id, document_id, bucket)
    criteria = _generate_criteria(app_id, user_id, id, bucket)
    result = _entities.find_one(criteria);
    if result is None:
        return None
    
    # remove unnecessary fields
    del result[APP_ID_KEY]
    del result[USER_ID_KEY]
    del result[BUCKET_KEY]
    
    # replace document id
    result[DOCUMENT_ID_KEY] = _get_public_id(result[DOCUMENT_ID_KEY])
    
    return result
    
def update(app_id, user_id, document, bucket=DEFAULT_BUCKET_KEY):
    """ Update operation for CRUD.
        Parameters:
        app_id: String, application id
        user_id: String, user id
        document: Dict, document with given _id will be updated in db
        bucket: String, document type """
        
    # validations
    if app_id is None:
        raise InvalidAppIdException('app_id must be not null')
    if user_id is None:
        raise InvalidUserIdException('user_id must be not null')
    if document is None:
        raise InvalidDocumentException('Entity for update cannot be null')
    if document['_id'] is None:
        raise InvalidDocumentIdException('Id of entity for update cannot be null')
    if type(document) is not _DICT_TYPE:
        raise InvalidDocumentException('document must be instance of dict type')
    
    # check user access to this document
    _check_access(app_id, user_id, document[DOCUMENT_ID_KEY], bucket)
    
    # logic
    document_to_update = {}
    for k, v in document.iteritems():
        if k is not DOCUMENT_ID_KEY:
            document_to_update[k] = v
        
    id = _generate_internal_id(app_id, user_id, document[DOCUMENT_ID_KEY], bucket)
    _entities.update({'_id': id}, # search by old id
        {'$set': document_to_update}) # edit user document body
    
def delete(app_id, user_id, document_id, bucket=DEFAULT_BUCKET_KEY):
    """ Delete operation for CRUD.
        Parameters:
        app_id: String, application id
        user_id: String, user id
        document_id: String, document id
        bucket: String, type of entity """
        
    # validations
    if app_id is None:
        raise InvalidAppIdException('app_id must be not null')
    if user_id is None:
        raise InvalidUserIdException('user_id must be not null')
    if document_id is None:
        raise InvalidDocumentIdException('document_id must be not null')
    
    # logic
    # check user access to this document
    _check_access(app_id, user_id, document_id, bucket)
    
    internal_id = _generate_internal_id(app_id, user_id, document_id, bucket)
    _entities.remove(internal_id)
        
def _check_access(app_id, user_id, document_id, bucket):
    entity = read(app_id, user_id, document_id, bucket)
    if entity is None:
        raise InvalidDocumentIdException('User #{0} dont have access to entity #{1}'
                                         .format(user_id, document_id) + 
                                         ' or this entity doesnt exists')
        
def _generate_internal_id(app_id, user_id, document_id, bucket):
    return _DOCUMENT_ID_FORMAT.format(app_id=app_id, user_id=user_id, bucket=bucket, document_id=document_id)
    
def _get_public_id(internal_id):
    return '_'.join(substr for substr in internal_id.split('_')[3:])
    
def _generate_criteria(app_id, user_id, document_id, bucket):
    return  {
                APP_ID_KEY: str(app_id),
                USER_ID_KEY: str(user_id), 
                BUCKET_KEY: str(bucket),
                DOCUMENT_ID_KEY: document_id
            }
