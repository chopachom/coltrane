__author__ = 'apetrovich'

from extensions.guard import Guard
from .mongodb import FlaskMongodb

guard = Guard()
mongodb = FlaskMongodb()