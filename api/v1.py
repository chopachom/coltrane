import json
from flask import Blueprint, jsonify
from flask.globals import request
from flask.templating import render_template
from flask.views import MethodView, View
from db.crud import crud

#ENTUTY_DELETED = jsonify({'status':1, 'message':'Entity has been deleted'})
ENTUTY_DELETED = 2

api = Blueprint('service', __name__)

#class UserAPI(MethodView):
#
#    def get(self):
#        users = User.query.all()
#
#    def post(self):
#        user = User.from_form_data(request.form)

def rate_limited(entityView):
    params = request.__dict__

def fromJSON(obj):
    return json.loads(obj)

class EntityView(MethodView):
  #  decorators = [rate_limited]
    
    def get(self, bucket, id):
        if id is None:
            objects = crud.get(bucket=bucket)
            return jsonify({bucket: objects})
        else:
            return jsonify(crud.get(bucket=bucket, id=id))

    def post(self, bucket, id=None):
        obj = request.form['data']
        obj = fromJSON(obj)
        res = crud.save(bucket=bucket, obj=obj, id=id)

        if res > 0:
            return jsonify({'response': res})
        elif res == -1:
            error_msg = 'Object of type [%s] couldn`t be saved due to some error.' % (bucket, id)
            return jsonify({'error': {'error_code': 1, 'error_msg': error_msg}})


    def delete(self, bucket, id):
        res = crud.delete(bucket=bucket, id=id)
        if res == 0:
            return jsonify({'response': 0})
        elif res == 1:
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

#@api.route('/<bucket>/', methods=['GET', 'POST'])
#def resources(bucket=None):
#    books = crud.all(page=1)
#    return jsonify(**books)
#
#
#@api.route('/<bucket>/<int:id>', methods=['GET', 'PUT', 'DELETE'])
#def resource(bucket=None, id=None):
#    return jsonify(crud.get(bucket = bucket, id=id))


if __name__ == '__main__':
    api.run(debug=True, port=5001)
