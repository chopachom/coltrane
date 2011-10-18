__author__ = 'qweqwe'

from  datetime import datetime
import uuid
from errors import EntryNotFoundError
from flaskext.mongokit import Document
from extensions import db



#entities = db.connection.test_db.entities

USER_ID = 'tHeUsErId'
APP_ID = 'tHeApPiD'

def key2id(key):
    #timestamp = time.mktime(datetime.utcnow().utctimetuple())
    return '{user_id}_{app_id}_{key}'.format(user_id=USER_ID,
                                             app_id=APP_ID,
                                             key=key)


class Entity(Document):
    __database__   = 'test_db'
    __collection__ = 'entities'

    structure = {
        '__user_id__': unicode,
        '__app_id__': unicode,
        '__bucket__': unicode,
        '__created_at__': datetime,
        '__ip_address__': unicode,
        '__deleted__': bool
    }

    required_fields = ['__app_id__', '__user_id__', '__bucket__',
                       '__created_at__', '__ip_address__',]
    default_values = {'deleted': False}

    
db.register([Entity])

def save(bucket=None, entry=None, key=None):
    #random uuid string if keys is not specified
    if key is None:
        key = str(uuid.uuid4())
    entry =  db.Entry()
    entry['__user_id__'] = USER_ID
    entry['__app_id__']  = APP_ID
    entry['__bucket__']  = bucket
    entry['__created_at__']  = datetime.utcnow()
    entry['__ip_address__']  = '127.0.0.1'
    entry['_id'] = key2id(key)

    for key, value in entry.items():
        if not entry.has_key(key):
            entry[key] = value

    entry.save()
    return key

        

def all(bucket=None, page=1):
    """
    Retrieves documents from a bucket sorted by date added (? This may change)
    """
    #using list to avoid TypeError: <mongokit.cursor.Cursor object at blablalbla> is not JSON serializable error
    return list(db.Entity.find({
        '__user_id__': USER_ID,
        '__app_id__' : APP_ID,
        '__deleted__': False,
        '__bucket__': bucket
    }).sort('__created_at__'))


def get(bucket=None, key=None):
    """
    Retrieves document from a bucket by id
    """
    entry = db.Entity.find_one({
        '__user_id__': USER_ID,
        '__app_id__' : APP_ID,
        '__deleted__': False,
        '__bucket__': bucket,
        '_id': key
    })

    if not entry:
        raise EntryNotFoundError(key=key)

    return entry


def delete(bucket=None, key=None):
    #TODO: raise error when key is not specified
    entity = db.Entity.find_one({
        '__user_id__': USER_ID,
        '__app_id__' : APP_ID,
        '__deleted__': False,
        '__bucket__': bucket,
        '_id': key
    })
    if entity:
        entity['deleted'] = True
        entity.save()