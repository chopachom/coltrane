__author__ = 'apetrovich'

from  datetime import datetime
import uuid
from errors import EntryNotFoundError
from flaskext.mongokit import Document
from extensions import db
from extensions.guard import guard


def get_user_id():
    return guard.current_user_token

def get_app_id():
    return guard.current_app_token


def key2id(bucket, key):
    #timestamp = time.mktime(datetime.utcnow().utctimetuple())
    return u'{user_id}_{app_id}_{bucket}_{key}'.format(
        user_id=get_user_id(), app_id=get_app_id(), bucket=bucket, key=key
    )

class Entity(Document):
    use_schemaless = True
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
    default_values = {'__deleted__': False}

    
db.register([Entity])

def save(bucket=None, document=None, key=None):
    #random uuid string if key is not specified
    if key is None:
        key = unicode(uuid.uuid4())
    entity =  db.Entity()
    entity['__user_id__'] = get_user_id()
    entity['__app_id__']  = get_app_id()
    entity['__bucket__']  = bucket
    entity['__created_at__']  = datetime.utcnow()
    entity['__ip_address__']  = u'127.0.0.1'
    entity['_id'] = key2id(bucket, key)

    for k, v in document.items():
        if not entity.has_key(k):
            entity[k] = unicode(v)

    entity.save()
    return key

        

def all(bucket=None, page=1):
    """
    Retrieves documents from a bucket sorted by date added (? This may change)
    """
    #using list to avoid TypeError: <mongokit.cursor.Cursor object at blablalbla> is not JSON serializable error
    return list(db.Entity.find({
        '__user_id__': get_user_id(),
        '__app_id__' : get_app_id(),
        '__deleted__': False,
        '__bucket__': bucket
    }).sort('__created_at__'))


def get(bucket=None, key=None):
    """
    Retrieves document from a bucket by id
    """
    #TODO: raise error when no bucket and key specified
    entry = db.Entity.find_one({
        '_id': key2id(bucket, key)
    })

    if not entry:
        raise EntryNotFoundError(key=key, bucket=bucket)
    else:
        document = {k:v for k,v in entry.items()
                if not str(k).startswith('__') and str(k) != '_id'}
        # TheUserId_TheAppId_bucket1_20b6389b-76da-43de-8ea6-8c03acfc898f' to '20b6389b-76da-43de-8ea6-8c03acfc898f'
        document[u'_id'] = entry[u'_id'].split('_')[-1]
        document[u'_bucket'] = entry[u'__bucket__']
        document[u'_created_at'] = entry[u'__created_at__']
        return document


def delete(bucket=None, key=None):
    #TODO: raise error when key is not specified
    entity = db.Entity.find_one({
        '__user_id__': get_user_id(),
        '__app_id__' : get_app_id(),
        '__deleted__': False,
        '__bucket__': bucket,
        '_id': key
    })
    if entity:
        entity['deleted'] = True
        entity.save()
