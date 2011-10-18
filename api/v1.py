import json
from flask import Blueprint, jsonify
from flask.globals import request
from functools import wraps
from db.crud import crud

api = Blueprint("api_v1", __name__)

def fromJSON(obj):
    return json.loads(obj)

def extract_form_data(f):
    @wraps(f)
    def decorator(bucket, id):
        obj = request.form['data']
        obj = fromJSON(obj)
        return f(bucket, id, obj)
    return decorator


@api.route('/<bucket>', defaults={'id': None}, methods=['GET'])
@api.route('/<bucket>/<id>', methods=['GET'])
def get(bucket, id=None):
    if id is None:
        objects = crud.get(bucket=bucket)
        return jsonify({bucket: objects})
    else:
        obj = crud.get(bucket=bucket, id=id)
        # obj may not be found
        return jsonify(obj)


@api.route('/<bucket>', defaults={'id': None}, methods=['POST'])
@api.route('/<bucket>/<id>', methods=['POST'])
@extract_form_data
def post(bucket, id, obj):
    res = crud.save(bucket=bucket, obj=obj, id=id)

    if res > 0:
        return jsonify({'response': res})
    elif res == -1:
        error_msg = 'Object of type [%s] couldn`t be saved due to some error.' % (bucket, id)
        return jsonify({'error': {'error_code': 1, 'error_msg': error_msg}})


@api.route('/<bucket>', methods=['DELETE'])
@api.route('/<bucket>/<id>', methods=['DELETE'])
def delete(bucket, id):
    id = int(id)
    res = crud.delete(bucket=bucket, id=id)
    if res == 0:
        return jsonify({'response': 0})
    elif res == 1:
        error_msg = 'Object of type [%s] with id [%d] couldn`t be deleted.' % (bucket, id)
        return jsonify({'error': {'error_code': 1, 'error_msg': error_msg}})


@api.route('/<bucket>', defaults={'id': None}, methods=['PUT'])
@api.route('/<bucket>/<id>', methods=['DELETE'])
@extract_form_data
def put(bucket, id, obj):
    if id is not None:
        res = crud.update(bucket=bucket, id=id, obj=obj)
    else:
        if obj['id'] is not None:
            res = crud.update(bucket=bucket, id=obj['id'], obj=obj)
        else:
            error_msg = 'Object of type [%s] couldn`t be updated due to no id specified.' % bucket
            return jsonify({'error': {'error_code': 1, 'error_msg': error_msg}})
    if res == 0:
        return jsonify({'response': 0})
    elif res == 1:
        error_msg = 'Object of type [%s] with id [%d] couldn`t be updated.' % (bucket, id)
        return jsonify({'error': {'error_code': 1, 'error_msg': error_msg}})


if __name__ == '__main__':
    api.run(debug=True, port=5001)
