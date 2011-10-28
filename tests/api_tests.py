import json
import unittest
from api import api_v1
from api import v1
from api.v1 import from_json
from api.statuses import app
from app import create_app
from ds import storage
from extensions import mongodb
from ds.storage import ext_fields

__author__ = 'pshkitin'

API_V1 = '/v1'
class ApiTestCase(unittest.TestCase):

    def setUp(self):
        v1.get_app_id = lambda : 'app_id1'
        v1.get_remote_ip = lambda : '127.0.0.1'
        v1.get_user_id = lambda : 'user_id1'

        app = create_app(
            modules=((api_v1, API_V1),),
            exts=(mongodb,),
            dict_config=dict(
                DEBUG=False,
                TESTING=True
            )
        )
        self.app = app.test_client()

    def tearDown(self):
        storage._entities.drop()

    def test_getAll_request(self):
        rv = self.app.get(API_V1 + '/books')
        res = from_json(rv.data)
        assert res == {'response': []}

    def test_get_by_not_existing_key(self):
        rv = self.app.get(API_V1 + '/books/1')
        res = from_json(rv.data)
        assert res == {
            "error": {
                "code": app.NOT_FOUND,
                "message": ("Document with bucket [books] and "
                            "key [1] was not found")
            }
        }

    def test_post_request_without_specified_key(self):
        rv = self.app.post(API_V1 + '/books', data=dict(
            data='{"title": "Title3", "author": "Pasha Shkitin"}'
        ), follow_redirects=True)
        key = from_json(rv.data)['response']['key']
        assert key is not None and isinstance(key, basestring) and len(key) > 0

    def test_success_delete_request(self):
        src = {'a':[1,2,3]}
        key = 'key_2'
        data = json.dumps(src)

        resp = self.app.post(API_V1 + '/books/' + key, data={'data': data}, follow_redirects=True)
        assert from_json(resp.data)['response']['key'] == key

        resp = self.app.delete(API_V1 + '/books/' + key)
        assert from_json(resp.data)['response'] == app.OK

    def test_fail_delete_request(self):
        rv = self.app.delete(API_V1 + '/books/4')
        assert from_json(rv.data)['error']['code'] == app.NOT_FOUND
        print "Fail delete: " + rv.data


#    def test_delete_all_with_filter_opts(self):
#        self.app.post(API_V1 + '/books', data=dict(
#            data='{"title": "Title1", "author": "author1"}'
#        ), follow_redirects=True)
#        self.app.post(API_V1 + '/books', data=dict(
#            data='{"title": "Title2", "author": "author2"}'
#        ), follow_redirects=True)
#        self.app.post(API_V1 + '/books', data=dict(
#            data='{"title": "Title3", "author": "author3"}'
#        ), follow_redirects=True)
#
#        resp = self.app.get(API_V1 + '/books')
#        books = from_json(resp.data)['response']
#        assert len(books) == 3
#
#        resp = self.app.delete(API_V1 + '/books/several/{}')
#        status = from_json(resp.data)['response']
#        assert status == app.OK
#
#        resp = self.app.get(API_V1 + '/books')
#        books = from_json(resp.data)['response']
#        assert len(books) == 0


    def test_put_not_existing_document_without_key(self):
        rv = self.app.put(API_V1 + '/books', data=dict(
            data='{"title": "Title3", "author": "Vasya Shkitin"}'
        ), follow_redirects=True)

        data = from_json(rv.data)
        key = data['response']['key']
        assert isinstance(key, basestring) and len(key) > 0
        print 'Put1: ' + rv.data


    def test_put_not_existing_document_with_key(self):
        src_key = "my_key"
        src = {ext_fields.KEY: src_key, "title": "Title3", "author": "Vasya Shkitin"}
        rv = self.app.put(API_V1 + '/books', data=dict(
            data=json.dumps(src)
        ), follow_redirects=True)

        print rv.data
        data = from_json(rv.data)
        key = data['response']['key']
        assert src_key == key


    def test_put_not_existing_document_with_key_in_url(self):
        src_key = "my_key"
        src = {ext_fields.KEY: src_key, "title": "Title3", "author": "Vasya Shkitin"}
        rv = self.app.put(API_V1 + '/books/new_key', data=dict(
            data=json.dumps(src)
        ), follow_redirects=True)

        print rv.data
        data = from_json(rv.data)
        key = data['response']['key']
        assert 'new_key' == key


    def test_put_existing_document(self):
        src = {"_key": "my_key", "title": "Title3", "author": "Pasha Shkitin"}
        rv = self.app.post(API_V1 + '/books', data=dict(
            data= json.dumps(src)
        ), follow_redirects=True)

        data = from_json(rv.data)
        key = data['response']['key']
        assert isinstance(key, basestring) and len(key) > 0

        src['author'] = 'Nikita Shmakov'
        rv = self.app.put(API_V1 + '/books/my_key', data=dict(
            data=json.dumps(src)
        ), follow_redirects=True)

        data = from_json(rv.data)
        assert data['response'] == app.OK


if __name__ == '__main__':
    unittest.main()