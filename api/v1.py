import json
from flask import Blueprint, jsonify
from flask.globals import request
from functools import wraps
from ds import storage
from extensions.guard import guard
from errors import *

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


@api.route('/<bucket>', defaults={'id': None}, methods=['GET'])
@api.route('/<bucket>/<id>', methods=['GET'])
def get(bucket, id=None):
    if id is None:
        # get all is not implemented yet
        #objects = storage.get(bucket=bucket)
        #return jsonify({bucket: objects})
        pass
    else:
        document = storage.read(get_app_id(), get_user_id(), id, bucket=bucket)
        # document may not be found
        return jsonify(document)


@api.route('/<bucket>', defaults={'id': None}, methods=['POST'])
@api.route('/<bucket>/<id>', methods=['POST'])
@extract_form_data
def post(bucket, id, document):
    """ Create new document and get _key back
    """
    if id is not None:
        document[storage.ext.DOCUMENT_ID] = id
    res = storage.create(
        get_app_id(), get_user_id(), get_remote_ip(), document, bucket=bucket
    )
    return jsonify({'response': res})


@api.route('/<bucket>', defaults={'id': None}, methods=['DELETE'])
@api.route('/<bucket>/<id>', methods=['DELETE'])
def delete(bucket, id=None):
    """ Deletes existing document (C.O.)
    """
    storage.delete(
        get_app_id(), get_user_id(), get_remote_ip(),  id, bucket=bucket
    )
    return jsonify({'deleted': id})


@api.route('/<bucket>', defaults={'id': None}, methods=['PUT'])
@api.route('/<bucket>/<id>', methods=['PUT'])
@extract_form_data
def put(bucket, id, document):
    """ Update existing document
    """
    if id is not None:
        document[storage.ext.DOCUMENT_ID] = id

    if document[storage.ext.DOCUMENT_ID] is not None:
        storage.update(
            get_app_id(), get_user_id(), get_remote_ip(), document, bucket=bucket
        )
    else:
        raise EntryNotFoundError(id=id, bucket=bucket)
    
    return jsonify({'updated': id})



@api.errorhandler(EntryNotFoundError)
@api.errorhandler(InvalidDocumentIdError)
def not_found(error):
    return jsonify({
        'error': 'Document with id {id} not found'.format (id=error.id)
    }),   404


@api.errorhandler(InvalidDocumentError)
def invalid_document():
    """ Return response with http's bad request code """
    return jsonify({'error': 'Invalid document'}), 400
