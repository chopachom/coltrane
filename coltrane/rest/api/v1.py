import logging
from flask import Blueprint
from coltrane.appstorage import reservedf, forbidden_fields
from coltrane.appstorage.storage import AppdataStorage
from coltrane.appstorage.storage import extf
from coltrane.rest.api.datatypes import serialize, deserialize
from coltrane.rest.extensions import guard
from coltrane.rest import exceptions, validators, http_status, STATUS_CODE, app_status
from coltrane.rest.utils import *


LOG = logging.getLogger('coltrane.rest.api.v1')
LOG.debug('starting rest api')


storage = AppdataStorage(lazy_coll)
api = Blueprint("api_v1", __name__)


@api.route('/<bucket:bucket>/<key:key>', methods=['GET'])
@jsonify
@serialize
def get_by_keys_handler(bucket, key):

    doc = storage.get(get_app_id(), get_user_id(), bucket, key)
    if doc:
        return doc, http_status.OK
    else:
        return {STATUS_CODE: app_status.NOT_FOUND,
                'message': resp_msgs.DOC_NOT_EXISTS}, http_status.NOT_FOUND


@api.route('/<bucket:bucket>', methods=['GET'])
@jsonify
@serialize
def get_by_filter_handler(bucket):

    filter_opts = extract_filter_opts()
    skip, limit = extract_pagination_data()
    count = extract_counting_data() # count flag
    count_only = count
    # if limit greater then 0 it means that documents have to be returned as well as count parameter
    if limit:
        count_only = False

    response = storage.find(get_app_id(), get_user_id(), bucket,
                             filter_opts, skip, limit, count_only)
    if count_only:
        return {'response': [], 'count': response}, http_status.OK
    else:
        if len(response):
            resp = {'response': response}
            if count:
                resp.update({'count': len(response)})
            return resp, http_status.OK

        return {'message': resp_msgs.DOC_NOT_EXISTS,
                STATUS_CODE: app_status.NOT_FOUND}, http_status.NOT_FOUND


@api.route('/<bucket:bucket>', defaults={'key': None}, methods=['POST'])
@api.route('/<bucket:bucket>/<key:key>', methods=['POST'])
@jsonify
@serialize
def post_handler(bucket, key):
    """ Create new document and get _key back
    """
    document = extract_form_data()

    if key:
        document[extf.KEY] = key
    else:
        key = document.get(extf.KEY, None)

    if extf.KEY in document:
        if storage.is_document_exists(get_app_id(), get_user_id(),
                        bucket, {extf.KEY: key}):
            raise exceptions.DocumentAlreadyExistsError(
                key=key,
                bucket=bucket)

    document_key = storage.create(get_app_id(), get_user_id(), bucket, get_remote_ip(),
                                  document)
    return {extf.KEY: document_key}, http_status.CREATED


@api.route('/<bucket:bucket>/<key:key>', methods=['PUT'])
@jsonify
@serialize
def put_by_keys_handler(bucket, key):
    """ Update existing documents by keys.
        If document with any key doesn't exist then create it
    """
    document = extract_form_data()
    force = is_force_mode()

    filter_opts = {extf.KEY: key}

    if not storage.is_document_exists(get_app_id(), get_user_id(),
        bucket, filter_opts):
        if force:
            document[extf.KEY] = key
            document = generate_normal_view(document)
            storage.create(get_app_id(), get_user_id(), bucket, get_remote_ip(),
                document)
            return {extf.KEY: key}, http_status.CREATED
        else:
            return {STATUS_CODE: app_status.NOT_FOUND,
                    'message': resp_msgs.DOC_NOT_EXISTS}, http_status.NOT_FOUND
    else:
        storage.update(get_app_id(), get_user_id(), bucket, get_remote_ip(),
            document, key=key)
        return {STATUS_CODE: app_status.OK,
                'message': resp_msgs.DOC_UPDATED}, http_status.OK


@api.route('/<bucket:bucket>', methods=['PUT'])
@jsonify
@serialize
def put_by_filter_handler(bucket):
    """ Update existing filtered documents.
        If document doesn't match the filter then create it
    """
    document = extract_form_data()
    filter_opts = extract_filter_opts()
    force = is_force_mode()

    if not storage.is_document_exists(get_app_id(), get_user_id(),
                                      bucket, filter_opts):
        if force:
            document = generate_normal_view(document)

            key = storage.create(
                get_app_id(), get_user_id(),  bucket, get_remote_ip(), document
            )
            return {
                extf.KEY: key, 'message': resp_msgs.DOC_CREATED,
                STATUS_CODE: app_status.CREATED
            }, http_status.CREATED

        else:
            return {
                'message': resp_msgs.DOC_NOT_EXISTS,
                STATUS_CODE: app_status.NOT_FOUND
            }, http_status.NOT_FOUND

    storage.update(get_app_id(), get_user_id(), bucket, get_remote_ip(),
                   document, filter_opts=filter_opts)

    return {'message': resp_msgs.DOC_UPDATED, STATUS_CODE: app_status.OK}, http_status.OK


@api.route('/<bucket:bucket>/<key:key>', methods=['DELETE'])
@jsonify
@serialize
def delete_by_keys_handler(bucket, key):
    """ Deletes existing document (C.O.)
    """
    filter_opts = {extf.KEY: key}
    if not storage.is_document_exists(get_app_id(), get_user_id(),
        bucket, filter_opts):
        return {STATUS_CODE: app_status.NOT_FOUND,
                'message': resp_msgs.DOC_NOT_EXISTS}, http_status.NOT_FOUND
    else:
        storage.delete(get_app_id(), get_user_id(), bucket, get_remote_ip(),
            filter_opts=filter_opts)
        return {STATUS_CODE: app_status.OK,
                'message': resp_msgs.DOC_DELETED}, http_status.OK


@api.route('/<bucket:bucket>', methods=['DELETE'])
@jsonify
@serialize
def delete_by_filter_handler(bucket):
    """ Delete all documents matched with filter
    """
    filter_opts = extract_filter_opts()
    if not storage.is_document_exists(get_app_id(), get_user_id(),
                                      bucket, filter_opts):
        return {'message': resp_msgs.DOC_NOT_EXISTS,
                STATUS_CODE: app_status.NOT_FOUND}, http_status.NOT_FOUND
    
    storage.delete(get_app_id(), get_user_id(), bucket, get_remote_ip(),
                    filter_opts=filter_opts)

    return {'message': resp_msgs.DOC_DELETED}, http_status.OK



def validate_forbidden_fields(doc, fields=None):
    if not fields:
        fields = forbidden_fields.values()
    valid1 = validators.RecursiveValidator(doc, fields)
    valid1.validate()

    
def validate_document(document):
    fields = forbidden_fields.values() + reservedf.values()
    validate_forbidden_fields(document, fields)
    validators.SaveDocumentKeysValidator(document).validate()


def validate_filter(filter):
    validate_forbidden_fields(filter)
    validators.FilterKeysValidator(filter).validate()


def validate_doc_for_update(update_doc):
    fields = forbidden_fields.values() + extf.values() + reservedf.values()
    validate_forbidden_fields(update_doc, fields)
    validators.UpdateDocumentKeysValidator(update_doc).validate()

    
def generate_normal_view(document):
    """
        {'a.b.c.d':1} => {'a':{'b':{'c':{'d':1}}}}
    """
    doc = {}
    for k in document:
        keys = k.split('.')

        v = document[k]
        for k2 in keys[:0:-1]: # [1,2,3,4] => [4,3,2]
            v = {k2: v}
        doc[keys[0]] = v
    return doc


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
    elif request.data:
        obj = from_json(request.data)
    else:
        #FIXME: DIRTY DIRTY DIRTY SUCKER
        obj = from_json(request.form.keys()[0])

    document = deserialize(obj)

    if request.method == 'POST':
        validate_document(obj)
    elif request.method == 'PUT':
        normal_view = generate_normal_view(obj)
        validate_doc_for_update(normal_view)
    
    return document


def extract_filter_opts():
    """
    Extracts filter data from the url
    """
    filter = request.args.get('filter', None)
    if filter is not None:
        filter = filter.strip()
        filter = from_json(filter)
        if not len(filter):
            raise exceptions.InvalidRequestError(
                'Invalid request syntax. Filter options were not specified')
        normal_view = generate_normal_view(filter)
        validate_filter(normal_view)
        filter = deserialize(filter)
    return filter


def is_force_mode():
    force = False
    if request.args.get('force', '').strip() == 'true':
        force = True
    return force


def extract_counting_data():
    """Extract count flag. If it has true value it means that count
    parameter should be added to the response."""
    count = False
    if request.args.get('count', '').strip() == 'true':
        count = True
    return count


def extract_pagination_data():
    """
        Extracts pagination data
    """
    skip = request.args.get('skip', 0)
    limit = request.args.get('limit', current_app.config.get('DEFAULT_QUERY_LIMIT', 1000))
    try:
        skip = int(skip)
        limit  = int(limit)
        if limit < 0 or skip < 0:
            raise Exception()
    except Exception:
        raise exceptions.InvalidRequestError(
            'Invalid request syntax. Parameters skip or limit have invalid value.')

    return skip, limit


def get_user_id():
    return str(guard.current_user.id)


def get_app_id():
    return str(guard.current_app.id)


def get_remote_ip():
    return request.remote_addr


