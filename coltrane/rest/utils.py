# -*- coding: utf-8 -*-
"""
    :Authors: - qweqwe
              - pasha
"""

from coltrane.appstorage.storage import intf
from coltrane.rest.extensions import mongodb
from coltrane.utils import Enum

import re
from flask import current_app, request
from functools import wraps
import json
import datetime


#TODO: may be we need to move it to statuses module?
class resp_msgs(Enum):
    DOC_NOT_EXISTS  = "Document doesn't exist"
    DOC_CREATED = "Document has been created"
    DOC_DELETED = "Document has been deleted"
    DOC_UPDATED = "Document has been updated"
    INTERNAL_ERROR  = "Internal server error"


class forbidden_fields(Enum):
    WHERE      = '$where'
    ID         = intf.ID



class lazy_coll(object):
    """
        This class is used to initialize mongodb collection lazily.
        I.e. it will use mongodb collection object only when Flask
        application was initialized.
    """
    class __metaclass__(type):
        coll = None
        @property
        def entities(self):
            if self.coll:
                return self.coll
            else:
                conf = current_app.config
                db   = conf['MONGODB_DATABASE']
                coll = conf['APPDATA_COLLECTION']
                self.coll = mongodb.connection[db][coll]
                return self.coll
        def __getattr__(self, name):
            return getattr(self.entities, name)

def jsonify(f):
    """ Used to decorate Flask route handlers,
        it will return json with proper mime-type
    """

    DT_HANDLER = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

    def to_json(dict):
        return json.dumps(dict, indent=None if request.is_xhr else 2,
            default=DT_HANDLER)

    @wraps(f)
    def wrapper(*args, **kwargs):
        resp = f(*args, **kwargs)
        try:
            body, code = resp
        except (TypeError, ValueError) as e:
            body = resp
            code = 200
        if not isinstance(body, current_app.response_class):
            return current_app.response_class(to_json(body),
                mimetype='application/json', status=code)
        else:
            return body

    return wrapper


reg = re.compile(r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d*))?Z?$')
def try_convert_to_date(data):
    if not isinstance(data, basestring):
        #TODO:REMOVE THIS FUCKING SHAME
        raise RuntimeError('Only str type data must be converted to date.')
    res = re.match(reg, data)
    #TODO: PASHA БЛЯ ДОБАВЛЯЙ КОММЕНТЫ К КОДУ НАХ!
    # я запушил неглядя и теперь вот сижу думаю че тут происходит
    if res:
        val = [int(x) if x else 0 for x in res.groups()]
        return datetime.datetime(*val)
    else:
        return data
