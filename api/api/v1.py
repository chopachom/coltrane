from flask import Blueprint, jsonify

api_v1 = Blueprint('api', __name__)


@api_v1.route('/<bucket>', methods=['GET', 'POST'])
def resources(bucket=None):
    books = crud.all(bucket=bucket, page=1)
    return jsonify(**books)


@api_v1.route('/<bucket>/<int:id>', methods=['GET', 'POST'])
def resource(bucket=None, id=None):
    return jsonify(crud.get(bucket = bucket, id=id))

