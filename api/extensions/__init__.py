__author__ = 'apetrovich'

from .guard import Guard
from .mongodb import FlaskMongodb

guard = Guard()
mongodb = FlaskMongodb()