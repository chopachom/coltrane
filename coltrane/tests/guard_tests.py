__author__ = 'qweqwe'
import unittest
from coltrane.api.app import create_app
from coltrane.api import api_v1
from coltrane.api.rest.v1 import from_json, resp_msgs
from coltrane.api.lib.guard_manager import GuardManager
from coltrane.api.extensions import guard
from coltrane.api.config import TestConfig
from coltrane.api.rest.statuses import http
from coltrane.db.models import User, AppToken, Application
from coltrane.db.extension import db
from coltrane import config


guard.manager = GuardManager

class GuardTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app(
            modules=((api_v1, '/v1'),),
            exts=(guard, db),
            config=TestConfig,
            dict_config=dict(SERVER_NAME='localhost')
        )
        cls.client = cls.app.test_client()
        cls.context = cls.app.test_request_context()
        cls.context.__enter__()
        u = User('user_id1', 'ololo@gmail.com', '123456')
        a = Application("Mrazish ololo", "mrazish", "description", u)
        at = AppToken(u,a)
        db.session.add_all([u, a, at])
        db.session.commit()
        cls.user=u
        cls.apptoken = at
        cls.application =a
        cls.session = db.session


    def test_allow_access(self):
        self.client.set_cookie(self.app.config.get('SERVER_NAME'), config.COOKIE_USER_AUTH_TOKEN, self.user.token)
        self.client.set_cookie(self.app.config.get('SERVER_NAME'), config.COOKIE_APP_TOKEN, self.apptoken.token)
        rv = self.client.get('/v1/books')
        self.client.delete_cookie(self.app.config.get('SERVER_NAME'), config.COOKIE_USER_AUTH_TOKEN)
        self.client.delete_cookie(self.app.config.get('SERVER_NAME'), config.COOKIE_APP_TOKEN)
        res = from_json(rv.data)
        assert res == {'message': resp_msgs.DOC_NOT_EXISTS}
        assert rv.status_code == http.NOT_FOUND


    def test_deny_access_for_auth_token(self):
        self.client.set_cookie(self.app.config.get('SERVER_NAME'), config.COOKIE_USER_AUTH_TOKEN, 'ololo')
        self.client.set_cookie(self.app.config.get('SERVER_NAME'), config.COOKIE_APP_TOKEN, self.apptoken.token)
        res = self.client.get('/v1/books')
        self.client.delete_cookie(self.app.config.get('SERVER_NAME'), config.COOKIE_USER_AUTH_TOKEN)
        self.client.delete_cookie(self.app.config.get('SERVER_NAME'), config.COOKIE_APP_TOKEN)
        assert res._status_code == http.UNAUTHORIZED


    def test_deny_access_for_app_token(self):
        self.client.set_cookie(self.app.config.get('SERVER_NAME'), config.COOKIE_USER_AUTH_TOKEN, self.user.token)
        self.client.set_cookie(self.app.config.get('SERVER_NAME'), config.COOKIE_APP_TOKEN, 'ololo')
        res = self.client.get('/v1/books')
        self.client.delete_cookie(self.app.config.get('SERVER_NAME'), config.COOKIE_USER_AUTH_TOKEN)
        self.client.delete_cookie(self.app.config.get('SERVER_NAME'), config.COOKIE_APP_TOKEN)
        assert res._status_code == http.UNAUTHORIZED

    @classmethod
    def tearDownClass(cls):
        print "Tearing down"
        db.session.delete(cls.user)
        db.session.delete(cls.apptoken)
        db.session.delete(cls.application)
        db.session.commit()
        cls.context.__exit__(None, None, None)



if __name__ == '__main__':
    unittest.main()