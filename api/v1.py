import json
from flask import Blueprint, jsonify
from flask.globals import request
from functools import wraps
from ds import storage
from ds.storage import ext_fields
import errors
from extensions import guard
from api.statuses import *

def get_user_id():
    return guard.current_user_token

def get_app_id():
    return guard.current_app_token

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
    return jsonify({'response': documents})


@api.route('/<bucket>/<key>', methods=['GET'])
def get_one_handler(bucket, key=None):
    document = storage.find_by_key(get_app_id(), get_user_id(), key, bucket=bucket)
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
        document[storage.ext_fields.DOCUMENT_KEY] = key
        
    return save(bucket, document)


@api.route('/<bucket>/<key>', methods=['DELETE'])
def delete_one_handler(bucket, key):
    """ Deletes existing document (C.O.)
    """
    return _delete_by_key_func(bucket, key)


@api.route('/<bucket>', defaults={'key': None}, methods=['PUT'])
@api.route('/<bucket>/<key>', methods=['PUT'])
@extract_form_data
def put_handler(bucket, key, document):
    """ Update existing document
    """
    if key:
        document[ext_fields.DOCUMENT_KEY] = key
    if (ext_fields.DOCUMENT_KEY not in document or not
         _is_document_exists(bucket, document[ext_fields.DOCUMENT_KEY])):
        return save(bucket, document)

    return _update_func(document, bucket)



def save(bucket, document):
    # save new entity and returns its key
    document_key = storage.create(
        get_app_id(), get_user_id(), get_remote_ip(), document, bucket=bucket
    )
    return jsonify({'response': {'key': document_key}})


def _delete_several_func(bucket, filter_opts=None):
    storage.delete_several(get_app_id(), get_user_id(), get_remote_ip(), bucket=bucket)
    return jsonify({'response': app.OK})


def _delete_by_key_func(bucket, key):
    storage.delete_by_key(
        get_app_id(), get_user_id(), get_remote_ip(),  key, bucket=bucket
    )
    return jsonify({'response': app.OK})

def _update_func(document, bucket):
    storage.update(
        get_app_id(), get_user_id(), get_remote_ip(), document, bucket=bucket
    )
    return jsonify({'response': app.OK})

def _is_document_exists(bucket, key):
    
    return storage.is_document_exists(get_app_id(), get_user_id(), key, bucket)


@api.errorhandler(errors.DocumentNotFoundError)
def not_found(error):
    """ Return response as a error json structure when document is not found by its key """
    error_msg = 'Document with bucket [%s] and key [%s] is not found' % (error.bucket, error.key)
    response_msg = json.dumps({'error': {'error_code': app.NOT_FOUND,
                                         'error_msg': error_msg}})
    return response_msg, http.NOT_FOUND

@api.errorhandler(errors.InvalidDocumentError)
@api.errorhandler(errors.InvalidDocumentKeyError)
def invalid_document(error):
    """ Return response with http's bad request code """
    response_msg = json.dumps({'error': {'error_code': app.BAD_REQUEST,
                                         'error_msg': error.message}})
    return response_msg, http.BAD_REQUEST

@api.errorhandler(errors.InvalidAppIdError)
def invalid_app_id(error):
    """ Return response with http's bad request code """
    response_msg = json.dumps({'error': {'error_code': app.APP_UNAUTHORIZED,
                                         'error_msg': error.message}})
    return response_msg, http.UNAUTHORIZED

@api.errorhandler(errors.InvalidUserIdError)
def invalid_user_id(error):
    """ Return response with http's bad request code """
    response_msg = json.dumps({'error': {'error_code': app.USER_UNAUTHORIZED,
                                         'error_msg': error.message}})
    return response_msg, http.UNAUTHORIZED

