from flask import Blueprint, jsonify
from flask.views import MethodView

from extensions import crud

api = Blueprint('api', __name__)


@api.route('/<bucket>', methods=['GET', 'POST'])
def resources(bucket=None):
    books = crud.all(bucket=bucket, page=1)
    return jsonify(**books)


@api.route('/<bucket>/<int:id>', methods=['GET', 'POST'])
def resource(bucket=None, id=None):
    return jsonify(crud.get(bucket = bucket, id=id))

