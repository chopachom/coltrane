import json
import unittest
import datetime
import time
from coltrane.rest import api_v1
from coltrane.rest.api import v1
from coltrane.rest.utils import resp_msgs, forbidden_fields
from coltrane.rest.api.v1 import from_json, storage
from coltrane.rest.api.statuses import app, STATUS_CODE, http
from coltrane.rest.app import create_app
from coltrane.rest.extensions import mongodb
from coltrane.rest.config import TestConfig, DefaultConfig
from coltrane.rest import exceptions
from coltrane.appstorage.storage import AppdataStorage, extf, intf

__author__ = 'pshkitin'

API_V1 = '/v1'

class ApiBaseTestClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        v1.get_app_id = lambda : 'app_id1'
        v1.get_remote_ip = lambda : '127.0.0.1'
        v1.get_user_id = lambda : 'user_id1'

        cls._app = create_app(
            modules=((api_v1, API_V1),),
            exts=(mongodb,),
            dict_config=dict(
                DEBUG=False,
                TESTING=True
            ),
            config=TestConfig
        )

        cls.app =  cls._app.test_client()

    @classmethod
    def tearDownClass(cls):
        with cls._app.test_request_context():
            storage.entities.drop()

            
class ApiTestCase(ApiBaseTestClass):
    def setUp(self):
        super(ApiTestCase, self).setUpClass()

    def tearDown(self):
        super(ApiTestCase, self).tearDownClass()


    def test_response_after_post(self):
        rv = self.app.post(API_V1 + '/books/key_1',
            data='{"title": "Title3", "author": "Pasha Shkitin"}',
            follow_redirects=True
        )

        rv = self.app.get(API_V1 + '/books/key_1, key_2, key_3')
        res = from_json(rv.data)['response']
        found = [d for d in res if d[STATUS_CODE] == app.OK]
        assert len(res) == 3
        assert len(found) == 1

        o = found[0]['document']
        for key in o.keys():
            assert key not in intf.values()

        del o[extf.KEY]
        del o[extf.CREATED_AT]
        del o[extf.BUCKET]
        del o['author']
        del o['title']
        assert len(o) == 0


    def test_get_fail_request(self):
        rv = self.app.get(API_V1 + '/books?filter="all"')
        res = from_json(rv.data)
        assert res['message'] == u'Invalid json object ""all""'


    def test_get_all_request(self):
        rv = self.app.get(API_V1 + '/books')
        res = from_json(rv.data)
        assert res == {'message': resp_msgs.DOC_NOT_EXISTS, STATUS_CODE: app.NOT_FOUND}


    def test_get_by_multiple_keys(self):
        rv = self.app.post(API_V1 + '/books/key_1',
            data='{"title": "Title3", "author": "Pasha Shkitin"}',
            follow_redirects=True
        )
        assert rv.status_code == http.CREATED
        assert from_json(rv.data)[extf.KEY] == 'key_1'

        rv = self.app.post(API_V1 + '/books/key_2',
            data='{"title": "Title2", "author": "Pushkin"}',
            follow_redirects=True
        )
        assert from_json(rv.data)[extf.KEY] == 'key_2'

        rv = self.app.post(API_V1 + '/books/key_4',
            data='{"title": "Title2", "author": "Pushkin"}',
            follow_redirects=True
        )
        assert from_json(rv.data)[extf.KEY] == 'key_4'

        rv = self.app.get(API_V1 + '/books/key_1, key_2, key_3')
        res = from_json(rv.data)['response']
        found = [d for d in res if d[STATUS_CODE] == app.OK]
        assert len(res) == 3
        assert len(found) == 2


    def test_get_with_no_keys(self):
        rv = self.app.get(API_V1 + '/books/  ,  ')
        assert  from_json(rv.data) == {'message': "Document key has invalid format []"}


    def test_post_request_without_specified_key(self):
        rv = self.app.post(API_V1 + '/books',
            data='{"title": "Title3", "author": "Pasha Shkitin"}',
            follow_redirects=True
        )
        key = from_json(rv.data)[extf.KEY]
        assert key is not None and isinstance(key, basestring) and len(key) > 0

    def test_success_delete_request(self):
        src = {'a': [1, 2, 3]}
        key = 'key_2'
        data = json.dumps(src)

        resp = self.app.post(API_V1 + '/books/' + key, data=data, follow_redirects=True)
        assert from_json(resp.data)[extf.KEY] == key

        resp = self.app.delete(API_V1 + '/books/' + key)
        assert from_json(resp.data) == {'message': resp_msgs.DOC_DELETED, STATUS_CODE: app.OK}

    def test_fail_delete_request(self):
        rv = self.app.delete(API_V1 + '/books/4')
        assert  from_json(rv.data) == \
                {'message': resp_msgs.DOC_NOT_EXISTS, STATUS_CODE: app.NOT_FOUND}
        assert rv.status_code == http.NOT_FOUND


    def test_forbidden_where_field(self):
        rv = self.app.post(API_V1 + '/books',
            data=json.dumps({intf.ID:'id', 'a':{'d': {'e': {forbidden_fields.WHERE:[1,2,3]}}}}),
            follow_redirects=True
        )
        res = from_json(rv.data)
        assert res == {"message": "Document contains forbidden fields [%s,%s]" %
                                  (forbidden_fields.WHERE, intf.ID), STATUS_CODE: app.BAD_REQUEST}

        filter = {'a':21, intf.ID:'app_id', 'b':[1,2,3],
                  'c': {'d': {'e': {forbidden_fields.WHERE:[1,2,3]}}}}
        rv = self.app.get(API_V1 + '/books?filter=' + json.dumps(filter))
        res = from_json(rv.data)
        assert res == {"message": "Document contains forbidden fields [%s,%s]" %
                                  (forbidden_fields.WHERE, intf.ID),
                       STATUS_CODE: app.BAD_REQUEST}

        filter = {'a':21, intf.ID:'app_id', 'b':[1,2,3],
                  'c': {'d': {'e': {forbidden_fields.WHERE:[1,2,3]}}}}
        rv = self.app.delete(API_V1 + '/books?filter=' + json.dumps(filter))
        res = from_json(rv.data)
        assert res == {"message": "Document contains forbidden fields [%s,%s]" %
                                  (forbidden_fields.WHERE, intf.ID),
                       STATUS_CODE: app.BAD_REQUEST}

        filter = {'a':21, intf.ID:'app_id', 'b':[1,2,3],
                  'c': {'d': {'e': {forbidden_fields.WHERE:[1,2,3]}}}}
        rv = self.app.put(API_V1 + '/books?filter=' + json.dumps(filter),
            data=json.dumps({'a':'b'}),
            follow_redirects=True
        )
        res = from_json(rv.data)
        assert res == {"message": "Document contains forbidden fields [%s,%s]" %
                                  (forbidden_fields.WHERE, intf.ID),
                       STATUS_CODE: app.BAD_REQUEST}


        filter = {'a':21, 'b':[1,2,3],
                  'c': {'d': {'e': [1,2,3]}}}
        rv = self.app.put(API_V1 + '/books?filter=' + json.dumps(filter),
            data=json.dumps({intf.ID:'app_id', 'a':{'d': {'e': {forbidden_fields.WHERE:[1,2,3]}}}}),
            follow_redirects=True
        )
        res = from_json(rv.data)
        assert res == {"message": "Document contains forbidden fields [%s,%s]" %
                                  (forbidden_fields.WHERE, intf.ID),
                       STATUS_CODE: app.BAD_REQUEST}


    def test_where_field_as_string(self):
        self.app.post(API_V1 + '/books',
            data=json.dumps({'a':1}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/books',
            data=json.dumps({'a':3}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/books',
            data=json.dumps({'a':5}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/books',
            data=json.dumps({'a':7}),
            follow_redirects=True
        )

        rv = self.app.get(API_V1 + '/books?filter=\'this.a > 3\'')
        res = from_json(rv.data)
        assert res == {"message": "Invalid json object \"\'this.a > 3\'\"",
                       STATUS_CODE: app.BAD_REQUEST}


    def test_creating_docs_with_same_key(self):
        self.app.post(API_V1 + '/books/key1',
            data=json.dumps({'a':1}),
            follow_redirects=True
        )
        res = self.app.post(API_V1 + '/books/key1',
            data=json.dumps({'b':1}),
            follow_redirects=True
        )
        assert res.status_code == http.CONFLICT
        assert from_json(res.data)['message'] == \
               "Document with key [key1] and bucket [books] already exists"



class ApiUpdateManyCase(ApiBaseTestClass):

    def setUp(self):
        super(ApiUpdateManyCase, self).setUpClass()

        self.app.post(API_V1 + '/books',
            data='{"_key":"1" ,"title": "Title1", "author": "author1", "age":10, "name":"Pasha", "cources":{"one":1, "two":2}}',
            follow_redirects=True)
        self.app.post(API_V1 + '/books',
            data='{"_key":"2" ,"title": "Title2", "author": "author2", "age":20, "name":"Sasha", "cources":{"one":2, "two":2}}',
            follow_redirects=True)
        self.app.post(API_V1 + '/books',
            data='{"_key":"3" ,"title": "Title3", "author": "author3", "age":15, "name":"Nikita", "cources":{"one":3, "two":2}}',
            follow_redirects=True)
        self.app.post(API_V1 + '/books',
            data='{"_key":"4" ,"title": "Title4", "author": "author4", "age":10, "name":"Sasha", "cources":{"one":4, "two":2}}',
            follow_redirects=True)
        self.app.post(API_V1 + '/books',
            data='{"_key":"5" ,"title": "Title4", "author": "author4", "age":15, "name":"Sasha", "cources":{"one":1, "two":2}}',
            follow_redirects=True)


    def tearDown(self):
        super(ApiUpdateManyCase, self).tearDownClass()

    def test_get_by_filter_with_key(self):
        filter = {extf.KEY: 5, 'age':15}
        res = self.app.get(API_V1 + '/books?filter=' + json.dumps(filter))
        assert len(from_json(res.data)['response']) == 1

        filter = {extf.KEY: 5, 'age':25}
        res = self.app.get(API_V1 + '/books?filter=' + json.dumps(filter))
        assert res.status_code == http.NOT_FOUND

    def test_inner_query(self):
        filter = {'$and': [{extf.KEY: 5}, {'age':15}]}
        res = self.app.get(API_V1 + '/books?filter=' + json.dumps(filter))
        assert len(from_json(res.data)['response']) == 1

        filter = {'$and': [{extf.KEY: {'$gt':3}}, {extf.KEY: {'$lt':5}}]}
        res = self.app.get(API_V1 + '/books?filter=' + json.dumps(filter))
        assert res.status_code == http.NOT_FOUND


    def test_put_not_existing_document(self):
        src_key = "my_key"
        src = {"title": "Title3", "author": "Vasya Shkitin"}
        rv = self.app.put(API_V1 + '/books/' + src_key,
            data=json.dumps(src),
            follow_redirects=True
        )

        print rv.data
        data = from_json(rv.data)
        res = data
        assert res == {'message': resp_msgs.DOC_NOT_EXISTS, STATUS_CODE: app.NOT_FOUND}


    def test_put_with_forbidden_fields(self):
        src_key = "my_key"
        src = {extf.KEY: src_key, intf.APP_ID: "123", extf.BUCKET: "books",
               intf.CREATED_AT: "12.12.1222", "title": "Title3", "author": "Vasya Shkitin"}
        rv = self.app.put(API_V1 + '/books/' + src_key,
            data=json.dumps(src),
            follow_redirects=True
        )

        print rv.data
        data = from_json(rv.data)
        res = data['message']
        assert res == 'Document contains forbidden fields [%s,%s]' % (
            extf.KEY, extf.BUCKET)

        src = {intf.APP_ID: "123", intf.CREATED_AT: "12.12.1222",
               "title": "Title3", "author": "Vasya Shkitin"}
        rv = self.app.put(API_V1 + '/books/' + src_key,
            data=json.dumps(src),
            follow_redirects=True
        )
        data = from_json(rv.data)
        res = data['message']
        assert res == 'Document key has invalid format [%s,%s]' % (
            intf.APP_ID, intf.CREATED_AT)


    def test_put_by_filter_with_force(self):
        src_key = "my_key"
        src = {extf.KEY: src_key, "a": "Math", "b": "Programming", "title": "Souls", "author": "Gogol"}
        rv = self.app.put(API_V1 + '/books?force=true&filter=' + json.dumps({"a": "Programming"}),
            data=json.dumps(src),
            follow_redirects=True
        )

        print rv.data
        data = from_json(rv.data)
        print data


    def test_put_not_existing_document_with_key_in_url(self):
        src = {"title": "Title3", "author": "Vasya Shkitin"}
        rv = self.app.put(API_V1 + '/books/new_key',
            data=json.dumps(src),
            follow_redirects=True
        )

        print rv.data
        data = from_json(rv.data)
        res = data
        assert res == {'message': resp_msgs.DOC_NOT_EXISTS, STATUS_CODE: app.NOT_FOUND}


    def test_put_existing_document(self):
        src = {"_key": "my_key", "title": "Title3", "author": "Pasha Shkitin"}
        rv = self.app.post(API_V1 + '/books',
            data=json.dumps(src),
            follow_redirects=True
        )
        del src['_key']

        data = from_json(rv.data)
        key = data[extf.KEY]
        assert isinstance(key, basestring) and len(key) > 0 and key == 'my_key'

        src['author'] = 'Nikita Shmakov'
        rv = self.app.put(API_V1 + '/books/my_key',
            data=json.dumps(src),
            follow_redirects=True
        )

        data = from_json(rv.data)
        assert data == {'message': resp_msgs.DOC_UPDATED, STATUS_CODE: app.OK}

    def test_update_all(self):
        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 5

        src_update = {"age": 50}
        resp = self.app.put(API_V1 + '/books',
                            data=json.dumps(src_update))
        assert from_json(resp.data) == {'message': resp_msgs.DOC_UPDATED, STATUS_CODE: app.OK}
        assert resp.status_code == http.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        for b in books:
            assert b['age'] == 50


    def test_update_filter1(self):
        src_update = {"age": 50}
        filter_opts = {"age": {"$lt": 20}}
        resp = self.app.put(API_V1 + '/books?filter=' + json.dumps(filter_opts),
                            data=json.dumps(src_update))
        assert from_json(resp.data) == {'message': resp_msgs.DOC_UPDATED, STATUS_CODE: app.OK}
        assert resp.status_code == http.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        res = filter(lambda b: b['age'] == 50, books)
        assert len(res) == 4

    def test_update_filter2(self):
        src_update = {"age": 50}
        filter_opts = {"age": {"$lt": 20}, "name": "Pasha"}
        resp = self.app.put(API_V1 + '/books?filter=' + json.dumps(filter_opts),
                            data=json.dumps(src_update))
        assert from_json(resp.data) == {'message': resp_msgs.DOC_UPDATED,
                                        STATUS_CODE: app.OK}
        assert resp.status_code == http.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        res = filter(lambda b: b['age'] == 50 and b['name'] == 'Pasha', books)
        assert len(res) == 1

    def test_update_filter3(self):
        src_update = {"age": 50, "cources.two": 5}
        filter_opts = {"age": {"$lt": 20}, "cources.one": {"$lt": 3}}
        resp = self.app.put(API_V1 + '/books?filter=' + json.dumps(filter_opts),
                            data=json.dumps(src_update))
        assert from_json(resp.data) == {'message': resp_msgs.DOC_UPDATED, STATUS_CODE: app.OK}
        assert resp.status_code == http.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        res = filter(lambda b: b['age'] == 50 and b['cources']['two'] == 5, books)
        assert len(res) == 2


    def test_update_newfield(self):
        src_update = {"new_field": 100}
        resp = self.app.put(API_V1 + '/books',
                            data=json.dumps(src_update))
        assert from_json(resp.data) == {'message': resp_msgs.DOC_UPDATED,
                                        STATUS_CODE: app.OK}
        assert resp.status_code == http.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        res = filter(lambda b: b.get('new_field') == 100, books)
        assert len(res) == 5


    def test_update_multiple_keys(self):
        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 5

        src_update = {"age": 50}
        resp = self.app.put(API_V1 + '/books/1,2,5,not_existing',
                            data=json.dumps(src_update))
        status = from_json(resp.data)['response']
        assert status == [{extf.KEY: '1', STATUS_CODE: app.OK, 'message': resp_msgs.DOC_UPDATED},
                        {extf.KEY: '2', STATUS_CODE: app.OK, 'message': resp_msgs.DOC_UPDATED},
                        {extf.KEY: '5', STATUS_CODE: app.OK, 'message': resp_msgs.DOC_UPDATED},
                        {extf.KEY: 'not_existing', STATUS_CODE: app.NOT_FOUND, 'message': resp_msgs.DOC_NOT_EXISTS}]

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        for b in books:
            if b['_key'] in ['1', '2', '5', 'not_existing']:
                assert b['age'] == 50
            else:
                assert b['age'] != 50

    def test_update_with_dot(self):
        src = {"cources.one": 2}
        resp = self.app.put(API_V1 + '/books/5', data=json.dumps(src))
        assert resp.status_code == http.OK

        resp = self.app.get(API_V1 + '/books/5')
        data = from_json(resp.data)
        assert data['cources']['two'] == 2
        assert data['cources']['one'] == 2

                
    def test_update_non_existing_with_force(self):
        filter = {'a': 1}
        src_update = {"a.b.c.d": 50}
        resp = self.app.put(API_V1 + '/books?filter=%s&force=true' % json.dumps(filter),
                            data=json.dumps(src_update))
        data = from_json(resp.data)
        assert resp.status_code == http.CREATED
        assert data['message'] == resp_msgs.DOC_CREATED
        key = data[extf.KEY]

        resp = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(src_update))
        resp = from_json(resp.data)['response'][0]
        resp2 = self.app.get(API_V1 + '/books/%s' % key)
        resp2 = from_json(resp2.data)

        assert resp == resp2


class ApiDeleteManyCase(ApiBaseTestClass):
    def setUp(self):
        super(ApiDeleteManyCase, self).setUpClass()
        self.app.post(API_V1 + '/books',
            data='{"title": "Title1", "author": "author1", "age":10, "name":"Pasha"}',
            follow_redirects=True)
        self.app.post(API_V1 + '/books',
            data='{"title": "Title2", "author": "author2", "age":20, "name":"Sasha"}',
            follow_redirects=True)
        self.app.post(API_V1 + '/books',
            data='{"title": "Title3", "author": "author3", "age":15, "name":"Nikita"}',
            follow_redirects=True)
        self.app.post(API_V1 + '/books',
            data='{"title": "Title4", "author": "author4", "age":10, "name":"Sasha"}',
            follow_redirects=True)
        self.app.post(API_V1 + '/books',
            data='{"title": "Title4", "author": "author4", "age":15, "name":"Sasha"}',
            follow_redirects=True)

    def tearDown(self):
        super(ApiDeleteManyCase, self).tearDownClass()
        

    def test_delete_all_with_filter_opts(self):
        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 5

        resp = self.app.delete(API_V1 + '/books')
        assert from_json(resp.data) == {'message': resp_msgs.DOC_DELETED}
        assert resp.status_code == http.OK

        resp = self.app.get(API_V1 + '/books')
        assert resp.status_code == http.NOT_FOUND
        assert from_json(resp.data) == {'message': resp_msgs.DOC_NOT_EXISTS,
                                        STATUS_CODE: app.NOT_FOUND}

    def test_delete_all_with_wrong_filter(self):
        resp = self.app.get(API_V1 + '/books?filter=all')
        assert from_json(resp.data) == {'message': 'Invalid json object "all"',
                                        STATUS_CODE: app.BAD_REQUEST}

    def test_delete_two_by_age(self):
        filter_opts = '{"age":10}'
        resp = self.app.delete(API_V1 + '/books?filter=' + filter_opts)
        assert from_json(resp.data) == {'message': resp_msgs.DOC_DELETED}
        assert resp.status_code == http.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 3

        success = True
        for book in books:
            if book['age'] == 10:
                success = False

        assert success


    def test_delete_one_by_filter(self):
        filter_opts = '{"age":10, "name":"Sasha"}'
        resp = self.app.delete(API_V1 + '/books?filter=' + filter_opts)
        assert from_json(resp.data) == {'message': resp_msgs.DOC_DELETED}
        assert resp.status_code == http.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 4


    def test_delete_by_LT_filter(self):
        filter_opts = '{"age": { "$lt" : 15 }}'
        resp = self.app.delete(API_V1 + '/books?filter=' + filter_opts)
        assert from_json(resp.data) == {'message': resp_msgs.DOC_DELETED}
        assert resp.status_code == http.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 3

        success = True
        for book in books:
            if book['age'] == 10:
                success = False

        assert success

    def test_delete_by_GT_filter(self):
        filter_opts = '{"age": { "$gt" : 10 }}'
        resp = self.app.delete(API_V1 + '/books?filter=' + filter_opts)
        assert from_json(resp.data) == {'message': resp_msgs.DOC_DELETED}
        assert resp.status_code == http.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 2

        success = True
        for book in books:
            if book['age'] > 10:
                success = False

        assert success


    def test_delete_by_NE_filter(self):
        filter_opts = '{"age": { "$ne" : 15 }}'
        resp = self.app.delete(API_V1 + '/books?filter=' + filter_opts)
        assert from_json(resp.data) == {'message': resp_msgs.DOC_DELETED}
        assert resp.status_code == http.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 2

        success = True
        for book in books:
            if book['age'] != 15:
                success = False

        assert success


    def test_delete_by_NE_and_other_filter(self):
        filter_opts = '{"age": { "$ne" : 15 }, "name": {"$ne" : "Sasha"}}'
        resp = self.app.delete(API_V1 + '/books?filter=' + filter_opts)
        assert from_json(resp.data) == {'message': resp_msgs.DOC_DELETED}
        assert resp.status_code == http.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 4

        success = True
        for book in books:
            if book['name'] == 'Pasha':
                success = False

        assert success


    def test_delete_nothing(self):
        filter_opts = '{"age":10, "name":"Sergey"}'
        resp = self.app.delete(API_V1 + '/books?filter=' + filter_opts)
        assert  from_json(resp.data) == {'message': resp_msgs.DOC_NOT_EXISTS,
                                         STATUS_CODE: app.NOT_FOUND}
        assert resp.status_code == http.NOT_FOUND

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 5


    def test_delete_with_broken_json(self):
        filter_opts = '{"age":10, name:"Sergey"all}'

        resp = self.app.delete(API_V1 + '/books?filter=' + filter_opts)
        resp = from_json(resp.data)
        expected = {'message': 'Invalid json object \"{"age":10, name:"Sergey"all}\"',
                    STATUS_CODE: app.BAD_REQUEST}
        assert resp == expected


    def test_delete_without_filter_opts(self):
        filter_opts = '{}'
        resp = self.app.delete(API_V1 + '/books?filter=' + filter_opts)
        resp = from_json(resp.data)
        print resp
        expected = {'message': 'Invalid request syntax. Filter options were not specified',
                    STATUS_CODE: app.BAD_REQUEST}
        assert resp == expected


class ApiSpecialEndpointsCase(ApiBaseTestClass):

    def test_get_404(self):
        resp = self.app.get(API_V1 + '/.books')
        assert resp.status_code == 404

    def test_post_404(self):
        resp = self.app.post(API_V1 + '/.books', data='ololo')
        assert resp.status_code == 404

    def test_put_404(self):
        resp = self.app.put(API_V1 + '/.books', data='ololo')
        assert resp.status_code == 404

    def test_delete_404(self):
        resp = self.app.delete(API_V1 + '/.books')
        assert resp.status_code == 404


#    def test_sever_error(self):
#        old_get = storage.get
#        def get_by_ket(app_id, user_id, bucket, key):
#            raise RuntimeError("My error")
#        storage.get= get_by_ket
#
#        res = self.app.get(API_V1 + '/books/key1')
#        storage.get = old_get
#        assert res.status_code == 500



class PaginatingQueryCase(ApiBaseTestClass):

    @classmethod
    def setUpClass(cls):
        super(PaginatingQueryCase, cls).setUpClass()

        for i in xrange(100):
            cls.app.post(API_V1 + '/books/%d_key' % i,
                data='{"title": "Title%d", "author": "author%d", "age":%d, "name":"Pasha"}' % (i, i, i),
                follow_redirects=True
            )


    def test_get_all(self):
        rv = self.app.get(API_V1 + '/books')
        res = from_json(rv.data)['response']
        assert len(res) == 100


    def test_get_all_limited(self):
        with self._app.test_client() as c:
            self._app.config['DEFAULT_QUERY_LIMIT'] = 50
            rv = c.get(API_V1 + '/books')
            res = from_json(rv.data)['response']
            assert len(res) == 50


    def test_get_paginating1(self):
        rv = self.app.get(API_V1 + '/books?limit=10&skip=50')
        res = from_json(rv.data)['response']
        assert len(res) == 10
        assert res[0][extf.KEY] == '50_key'


    def test_get_paginating2(self):
        filter = {'$and': [{'age': {'$gt': 20}}, {'age': {'$lt': 80}}]}
        rv = self.app.get(API_V1 + '/books?filter=%s&limit=30&skip=20' % json.dumps(filter))
        res = from_json(rv.data)['response']
        assert len(res) == 30
        assert res[0][extf.KEY] == '41_key'


    def test_get_paginating3(self):
        filter = {'$and': [{'age': {'$gt': 20}}, {'age': {'$lt': 60}}]}
        rv = self.app.get(API_V1 + '/books?filter=%s&limit=30&skip=20' % json.dumps(filter))
        res = from_json(rv.data)['response']
        assert len(res) == 19
        assert res[0][extf.KEY] == '41_key'


    def test_get_paginating4(self):
        filter = {'$and': [{'age': {'$gt': 20}}, {'age': {'$lt': 60}}]}
        rv = self.app.get(API_V1 + '/books?filter=%s&skip=10' % json.dumps(filter))
        res = from_json(rv.data)['response']
        assert len(res) == 29
        assert res[0][extf.KEY] == '31_key'


    def test_get_paginating5(self):
        filter = {'$and': [{'age': {'$gt': 20}}, {'age': {'$lt': 60}}]}
        rv = self.app.get(API_V1 + '/books?filter=%s&limit=30' % json.dumps(filter))
        res = from_json(rv.data)['response']
        assert len(res) == 30
        assert res[0][extf.KEY] == '21_key'


    def test_get_paginating_invalid_params(self):
        filter = {'$and': [{'age': {'$gt': 20}}, {'age': {'$lt': 60}}]}
        rv = self.app.get(API_V1 + '/books?filter=%s&limit=-1&skip=20' % json.dumps(filter))
        res = from_json(rv.data)
        assert res['message'] == 'Invalid request syntax. ' \
                'Parameters skip or limit have invalid value.'
        assert rv.status_code == http.BAD_REQUEST

        rv = self.app.get(API_V1 + '/books?filter=%s&limit=10&skip=-1' % json.dumps(filter))
        res = from_json(rv.data)
        assert res['message'] == 'Invalid request syntax. '  \
                'Parameters skip or limit have invalid value.'
        assert rv.status_code == http.BAD_REQUEST

        rv = self.app.get(API_V1 + '/books?filter=%s&limit=0&skip=0' % json.dumps(filter))
        res = from_json(rv.data)
        assert res['message'] == 'Invalid request syntax. '  \
                'Parameters skip or limit have invalid value.'
        assert rv.status_code == http.BAD_REQUEST


class KeysValidationCase(ApiBaseTestClass):

    def test_strong_filter(self):
        data = {'a': 50, 'c':{'d':{'e':[{'i':10, 'j':1},{'k':9}]}},
                'b': {'b': {'c':{'d':{'e':10}}}}}
        self.app.post(API_V1 + '/books',
            data=json.dumps(data))

        filter = {'b.b.c':{'d':{'e':10}}}
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1

        filter = {'c.d.e.0.j':1}
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1

        filter = {'c.d.e.j':1}
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1

        filter = {'b.b.c':{'d.e':10}}
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        assert res.status_code == http.NOT_FOUND


        filter = {'b.__b.c': {'_d': {'e__': 10}}}
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        assert from_json(res.data)['message'] == 'Document key has invalid format [e__,__b]'


    def test_post_wrong_key_format(self):
        data = {"a": 50, 'b': {'b*s': [1,2,3]}}
        resp = self.app.post(API_V1 + '/books',
            data=json.dumps(data))
        data = from_json(resp.data)
        assert resp.status_code == http.BAD_REQUEST
        assert data['message'] == "Document key has invalid format [b*s]"


        data = {"a": 50, 'b': {'b*s': [1,2,3]}, 'c': {'d#2':{'%s*w':'a'}}}
        resp = self.app.post(API_V1 + '/books',
            data=json.dumps(data))
        data = from_json(resp.data)
        assert resp.status_code == http.BAD_REQUEST
        assert data['message'] == "Document key has invalid format [%s*w,d#2,b*s]"


    def test_put_filter(self):
        filter = {'a.__b__.c__': 3, 'b': {'c': {'_sa-6767_': [10, 10]}}}
        res = self.app.put(API_V1 + '/books?filter=%s' % json.dumps(filter),
            data="{}")
        assert from_json(res.data)['message'] == 'Document key has invalid format [__b__,c__]'


        doc = {'a.__b__.c__': 3, 'b': {'c': {'_sa-6767_': [10, 10]}}}
        res = self.app.put(API_V1 + '/books',
            data=json.dumps(doc))
        assert from_json(res.data)['message'] == 'Document key has invalid format [__b__,c__]'
        

    def test_get_filter(self):
        filter = {"a.b": 50, '$and': [{'b': [1,2,3]}, {'c':10}]}
        resp = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        assert resp.status_code == http.NOT_FOUND


        data = {"-a":{"-b": 50}, 'b': [1,2,3], 'c':10}
        resp = self.app.post(API_V1 + '/books',
             data = json.dumps(data))
        assert resp.status_code == http.BAD_REQUEST

        filter = {"-a.-b": 50, '$and': [{'b': [1,2,3]}, {'c':10}]}
        resp = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        assert resp.status_code == http.BAD_REQUEST
        data = from_json(resp.data)
        assert data['message'] == "Document key has invalid format [-a,-b]"

        filter = {'$and': [{'_id': {'$gt': 20}}, {'_id': {'$lt': 80}, 'a':[1,2, {'$where':1}]}]}
        resp = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        assert resp.status_code == http.BAD_REQUEST
        assert from_json(resp.data)['message'] == \
               "Document contains forbidden fields [_id,$where]"


    def test_request_with_wrong_key(self):

        data = {"a":{"b": 50}, 'b': [1,2,3], 'c':10}
        resp = self.app.post(API_V1 + '/books/*key1',
             data = json.dumps(data))
        assert resp.status_code == http.BAD_REQUEST
        assert from_json(resp.data)['message'] == "Document key has invalid format [*key1]"

        resp = self.app.get(API_V1 + '/books/-key1_')
        assert resp.status_code == http.BAD_REQUEST
        assert from_json(resp.data)['message'] == "Document key has invalid format [-key1_]"


class FilterByDateCase(ApiBaseTestClass):
    def tearDown(self):
        super(FilterByDateCase, self).tearDownClass()

    def setUp(self):
        super(FilterByDateCase, self).setUpClass()



    def to_json(self, dict):
        DT_HANDLER = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
        return json.dumps(dict, default=DT_HANDLER)

    def test_filter_by_created_date(self):
        data = {"a":{"b": 50}, 'b': [1,2,3], 'c':10}
        self.app.post(API_V1 + '/books',
            data = json.dumps(data))
        now = datetime.datetime.utcnow()
        time.sleep(1)
        self.app.post(API_V1 + '/books',
            data = json.dumps(data))

        filter = {extf.CREATED_AT: {'$gt': now}}
        filter = self.to_json(filter)
        res = self.app.get(API_V1 + '/books?filter=%s' % filter)
        res = from_json(res.data)['response']
        v = datetime.datetime.strptime(res[0][extf.CREATED_AT], '%Y-%m-%dT%H:%M:%S.%f')
        assert now.microsecond < v.microsecond
        assert len(res) == 1


    def test_filter_by_special_date(self):
        data = {"a":{"b": 50}, 'date1': "2001-12-12T12:12:12.12Z", 'date2': "2011-12-12T12:12:12.12Z", 'c':10}
        self.app.post(API_V1 + '/books',
            data = json.dumps(data))
        data = {"a":{"b": 50}, 'date1': "2002-12-12T12:12:12.12Z", 'date2': "2009-12-12T12:12:12.12Z", 'c':10}
        self.app.post(API_V1 + '/books',
            data = json.dumps(data))
        data = {"a":{"b": 50}, 'date1': "2003-12-12T12:12:12.12Z", 'date2': "2012-12-12T12:12:12.12Z", 'c':10}
        self.app.post(API_V1 + '/books',
            data = json.dumps(data))


        filter = {'date1': {'$gt': "2002-12-12T12:12:12.12Z"}}
        filter = self.to_json(filter)
        res = self.app.get(API_V1 + '/books?filter=%s' % filter)
        res = from_json(res.data)['response']
        assert len(res) == 1

        filter = {'date1': {'$gt': "2002-12-12T12:12:11.12Z"}}
        filter = self.to_json(filter)
        res = self.app.get(API_V1 + '/books?filter=%s' % filter)
        res = from_json(res.data)['response']
        assert len(res) == 2

        filter = {'date1': {'$lt': "2003-12-12T12:12:13.12Z"}, 'date2': {'$gt': "2009-12-12T12:12:13.12Z"}}
        filter = self.to_json(filter)
        res = self.app.get(API_V1 + '/books?filter=%s' % filter)
        res = from_json(res.data)['response']
        assert len(res) == 2



if __name__ == '__main__':
    unittest.main()