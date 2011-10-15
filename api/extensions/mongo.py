__author__ = 'qweqwe'
from flask import _request_ctx_stack
from flaskext.mongokit import MongoKit

class MongoKitConnection(MongoKit):
    @property
    def connection(self):
        if self.connected:
            ctx = _request_ctx_stack.top
            return ctx.mongokit_connection