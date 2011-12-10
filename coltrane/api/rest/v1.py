import json
import datetime
import logging

from flask import Blueprint, current_app
from flask.globals import request
from coltrane.appstorage.storage import AppdataStorage
from coltrane.appstorage.storage import extf, intf
from coltrane.api.validators import SimpleValidator, RecursiveValidator
from coltrane.api.extensions import guard
from coltrane.api.extensions import mongodb
from coltrane.api.rest.statuses import *
from coltrane.api import exceptions
from coltrane.utils import Enum
from coltrane.exceptions import AppException

from functools import wraps



LOG = logging.getLogger('coltrane.api')
LOG.debug('starting coltrane api')

class resp_msgs(Enum):

    DOC_NOT_EXISTS  = "Document doesn't exist"
    DOC_WAS_CREATED = "Document was created"
    DOC_WAS_DELETED = "Document was deleted"
    DOC_WAS_UPDATED = "Document was updated"
    
    INTERNAL_ERROR  = "Internal server error"


class forbidden_fields(Enum):
    WHERE      = '$where'


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

api = Blueprint("api_v1", __name__)
storage = AppdataStorage(lazy_coll)



@api.route('/<bucket:bucket>', defaults={'key': None}, methods=['POST'])
@api.route('/<bucket:bucket>/<key>', methods=['POST'])
@jsonify
def post_handler(bucket, key):
    """ Create new document and get _key back
    """
    document = extract_form_data()
    validate_document(document)
    if key is not None:
        document[extf.KEY] = key
    document_key = storage.create(get_app_id(), get_user_id(), get_remote_ip(),
                                  document, bucket=bucket)
    return {extf.KEY: document_key}, http.CREATED


@api.route('/<bucket:bucket>/<keys:keys>', methods=['GET'])
@jsonify
def get_by_keys_handler(bucket, keys):
    if not len(keys):
            raise exceptions.InvalidRequestError('At least one key must be passed.')
    res = []
    http_status = http.OK

    for key in keys:
        doc = storage.get(get_app_id(), get_user_id(), bucket, key)
        if doc:
            doc_resp = {extf.KEY: key, STATUS_CODE: app.OK,
                        'document': doc}
            res.append(doc_resp)
        else:
            doc_resp = {extf.KEY: key, STATUS_CODE: app.NOT_FOUND,
                        'message': resp_msgs.DOC_NOT_EXISTS}
            res.append(doc_resp)

    if len(res) == 1:
        res = res[0]
        if res[STATUS_CODE] == app.OK:
            res = res['document']
        elif res[STATUS_CODE] == app.NOT_FOUND:
            res = {'message': res['message']}
            http_status = http.NOT_FOUND

    return {'response': res}, http_status



@api.route('/<bucket:bucket>', methods=['GET'])
@jsonify
def get_by_filter_handler(bucket):
    filter_opts = extract_filter_opts()
    validate_filter(filter_opts)
    skip, limit = extract_pagination_data()
    documents = storage.find(get_app_id(), get_user_id(), bucket,
                             filter_opts, skip, limit)
    if len(documents):
        return {'response': documents}, http.OK

    return {'message': resp_msgs.DOC_NOT_EXISTS}, http.NOT_FOUND



@api.route('/<bucket:bucket>/<keys:keys>', methods=['DELETE'])
@jsonify
def delete_by_keys_handler(bucket, keys):
    """ Deletes existing document (C.O.)
    """
    if not len(keys):
        raise exceptions.InvalidRequestError('At least one key must be passed.')

    res = []
    http_status = http.OK
    
    for key in keys:
        filter_opts = {extf.KEY: key}
        if not storage.is_document_exists(get_app_id(), get_user_id(),
                                          bucket, filter_opts):
            res.append({extf.KEY: key, STATUS_CODE: app.NOT_FOUND,
                        'message': resp_msgs.DOC_NOT_EXISTS})
        else:
            storage.delete(get_app_id(), get_user_id(), get_remote_ip(),
                           bucket=bucket, filter_opts=filter_opts)
            res.append({extf.KEY: key, STATUS_CODE: app.OK,
                        'message': resp_msgs.DOC_WAS_DELETED})

    if len(res) == 1:
        res = res[0]
        if res[STATUS_CODE] == app.NOT_FOUND:
            http_status = http.NOT_FOUND
        res = {'message': res['message']}

    return res, http_status


@api.route('/<bucket:bucket>', methods=['DELETE'])
@jsonify
def delete_by_filter_handler(bucket):
    """ Delete all documents matched with filter
    """
    filter_opts = extract_filter_opts()
    validate_filter(filter_opts)
    if not storage.is_document_exists(get_app_id(), get_user_id(),
                                      bucket, filter_opts):
        return {'message': resp_msgs.DOC_NOT_EXISTS}, http.NOT_FOUND
    
    storage.delete(get_app_id(), get_user_id(), get_remote_ip(),
                   bucket=bucket, filter_opts=filter_opts)

    return {'message': resp_msgs.DOC_WAS_DELETED}, http.OK


@api.route('/<bucket:bucket>/<keys:keys>', methods=['PUT'])
@jsonify
def put_by_keys_handler(bucket, keys):
    """ Update existing documents by keys.
        If document with any key doesn't exist then create it
    """
    if not len(keys):
        raise exceptions.InvalidRequestError('At least one key must be passed.')
    document = extract_form_data()
    force = is_force_mode()

    validate_document(document)

    #TODO: if there was only one document we should return proper http response and
    res = []
    http_status = http.OK
    for key in keys:
        filter_opts = {extf.KEY: key}

        if not storage.is_document_exists(get_app_id(), get_user_id(),
                                          bucket, filter_opts):
            if force:
                document[extf.KEY] = key
                storage.create(get_app_id(), get_user_id(), get_remote_ip(),
                               document, bucket=bucket)
                res.append({extf.KEY: key, STATUS_CODE: app.CREATED,
                        'message': resp_msgs.DOC_WAS_CREATED})
            else:
                res.append({extf.KEY: key, STATUS_CODE: app.NOT_FOUND,
                        'message': resp_msgs.DOC_NOT_EXISTS})
        else:
            storage.update(get_app_id(), get_user_id(), get_remote_ip(),
                           bucket, document, key=key)
            res.append({extf.KEY: key, STATUS_CODE: app.OK,
                        'message': resp_msgs.DOC_WAS_UPDATED})
    if len(res) == 1:
        res = res[0]
        if res[STATUS_CODE] == app.CREATED:
            http_status = http.CREATED
        elif res[STATUS_CODE] == app.NOT_FOUND:
            http_status = http.NOT_FOUND
        res = {'message': res['message']}
    else:
        res = {'response': res}

    return res, http_status


@api.route('/<bucket:bucket>', methods=['PUT'])
@jsonify
def put_by_filter_handler(bucket):
    """ Update existing filtered documents.
        If document doesn't match the filter then create it
    """
    document = extract_form_data()
    filter_opts = extract_filter_opts()
    force = is_force_mode()

    validate_document(document)
    validate_filter(filter_opts)

    if not storage.is_document_exists(get_app_id(), get_user_id(),
                                      bucket, filter_opts):
        if force:
            key = storage.create(
                get_app_id(), get_user_id(), get_remote_ip(), document, bucket=bucket
            )
            return {
                extf.KEY: key, 'message': resp_msgs.DOC_WAS_CREATED
            }, http.CREATED

        else:
            return {
                'message': resp_msgs.DOC_NOT_EXISTS
            }, http.NOT_FOUND

    storage.update(get_app_id(), get_user_id(), get_remote_ip(),
                             bucket, document, filter_opts=filter_opts)

    return {'message': resp_msgs.DOC_WAS_UPDATED}, http.OK


@api.errorhandler(Exception)
@jsonify
def app_exception(error):
    """ Return response as a error """

    error_class = error.__class__

    if error_class in ERROR_INFO_MATCHING:
        message = error.message
    else:
        message = resp_msgs.INTERNAL_ERROR
        LOG.debug(error.message)
        
    app_code, http_code = ERROR_INFO_MATCHING.get(
        error_class, (app.SERVER_ERROR, http.SERVER_ERROR))

    return {'message': message}, http_code


def validate_document(document):
    if not document:
        return

    valid1 = RecursiveValidator(document, forbidden_fields.values())
    valid2 = SimpleValidator(document, intf.values(), valid1)
    valid2.validate()

def validate_filter(filter):
    #TODO: re-implement this function in right way
    if not filter:
        return
    validate_document(filter)

def get_user_id():
    return guard.current_user.id


def get_app_id():
    return guard.current_app.id


def get_remote_ip():
    request.get('remote_addr', None)


def from_json(obj):
    try:
        res = json.loads(obj)
        if type(res) not in (dict, list):
            raise Exception()
        return res
    except Exception:
        raise exceptions.InvalidJSONFormatError("Invalid json object \"%s\"" % obj)


def extract_form_data():
    """
    Extracts form data when was passed json data in the HTTP headers
    """
    if request.json:
        obj = request.json
    else:
        obj = json.loads(request.data)
    return obj


def extract_filter_opts():
    """
    Extracts filter data from the url
    """
    filter_opts = request.args.get('filter', None)
    if filter_opts is not None:
        filter_opts = filter_opts.strip()
        filter_opts = from_json(filter_opts)
        if not len(filter_opts):
            raise exceptions.InvalidRequestError(
                'Invalid request syntax. Filter options were not specified')

    return filter_opts


def is_force_mode():
    force = False
    if request.args.get('force', '').strip() == 'true':
        force = True
    return force

def extract_pagination_data():
    """
        Extracts pagination data
    """
    skip = request.args.get('skip', 0)
    limit = request.args.get('limit', current_app.config.get('DEFAULT_QUERY_LIMIT', 1000))
    try:
        skip = int(skip)
        limit  = int(limit)
        if limit <= 0 or skip < 0:
            raise Exception()
    except Exception:
        raise exceptions.InvalidRequestError(
            'Invalid request syntax. Parameters skip or limit have invalid value.')

    return skip, limit


