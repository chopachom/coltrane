__author__ = 'qweqwe'
import unittest
import os
from api.app import create_app
from api import api_v1
from api.rest.v1 import from_json
from api.lib.guard_manager import GuardManager
from api.extensions import guard
from api.config import TestConfig
from db.models import User, AppToken
from db.extension import db


guard.manager = GuardManager

class GuardTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        api_v1.get_app_id = lambda : 'app_id1'
        api_v1.get_remote_ip = lambda : '127.0.0.1'
        api_v1.get_user_id = lambda : 'user_id1'
        app = create_app(
            modules=((api_v1, '/v1'),),
            exts=(guard, db),
            config=TestConfig
        )
        cls.app = app.test_client()
        db.session.begin_transaction()


    def test_allow_access(self):
        rv = self.app.get('/v1/books')
        res = from_json(rv.data)
        assert res == {'response': []}

    def test_deny_access_for_auth_token(self):
        res = self.app.get('/v1/books')
        assert res._status_code == 401


    def test_deny_access_for_app_token(self):
        res = self.app.get('/v1/books')
        assert res._status_code == 401

    @classmethod
    def tearDownClass(cls):
        db.session.rollback()



if __name__ == '__main__':
    unittest.main()