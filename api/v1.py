import json
from flask import Blueprint, jsonify
from flask.globals import request
from functools import wraps
from ds import storage
from extensions.guard import guard
from errors import *

RESPONSE_OK = 0

def get_user_id():
    return guard.current_user_token


def get_app_id():
    return guard.current_app_token

def get_remote_ip():
    request.get('remote_addr', None)


api = Blueprint("api_v1", __name__)

def fromJSON(obj):
    return json.loads(obj)

def extract_form_data(f):
    @wraps(f)
    def decorator(bucket, key):
        obj = request.form['data']
        obj = fromJSON(obj)
        return f(bucket, key, obj)
    return decorator


@api.route('/<bucket>', defaults={'key': None}, methods=['GET'])
@api.route('/<bucket>/<key>', methods=['GET'])
def get(bucket, key=None):
    if key is None:
        documents = storage.find_all(get_app_id(), get_user_id(), bucket)
        return jsonify({'response': documents})
    else:
        document = storage.read(get_app_id(), get_user_id(), key, bucket=bucket)
        if document is None:
            raise EntryNotFoundError(key=key, bucket=bucket)

        return jsonify({'response': [document]})


@api.route('/<bucket>', defaults={'key': None}, methods=['POST'])
@api.route('/<bucket>/<key>', methods=['POST'])
@extract_form_data
def post(bucket, key, document):
    """ Create new document and get _key back
    """
    if key is not None:
        document[storage.ext.DOCUMENT_KEY] = key

    # save new entity and returns its key
    document_key = storage.create(
        get_app_id(), get_user_id(), get_remote_ip(), document, bucket=bucket
    )
    return jsonify({'response': {'key': document_key}})


@api.route('/<bucket>/delete_all', methods=['DELETE'])
def delete(bucket, key=None):
    """ Deletes all existing documents of the specified bucket
    """
    storage.delete_all(get_app_id(), get_user_id(), get_remote_ip(), bucket=bucket)
    return jsonify({'response': RESPONSE_OK})


@api.route('/<bucket>/<key>', methods=['DELETE'])
def delete(bucket, key=None):
    """ Deletes existing document (C.O.)
    """
    storage.delete(
        get_app_id(), get_user_id(), get_remote_ip(),  key, bucket=bucket
    )
    return jsonify({'response': {'key': key}})


@api.route('/<bucket>', defaults={'key': None}, methods=['PUT'])
@api.route('/<bucket>/<key>', methods=['PUT'])
@extract_form_data
def put(bucket, key, document):
    """ Update existing document
    """
    if key is not None:
        document[storage.ext.DOCUMENT_KEY] = key
        storage.update(
            get_app_id(), get_user_id(), get_remote_ip(), document, bucket=bucket
        )
    else:
        raise EntryNotFoundError(key=key, bucket=bucket)
    
    return jsonify({'response': {'key': key}})



@api.errorhandler(EntryNotFoundError)
@api.errorhandler(InvalidDocumentKeyError)
def not_found(error):
    error_msg = 'Document with bucket [%s] and key [%s] is not found' % (error.bucket, error.key)
    return jsonify({
        'error': {'error_code': 0, 'error_msg': error_msg}
    }),   404


@api.errorhandler(InvalidDocumentError)
def invalid_document():
    """ Return response with http's bad request code """
    return jsonify({'error': 'Invalid document'}), 400
