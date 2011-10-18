import json
from flask import Blueprint, jsonify
from flask.globals import request
from flask.views import MethodView
from db.crud import crud
import appstorage as storage
from errors import EntryNotFoundError


ENTITY_DELETED = 2

api = Blueprint('api_v1', __name__)


def rate_limited(entityView):
    params = request.__dict__

def fromJSON(obj):
    return json.loads(obj)

class EntityView(MethodView):
  #  decorators = [rate_limited]
    
    def get(self, bucket, id):
        if id is None:
            objects = storage.all(bucket=bucket)
            return jsonify({bucket: objects})
        else:
            return jsonify(storage.get(bucket=bucket, key=id))

    def post(self, bucket, id=None):
        obj = request.form['data']
        obj = fromJSON(obj)
        try:
            res = storage.save(bucket=bucket, entry=obj, key=id)
            return jsonify({'response': res})
        except EntryNotFoundError as e:
            error_msg = 'Object of type [%s] with key %s couldn\'t be saved due to some error.' % (bucket, id)
            return jsonify({'error': {'error_code': 1, 'error_msg': error_msg}})


    def delete(self, bucket, id):
        try:
            res = crud.delete(bucket=bucket, id=id)
            return jsonify({'response': 0})
        except EntryNotFoundError as e:
            error_msg = 'Object of type [%s] with id [%d] couldn`t be deleted.' % (bucket, id)
            return jsonify({'error': {'error_code': 1, 'error_msg': error_msg}})

    def put(self, bucket, id):
        obj = request.form['data']
        obj = fromJSON(obj)
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
            

entity_view = EntityView.as_view('entity_view')
api.add_url_rule('/<bucket>/', defaults={'id': None},
                 view_func=entity_view, methods=['GET', 'PUT', 'POST'])

api.add_url_rule('/<bucket>/<int:id>', view_func=entity_view,
                 methods=['GET', 'DELETE'])


if __name__ == '__main__':
    api.run(debug=True, port=5001)
