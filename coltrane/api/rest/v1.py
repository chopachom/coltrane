import json
import datetime
import logging
import traceback

from flask import Blueprint, current_app
from flask.globals import request
from coltrane.appstorage.storage import AppdataStorage
from coltrane.appstorage.storage import extf, intf
from coltrane.api.validators import SimpleValidator, RecursiveValidator
from coltrane.api.extensions import guard
from coltrane.api.extensions import mongodb
from coltrane.api.rest.statuses import *

from coltrane.config import RESTConfig

from coltrane.api import exceptions
from coltrane.utils import Enum



LOG = logging.getLogger('coltrane.api')
LOG.debug('starting coltrane api')

class resp_msgs(Enum):

    DOC_NOT_EXISTS  = "Document doesn't exist"
    DOC_WAS_CREATED = "Document was created"
    DOC_WAS_DELETED = "Document was deleted"
    DOC_WAS_UPDATED = "Document was updated"
    
    INTERNAL_ERROR  = "Server internal error"


class forbidden_fields(Enum):
    WHERE      = '$where'

class lazy_conn(object):
    class __metaclass__(type):
        conn = None
        @property
        def entities(self):
            if self.conn:
                return self.conn
            else:
                conf = current_app.config
                db   = conf['MONGODB_DATABASE']
                coll = conf['APPDATA_COLLECTION']
                self.conn = mongodb.connection[db][coll]
                return self.conn
        def __getattr__(self, name):
            return getattr(self.entities, name)


def jsonify(*args, **kwargs):
    DT_HANDLER = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
    return current_app.response_class(
        json.dumps(
            dict(*args, **kwargs),
            indent=None if request.is_xhr else 2,
            default=DT_HANDLER
        ),
        mimetype='application/json'
    )


api = Blueprint("api_v1", __name__)
storage = AppdataStorage(lazy_conn)



@api.route('/<bucket:bucket>', defaults={'key': None}, methods=['POST'])
@api.route('/<bucket:bucket>/<key>', methods=['POST'])
def post_handler(bucket, key):
    """ Create new document and get _key back
    """
    document = extract_form_data()
    validate_document(document)
    if key is not None:
        document[extf.KEY] = key
    document_key = storage.create(get_app_id(), get_user_id(), get_remote_ip(),
                                  document, bucket=bucket)
    res = json.dumps({extf.KEY: document_key})
    return make_response(res, http.CREATED)


@api.route('/<bucket:bucket>/<keys:keys>', methods=['GET'])
def get_by_keys_handler(bucket, keys):
    if not len(keys):
            raise errors.InvalidRequestError('At least one key must be passed.')
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

    res = json.dumps(res, default=DT_HANDLER)
    return make_response(res, http_status)



@api.route('/<bucket:bucket>', methods=['GET'])
def get_by_filter_handler(bucket):
    filter_opts = extract_filter_opts()
    validate_filter(filter_opts)

    skip, limit = extract_pagination_data()

    documents = storage.find(get_app_id(), get_user_id(), bucket,
                             filter_opts, skip, limit)

    if len(documents):
        res = json.dumps(documents, default=DT_HANDLER)
        return make_response(res, http.OK)
    
    res = json.dumps({'message': resp_msgs.DOC_NOT_EXISTS})
    return make_response(res, http.NOT_FOUND)



@api.route('/<bucket:bucket>/<keys:keys>', methods=['DELETE'])
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

    return make_response(json.dumps(res), http_status)


@api.route('/<bucket:bucket>', methods=['DELETE'])
def delete_by_filter_handler(bucket):
    """ Delete all documents matched with filter
    """
    filter_opts = extract_filter_opts()
    validate_filter(filter_opts)
    if not storage.is_document_exists(get_app_id(), get_user_id(),
                                      bucket, filter_opts):
        res = json.dumps({'message': resp_msgs.DOC_NOT_EXISTS})
        return make_response(res, http.NOT_FOUND)
    
    storage.delete(get_app_id(), get_user_id(), get_remote_ip(),
                   bucket=bucket, filter_opts=filter_opts)

    res = json.dumps({'message': resp_msgs.DOC_WAS_DELETED})
    return make_response(res, http.OK)


@api.route('/<bucket:bucket>/<keys:keys>', methods=['PUT'])
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

    response_msg = json.dumps(res)
    return make_response(response_msg, http_status)


@api.route('/<bucket:bucket>', methods=['PUT'])
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
            res = json.dumps({
                    extf.KEY: key, 'message': resp_msgs.DOC_WAS_CREATED
                })
            return make_response(res, http.CREATED)
        else:
            res = json.dumps({
                'message': resp_msgs.DOC_NOT_EXISTS
            })
            return make_response(res, http.NOT_FOUND)

    storage.update(get_app_id(), get_user_id(), get_remote_ip(),
                             bucket, document, filter_opts=filter_opts)

    res = json.dumps({'message': resp_msgs.DOC_WAS_UPDATED})
    return make_response(res, http.OK)


@api.errorhandler(Exception)
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
    
    response_msg = json.dumps({'message': message})
    return make_response(response_msg, http_code)


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
    obj = request.form['data']
    obj = from_json(obj)
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
            raise exceptions.InvalidRequestError('Invalid request syntax. '  \
                                             'Filter options were not specified')

    return filter_opts


def is_force_mode():
    force = request.args.get('force', None)
    if force is None:
        force = False
    else:
        force = force.strip()
        if force == 'true':
            force = True
        else:
            force = False
    return force

def extract_pagination_data():

    """
        Extracts pagination data
    """
    skip = request.args.get('skip', 0)
    limit = request.args.get('limit', RESTConfig.PAGE_QUERY_SIZE)
    try:
        skip = int(skip)
        limit  = int(limit)
        if limit <= 0 or skip < 0:
            raise Exception()
    except Exception:
        raise errors.InvalidRequestError('Invalid request syntax. '  \
                'Parameters skip or limit have invalid value.')

    return skip, limit


