from pymongo import Connection
from pymongo.objectid import ObjectId
from pymongo.errors import InvalidId
from crud_exceptions import *

# protected constants
_DICT_TYPE = type(dict())

# public contstants
APP_ID_KEY = 'app_id'
USER_ID_KEY = 'user_id'
ENTITY_DATA_KEY = 'entity_data'
ENTITY_TYPE_KEY = 'entity_type'
ENTITY_ID_KEY = '_id'
DEFAULT_ENTITY_TYPE = 'default'

# PyMongo variables
_con = Connection()
_db = _con.test_database # for prototype purposes only
_entities = _db.entities

def create(app_id, user_id, entity_data, entity_type=DEFAULT_ENTITY_TYPE):
    """ Create operation for CRUD service.
        Parameters:
        app_id: String, application id
        user_id: String, user id
        entity_data: Dict, entity data
        entity_type: String, type of entity
        
        Returns id of inserted entity """
        
    # validations
    if (app_id is None): 
        raise InvalidAppIdException('app_id must be not null')
    if (user_id is None):
        raise InvalidUserIdException('user_id must be not null')
    if (entity_data is None):
        raise InvalidEntityException('entity_data must be not null')
    if (type(entity_data) is not _DICT_TYPE):
        raise InvalidEntityException('entity_data must be instance of dict type')
    
    # logic
    data = {APP_ID_KEY: str(app_id),
            USER_ID_KEY: str(user_id),
            ENTITY_TYPE_KEY: str(entity_type),
            ENTITY_DATA_KEY: entity_data}
    return str(_entities.insert(data))
    
def read(app_id, user_id, entity_id, entity_type=DEFAULT_ENTITY_TYPE):
    """ Read operation for CRUD service.
        Parameters:
        app_id: String, application id
        user_id: String, user id
        entity_id: String, entity id
        entity_type: String, type of entity
        
        Returns founded entity object or None if object not found """
    
    # validations
    if (app_id is None):
        raise InvalidAppIdException('app_id must be not null')
    if (user_id is None):
        raise InvalidUserIdException('user_id must be not null')
    if (entity_id is None):
        raise InvalidEntityException('entity_id must be not null')
    
    # logic
    try:        
        criteria = {APP_ID_KEY: str(app_id),
                    USER_ID_KEY: str(user_id), 
                    ENTITY_TYPE_KEY: str(entity_type),
                    ENTITY_ID_KEY: ObjectId(entity_id)
                    }
    except InvalidId:
        raise InvalidEntityException('entity_id is invalid')
        
    result = _entities.find_one(criteria);
    if (result is None):
        return None
    
    # convert PyMongo's ObjectId to String value
    result[ENTITY_ID_KEY] = str(result[ENTITY_ID_KEY])
    
    # remove unnecessary fields
    del result[APP_ID_KEY]
    del result[USER_ID_KEY]
    del result[ENTITY_TYPE_KEY]
    
    return result
    
def update(app_id, user_id, entity_data, entity_type=DEFAULT_ENTITY_TYPE):
    """ Update operation for CRUD service.
        Parameters:
        app_id: String, application id
        user_id: String, user id
        entity_data: Dict, entity with entity_data['_id'] will be updated in db
        entity_type: String, entity type """
        
    # validations
    if (app_id is None):
        raise InvalidAppIdException('app_id must be not null')
    if (user_id is None):
        raise InvalidUserIdException('user_id must be not null')
    if (entity_data is None) :
        raise InvalidEntityException('Entity for update cannot be null')
    if (entity_data['_id'] is None):
        raise InvalidEntityException('Id of entity for update cannot be null')
    if (type(entity_data) is not _DICT_TYPE):
        raise InvalidEntityException('entity_data must be instance of dict type')
    
    # check user access to this entity
    _check_access(app_id, user_id, entity_data[ENTITY_ID_KEY], entity_type)
    
    # logic
    # replace String id by PyMongo ObjectId
    entity_data[ENTITY_ID_KEY] = ObjectId(entity_data[ENTITY_ID_KEY])
    
    _entities.update({'_id': entity_data[ENTITY_ID_KEY]}, # search by old id
        {'$set': {ENTITY_DATA_KEY: entity_data[ENTITY_DATA_KEY]}}, # replace entity body
        upsert=True)
    
    # replace PyMongo ObjectId by String id
    entity_data[ENTITY_ID_KEY] = str(entity_data[ENTITY_ID_KEY])
    
def delete(app_id, user_id, entity_id, entity_type=DEFAULT_ENTITY_TYPE):
    """ Delete operation for CRUD service.
        Parameters:
        app_id: String, application id
        user_id: String, user id
        entity_id: String, entity id
        entity_type: String, type of entity """
        
    # validations
    if (app_id is None):
        raise InvalidAppIdException('app_id must be not null')
    if (user_id is None):
        raise InvalidUserIdException('user_id must be not null')
    if (entity_id is None):
        raise InvalidEntityException('entity_id must be not null')
    
    # logic
    # check user access to this entity
    _check_access(app_id, user_id, entity_id, entity_type)
    _entities.remove(ObjectId(entity_id))
        
def _check_access(app_id, user_id, entity_id, entity_type):
    entity = read(app_id, user_id, entity_id, entity_type)
    if (entity is None):
        raise InvalidEntityException('User #{0} dont have access to entity with id #{1} ' +
                                     'or this entity doesnt exists'
                                     .format(user_id, entity_id))
