from flask import Blueprint, jsonify
import appstorage

api_v1 = Blueprint('api', __name__)


@api_v1.route('/<bucket>', methods=['GET', 'POST'])
def resources(bucket=None):
    books = appstorage.all(bucket=bucket)
    return jsonify(**books)


@api_v1.route('/<bucket>/<int:id>', methods=['GET', 'POST'])
def resource(bucket=None, id=None):
    return jsonify(appstorage.get(bucket = bucket, id=id))

