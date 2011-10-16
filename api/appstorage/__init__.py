__author__ = 'qweqwe'

from  datetime import datetime
import time
from flaskext.mongokit import Document
from pymongo.objectid import ObjectId
from extensions import db
from extensions.guard import guard


entities = db.connection.test_db.entities

USER_ID = 'tHeUsErId'
APP_ID = 'tHeApPiD'

def key2id(key):
    timestamp = time.mktime(datetime.utcnow().utctimetuple())
    return '{user_id}_{app_id}_{key}'.format(user_id=USER_ID,
                                             app_id=APP_ID,
                                             key=key)


class Entity(Document):
    __collection__ = 'entities'

    structure = {
        '__user_id__': unicode,
        '__app_id__': unicode,
        '__type__': unicode,
        '__created_at__': datetime,
        '__ip_address__': unicode,
    }

    required_fields = ['__app_id__', '__user_id__', '__type__',
                       '__created_at__', '__ip_address__',]

    
db.register([Entity])

def save(bucket=None, entry=None, key=None):
    if key is None:
        
        

def all(bucket=None, page=1):
    """
    Retrieves documents from a bucket sorted by date added (? This may change)
    """
    db.Entity.find({
        '__user_id__': USER_ID,
        '__app_id__' : APP_ID,
        '__type__': bucket
    })

def get(bucket=None, key=None):
    """
    Retrieves document from a bucket by id
    """
    db.Entity.find({
        '__user_id__': USER_ID,
        '__app_id__' : APP_ID,
        '__type__': bucket,
        '_id': key
    })


