import json
from flask import Blueprint, jsonify
from flask.globals import request
from functools import wraps
from ds import storage

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
        objects = crud.get(bucket=bucket)
        return jsonify({bucket: objects})
    else:
        obj = crud.get(bucket=bucket, key=key)
        # obj may not be found
        return jsonify(obj)


@api.route('/<bucket>', defaults={'key': None}, methods=['POST'])
@api.route('/<bucket>/<key>', methods=['POST'])
@extract_form_data
def post(bucket, key, obj):
    res = crud.save(bucket=bucket, obj=obj, key=key)

    if res > 0:
        return jsonify({'response': res})
    elif res == -1:
        error_msg = "Object of type [%s] couldn't be saved due to some error." % bucket
        return jsonify({'error': {'error_code': 1, 'error_msg': error_msg}})


@api.route('/<bucket>', defaults={'key': None}, methods=['DELETE'])
@api.route('/<bucket>/<key>', methods=['DELETE'])
def delete(bucket, key=None):
    key = int(key)
    res = crud.delete(bucket=bucket, key=key)
    if res == 0:
        return jsonify({'response': 0})
    elif res == 1:
        error_msg = "Object of type [%s] with key [%d] couldn't be deleted." % (bucket, key)
        return jsonify({'error': {'error_code': 1, 'error_msg': error_msg}})


@api.route('/<bucket>', defaults={'key': None}, methods=['PUT'])
@api.route('/<bucket>/<key>', methods=['PUT'])
@extract_form_data
def put(bucket, key, obj):
    if key is not None:
        res = crud.update(bucket=bucket, key=key, obj=obj)
    else:
        if obj['key'] is not None:
            res = crud.update(bucket=bucket, key=obj['key'], obj=obj)
        else:
            error_msg = "Object of type [%s] couldn't be updated due to no key specified." % bucket
            return jsonify({'error': {'error_code': 1, 'error_msg': error_msg}})
    if res == 0:
        return jsonify({'response': 0})
    elif res == 1:
        error_msg = "Object of type [%s] with key [%d] couldn't be updated." % (bucket, key)
        return jsonify({'error': {'error_code': 1, 'error_msg': error_msg}})
