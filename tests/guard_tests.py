__author__ = 'qweqwe'
import unittest
from app import create_app
from api import api_v1
from api.v1 import from_json
from tests.stubs import fake_guard

AUTH_TOKEN = fake_guard.AUTH_TOKEN
APP_TOKEN  = fake_guard.APP_TOKEN

class GuardTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        api_v1.get_app_id = lambda : 'app_id1'
        api_v1.get_remote_ip = lambda : '127.0.0.1'
        api_v1.get_user_id = lambda : 'user_id1'
        app = create_app(
            modules=((api_v1, '/v1') ,),
            exts=(fake_guard.guard,),
            dict_config=dict(
                DEBUG=False,
                TESTING=True
            )
        )
        cls.app = app.test_client()


    def test_allow_access(self):
        rv = self.app.get('/v1/books')
        res = from_json(rv.data)
        assert res == {'response': []}

    def test_deny_access_for_auth_token(self):
        fake_guard.AUTH_TOKEN = 'Hui'
        res = self.app.get('/v1/books')
        assert res._status_code == 401
        #put back the original token
        fake_guard.AUTH_TOKEN = AUTH_TOKEN


    def test_deny_access_for_app_token(self):
        fake_guard.APP_TOKEN = 'Hui'
        res = self.app.get('/v1/books')
        assert res._status_code == 401
        #put back the original token
        fake_guard.APP_TOKEN = APP_TOKEN


if __name__ == '__main__':
    unittest.main()