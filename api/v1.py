import json
import datetime
from flask import Blueprint, jsonify
from flask.globals import request
from functools import wraps
from ds import storage
from ds.storage import ext_fields
import errors
from extensions import guard
from api.statuses import *

def get_user_id():
    return guard.current_user.id


def get_app_id():
    return guard.current_app.id


def get_remote_ip():
    request.get('remote_addr', None)


api = Blueprint("api_v1", __name__)

def from_json(obj):
    try:
        return json.loads(obj)
    except Exception:
        raise errors.JSONInvalidFormatError("Invalid json object [%s]" % obj)


def extract_form_data(f):
    @wraps(f)
    def decorator(bucket, key):
        obj = request.form['data']
        obj = from_json(obj)
        return f(bucket, key, obj)

    return decorator


@api.route('/<bucket>', methods=['GET'])
def get_many_handler(bucket):
    documents = storage.get_all(get_app_id(), get_user_id(), bucket)
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

    js = json.dumps({'response': documents}, default=dthandler)
    return js


@api.route('/<bucket>/<key>', methods=['GET'])
def get_one_handler(bucket, key=None):
    document = storage.find_by_key(get_app_id(), get_user_id(), key,
                                   bucket=bucket)
    if document is None:
        raise errors.DocumentNotFoundError(key=key, bucket=bucket)

    return jsonify({'response': [document]})


@api.route('/<bucket>', defaults={'key': None}, methods=['POST'])
@api.route('/<bucket>/<key>', methods=['POST'])
@extract_form_data
def post_handler(bucket, key, document):
    """ Create new document and get _key back
    """

    if key is not None:
        document[storage.ext_fields.KEY] = key

    return _save(bucket, document)


@api.route('/<bucket>/<key>', methods=['DELETE'])
def delete_one_handler(bucket, key):
    """ Deletes existing document (C.O.)
    """
    return _delete_one(bucket, key)


@api.route('/<bucket>', defaults={'key': None}, methods=['PUT'])
@api.route('/<bucket>/<key>', methods=['PUT'])
@extract_form_data
def put_handler(bucket, key, document):
    """ Update existing document
    """
    if key:
        document[ext_fields.KEY] = key
    # upsert
    if ext_fields.KEY not in document or not\
        _is_document_exists(bucket, document[ext_fields.KEY]):
        return _save(bucket, document)

    return _update(document, bucket)


def _save(bucket, document):
    # _save new entity and returns its key
    document_key = storage.create(
        get_app_id(), get_user_id(), get_remote_ip(), document, bucket=bucket
    )
    return jsonify({'response': {'key': document_key}})


def _delete_many(bucket, filter_opts=None):
    storage.delete_several(get_app_id(), get_user_id(), get_remote_ip(),
                           bucket=bucket)
    return jsonify({'response': app.OK})


def _delete_one(bucket, key):
    storage.delete_by_key(
        get_app_id(), get_user_id(), get_remote_ip(), key, bucket=bucket
    )
    return jsonify({'response': app.OK})


def _update(document, bucket):
    storage.update(
        get_app_id(), get_user_id(), get_remote_ip(), document, bucket=bucket
    )
    return jsonify({'response': app.OK})


def _is_document_exists(bucket, key):
    return storage.is_document_exists(get_app_id(), get_user_id(), key, bucket)


@api.errorhandler(errors.DocumentNotFoundError)
def not_found(error):
    """ Return response as a error json structure when document is not found by its key """
    message = ('Document with bucket [{bucket}] and '
               'key [{key}] was not found').format(bucket=error.bucket,
                                                   key=error.key)
    response_msg = json.dumps({'error': {'code': app.NOT_FOUND,
                                         'message': message}})
    return response_msg, http.NOT_FOUND


@api.errorhandler(errors.InvalidDocumentError)
@api.errorhandler(errors.InvalidDocumentKeyError)
def invalid_document(error):
    """ Return response with http's bad request code """
    response_msg = json.dumps({'error': {'code': app.BAD_REQUEST,
                                         'message': error.message}})
    return response_msg, http.BAD_REQUEST


@api.errorhandler(errors.InvalidAppIdError)
def invalid_app_id(error):
    """ Return response with http's bad request code """
    response_msg = json.dumps({'error': {'code': app.APP_UNAUTHORIZED,
                                         'message': error.message}})
    return response_msg, http.UNAUTHORIZED


@api.errorhandler(errors.InvalidUserIdError)
def invalid_user_id(error):
    """ Return response with http's bad request code """
    response_msg = json.dumps({'error': {'code': app.USER_UNAUTHORIZED,
                                         'message': error.message}})
    return response_msg, http.UNAUTHORIZED

