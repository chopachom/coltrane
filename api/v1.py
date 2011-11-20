import json
import datetime
from flask import Blueprint, jsonify
from flask.globals import request
from ds import storage
from ds.storage import ext_fields, int_fields
import errors
from extensions import guard
from api.statuses import *

DT_HANDLER = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

api = Blueprint("api_v1", __name__)


@api.route('/<bucket>', defaults={'key': None}, methods=['POST'])
@api.route('/<bucket>/<key>', methods=['POST'])
def post_handler(bucket, key):
    """ Create new document and get _key back
    """
    document = extract_form_data()

    validate_document(document)

    if key is not None:
        document[storage.ext_fields.KEY] = key


    document_key = storage.create(get_app_id(), get_user_id(), get_remote_ip(), document, bucket=bucket)
    return jsonify({'response': {'key': document_key}})


@api.route('/<bucket>/<keys:keys>', methods=['GET'])
def get_by_keys_handler(bucket, keys):
    documents = []

    if not len(keys):
            raise errors.InvalidRequestError('At least one key must be passed.')
    
    for key in keys:
        doc = storage.get_by_key(get_app_id(), get_user_id(),
                                   bucket, key)
        if doc:
            documents.append(doc)

    res = json.dumps({'response': documents}, default=DT_HANDLER)
    return res


@api.route('/<bucket>', methods=['GET'])
def get_by_filter_handler(bucket):
    filter_opts = extract_filter_opts()
    documents = storage.get_by_filter(get_app_id(), get_user_id(), bucket, filter_opts)

    res = json.dumps({'response': documents}, default=DT_HANDLER)
    return res


@api.route('/<bucket>/<keys:keys>', methods=['DELETE'])
def delete_by_keys_handler(bucket, keys):
    """ Deletes existing document (C.O.)
    """
    if not len(keys):
            raise errors.InvalidRequestError('At least one key must be passed.')
    res = []
    for key in keys:
        filter_opts = {ext_fields.KEY: key}
        if not storage.is_document_exists(get_app_id(), get_user_id(), bucket, filter_opts):
            res.append({key: app.NOT_FOUND})
        else:
            storage.delete_by_filter(get_app_id(), get_user_id(), get_remote_ip(),
                           bucket=bucket, filter_opts=filter_opts)
            res.append({key: app.OK})
    return jsonify({'response': res})


@api.route('/<bucket>', methods=['DELETE'])
def delete_by_filter_handler(bucket):
    """ Delete all matched with filter documents.
    """
    filter_opts = extract_filter_opts()
    if not storage.is_document_exists(get_app_id(), get_user_id(), bucket, filter_opts):
        return jsonify({'response': app.NOT_FOUND})

    storage.delete_by_filter(get_app_id(), get_user_id(), get_remote_ip(),
                           bucket=bucket, filter_opts=filter_opts)
    return jsonify({'response': app.OK})


@api.route('/<bucket>/<keys:keys>', methods=['PUT'])
def put_by_keys_handler(bucket, keys):
    """ Update existing documents by keys.
    If document with any key doesn't exist then create it
    """
    if not len(keys):
            raise errors.InvalidRequestError('At least one key must be passed.')
    document = extract_form_data()
    force = is_force_mode()

    validate_document(document)

    res = []
    for key in keys:
        filter_opts = {ext_fields.KEY: key}

        if not storage.is_document_exists(get_app_id(), get_user_id(), bucket, filter_opts):
            if force:
                document[ext_fields.KEY] = key
                storage.create(get_app_id(), get_user_id(), get_remote_ip(), document, bucket=bucket)
            res.append({key: app.NOT_FOUND})
        else:
            storage.update_by_key(get_app_id(), get_user_id(), get_remote_ip(),
                            bucket, document, key)
            res.append({key: app.OK})
    return jsonify({'response': res})


@api.route('/<bucket>', methods=['PUT'])
def put_by_filter_handler(bucket):
    """ Update existing filtered documents.
    If document doesn't match filter then create it
    """
    document = extract_form_data()
    filter_opts = extract_filter_opts()
    force = is_force_mode()

    validate_document(document)

    if not storage.is_document_exists(get_app_id(), get_user_id(), bucket, filter_opts):
        if force:
            key = storage.create(get_app_id(), get_user_id(), get_remote_ip(), document, bucket=bucket)
            return jsonify({'response': {ext_fields.KEY: key, STATUS_CODE: app.NOT_FOUND}})
        else:
            return jsonify({'response': {STATUS_CODE: app.NOT_FOUND}})

    storage.update_by_filter(get_app_id(), get_user_id(), get_remote_ip(),
                        bucket, document, filter_opts)
    return jsonify({'response': {STATUS_CODE: app.OK}})


@api.errorhandler(errors.DocumentNotFoundError)
def not_found(error):
    """ Return response as a error json structure when document is not found by its key """

    message = error.message
    response_msg = json.dumps({'error': {STATUS_CODE: app.NOT_FOUND,
                                         'message': message}})
    return response_msg, http.NOT_FOUND


@api.errorhandler(errors.InvalidDocumentError)
@api.errorhandler(errors.InvalidDocumentKeyError)
def invalid_document(error):
    """ Return response with http's bad request code """
    response_msg = json.dumps({'error': {STATUS_CODE: app.BAD_REQUEST,
                                         'message': error.message}})
    return response_msg, http.BAD_REQUEST


@api.errorhandler(errors.InvalidAppIdError)
def invalid_app_id(error):
    """ Return response with http's bad request code """
    response_msg = json.dumps({'error': {STATUS_CODE: app.APP_UNAUTHORIZED,
                                         'message': error.message}})
    return response_msg, http.UNAUTHORIZED


@api.errorhandler(errors.InvalidUserIdError)
def invalid_user_id(error):
    """ Return response with http's bad request code """
    response_msg = json.dumps({'error': {STATUS_CODE: app.USER_UNAUTHORIZED,
                                         'message': error.message}})
    return response_msg, http.UNAUTHORIZED


@api.errorhandler(errors.InvalidJSONFormatError)
def invalid_json_format(error):
    """ Return response with http's bad request code """
    response_msg = json.dumps({'error': {STATUS_CODE: app.BAD_REQUEST,
                                         'message': error.message}})
    return response_msg, http.BAD_REQUEST


@api.errorhandler(errors.InvalidRequestError)
def invalid_json_format(error):
    """ Return response with http's bad request code """
    response_msg = json.dumps({'error': {STATUS_CODE: app.BAD_REQUEST,
                                         'message': error.message}})
    return response_msg, http.BAD_REQUEST


def validate_document(document):
    # assert that document not contains forbidden fields
    fields = [key for key in document if key in int_fields.values()]
    if len(fields):
        raise errors.InvalidDocumentError(
            errors.InvalidDocumentError.FORBIDDEN_FIELDS_MSG % ','.join(fields))

def validate_filter(filter):
    "TODO: re-implement this function in right way"
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
        if type(res) is not dict:
            raise Exception()
        return res
    except Exception:
        raise errors.InvalidJSONFormatError("Invalid json object \"%s\"" % obj)


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
        validate_filter(filter_opts)
        if not len(filter_opts):
            raise errors.InvalidRequestError('Invalid request syntax. There is no filters opts.')

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

