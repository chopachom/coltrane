from flask import Blueprint, jsonify
from flask.views import MethodView

from extensions import crud

api = Blueprint('api', __name__)


books = { 'books': [
    {'id':1, 'title': 'Vse o huyah', 'author': 'Nikita Shmakov'},
    {'id':2, 'title': 'Vse o pezdah', 'author': 'Nikita Shmakov'}
]}



@api.route("/")
@api.route('/<bucket>', methods=['GET', 'POST'])
def resources(bucket=None):
    books = crud.all(page=1)
    return jsonify(**books)


@api.route('/<bucket>/<int:id>', methods=['GET', 'POST'])
def resource(bucket=None, id=None):
    return jsonify(crud.get(bucket = bucket, id=id))


if __name__ == '__main__':
    api.run(debug=True, port=5001)
