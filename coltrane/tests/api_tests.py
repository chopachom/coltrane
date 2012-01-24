import base64
import json
import unittest
import datetime
import time
from bson.binary import Binary
from bson.dbref import DBRef
from pymongo import GEO2D
from coltrane import appstorage
from coltrane.appstorage import reservedf, forbidden_fields
from coltrane.appstorage.datatypes import Pointer, Blob, GeoPoint
from coltrane.rest.api import api_v1
from coltrane.rest.api import v1
from coltrane.rest.api.datatypes import type_codes, TYPE_FIELD
from coltrane.rest.utils import resp_msgs
from coltrane.rest.api.v1 import from_json, storage
from coltrane.rest.app import create_app
from coltrane.rest.extensions import mongodb
from coltrane.rest.config import TestConfig
from coltrane.rest import STATUS_CODE, app_status, http_status
from coltrane.appstorage.storage import extf, intf
from coltrane.appstorage import storage as storage_module

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

    def test_get_fail_request(self):
        rv = self.app.get(API_V1 + '/books?filter="all"')
        res = from_json(rv.data)
        assert res['message'] == u'Invalid json object ""all""'


    def test_get_all_request(self):
        rv = self.app.get(API_V1 + '/books')
        res = from_json(rv.data)
        assert res == {'message': resp_msgs.DOC_NOT_EXISTS, STATUS_CODE: app_status.NOT_FOUND}


    def test_get_by_multiple_keys(self):
        rv = self.app.post(API_V1 + '/books/key_1',
            data='{"title": "Title3", "author": "Pasha Shkitin"}',
            follow_redirects=True
        )
        assert rv.status_code == http_status.CREATED
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
        assert rv.status_code == http_status.NOT_FOUND


    def test_get_with_no_keys(self):
        rv = self.app.get(API_V1 + '/books/  ')
        assert  from_json(rv.data) == {'message': "No key has been passed"}


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
        assert from_json(resp.data) == {'message': resp_msgs.DOC_DELETED, STATUS_CODE: app_status.OK}

    def test_fail_delete_request(self):
        rv = self.app.delete(API_V1 + '/books/4')
        assert  from_json(rv.data) ==\
                {'message': resp_msgs.DOC_NOT_EXISTS, STATUS_CODE: app_status.NOT_FOUND}
        assert rv.status_code == http_status.NOT_FOUND


    def test_forbidden_where_field(self):
        rv = self.app.post(API_V1 + '/books',
            data=json.dumps({intf.ID:'id', 'a':{'d': {'e': {forbidden_fields.WHERE:[1,2,3]}}}}),
            follow_redirects=True
        )
        res = from_json(rv.data)
        assert res == {"message": "Document contains forbidden fields [%s,%s]" %
                                  (forbidden_fields.WHERE, intf.ID), STATUS_CODE: app_status.BAD_REQUEST}

        filter = {'a':21, intf.ID:'app_id', 'b':[1,2,3],
                  'c': {'d': {'e': {forbidden_fields.WHERE:[1,2,3]}}}}
        rv = self.app.get(API_V1 + '/books?filter=' + json.dumps(filter))
        res = from_json(rv.data)
        assert res == {"message": "Document contains forbidden fields [%s,%s]" %
                                  (forbidden_fields.WHERE, intf.ID),
                       STATUS_CODE: app_status.BAD_REQUEST}

        filter = {'a':21, intf.ID:'app_id', 'b':[1,2,3],
                  'c': {'d': {'e': {forbidden_fields.WHERE:[1,2,3]}}}}
        rv = self.app.delete(API_V1 + '/books?filter=' + json.dumps(filter))
        res = from_json(rv.data)
        assert res == {"message": "Document contains forbidden fields [%s,%s]" %
                                  (forbidden_fields.WHERE, intf.ID),
                       STATUS_CODE: app_status.BAD_REQUEST}

        filter = {'a':21, intf.ID:'app_id', 'b':[1,2,3],
                  'c': {'d': {'e': {forbidden_fields.WHERE:[1,2,3]}}}}
        rv = self.app.put(API_V1 + '/books?filter=' + json.dumps(filter),
            data=json.dumps({'a':'b'}),
            follow_redirects=True
        )
        res = from_json(rv.data)
        assert res == {"message": "Document contains forbidden fields [%s,%s]" %
                                  (forbidden_fields.WHERE, intf.ID),
                       STATUS_CODE: app_status.BAD_REQUEST}


        filter = {'a':21, 'b':[1,2,3],
                  'c': {'d': {'e': [1,2,3]}}}
        rv = self.app.put(API_V1 + '/books?filter=' + json.dumps(filter),
            data=json.dumps({intf.ID:'app_id', 'a':{'d': {'e': {forbidden_fields.WHERE:[1,2,3]}}}}),
            follow_redirects=True
        )
        res = from_json(rv.data)
        assert res == {"message": "Document contains forbidden fields [%s,%s]" %
                                  (forbidden_fields.WHERE, intf.ID),
                       STATUS_CODE: app_status.BAD_REQUEST}


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
                       STATUS_CODE: app_status.BAD_REQUEST}


    def test_creating_docs_with_same_key(self):
        self.app.post(API_V1 + '/books/key1',
            data=json.dumps({'a':1}),
            follow_redirects=True
        )
        res = self.app.post(API_V1 + '/books/key1',
            data=json.dumps({'b':1}),
            follow_redirects=True
        )
        assert res.status_code == http_status.CONFLICT
        assert from_json(res.data)['message'] ==\
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
        assert res.status_code == http_status.NOT_FOUND

    def test_inner_query(self):
        filter = {'$and': [{extf.KEY: 5}, {'age':15}]}
        res = self.app.get(API_V1 + '/books?filter=' + json.dumps(filter))
        assert len(from_json(res.data)['response']) == 1

        filter = {'$and': [{extf.KEY: {'$gt':3}}, {extf.KEY: {'$lt':5}}]}
        res = self.app.get(API_V1 + '/books?filter=' + json.dumps(filter))
        assert res.status_code == http_status.NOT_FOUND


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
        assert res == {'message': resp_msgs.DOC_NOT_EXISTS, STATUS_CODE: app_status.NOT_FOUND}


    def test_put_with_forbidden_fields(self):
        src_key = "my_key"
        src = {extf.KEY: src_key, intf.APP_ID: "123", reservedf.BUCKET: "books",
               reservedf.CREATED_AT: "12.12.1222", "title": "Title3", "author": "Vasya Shkitin"}
        rv = self.app.put(API_V1 + '/books/' + src_key,
            data=json.dumps(src),
            follow_redirects=True
        )

        print rv.data
        data = from_json(rv.data)
        res = data['message']
        assert res == 'Document contains forbidden fields [%s,%s,%s]' % (
            extf.KEY, reservedf.CREATED_AT, reservedf.BUCKET)

        src = {intf.APP_ID: "123",
               "title": "Title3", "author": "Vasya Shkitin"}
        rv = self.app.put(API_V1 + '/books/' + src_key,
            data=json.dumps(src),
            follow_redirects=True
        )
        data = from_json(rv.data)
        res = data['message']
        assert res == 'Document key has invalid format [%s]' % (
            intf.APP_ID)


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
        assert res == {'message': resp_msgs.DOC_NOT_EXISTS, STATUS_CODE: app_status.NOT_FOUND}


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
        assert data == {'message': resp_msgs.DOC_UPDATED, STATUS_CODE: app_status.OK}

    def test_update_all(self):
        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 5

        src_update = {"age": 50}
        resp = self.app.put(API_V1 + '/books',
            data=json.dumps(src_update))
        assert from_json(resp.data) == {'message': resp_msgs.DOC_UPDATED, STATUS_CODE: app_status.OK}
        assert resp.status_code == http_status.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        for b in books:
            assert b['age'] == 50


    def test_update_filter1(self):
        src_update = {"age": 50}
        filter_opts = {"age": {"$lt": 20}}
        resp = self.app.put(API_V1 + '/books?filter=' + json.dumps(filter_opts),
            data=json.dumps(src_update))
        assert from_json(resp.data) == {'message': resp_msgs.DOC_UPDATED, STATUS_CODE: app_status.OK}
        assert resp.status_code == http_status.OK

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
                                        STATUS_CODE: app_status.OK}
        assert resp.status_code == http_status.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        res = filter(lambda b: b['age'] == 50 and b['name'] == 'Pasha', books)
        assert len(res) == 1

    def test_update_filter3(self):
        src_update = {"age": 50, "cources.two": 5}
        filter_opts = {"age": {"$lt": 20}, "cources.one": {"$lt": 3}}
        resp = self.app.put(API_V1 + '/books?filter=' + json.dumps(filter_opts),
            data=json.dumps(src_update))
        assert from_json(resp.data) == {'message': resp_msgs.DOC_UPDATED, STATUS_CODE: app_status.OK}
        assert resp.status_code == http_status.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        res = filter(lambda b: b['age'] == 50 and b['cources']['two'] == 5, books)
        assert len(res) == 2


    def test_update_newfield(self):
        src_update = {"new_field": 100}
        resp = self.app.put(API_V1 + '/books',
            data=json.dumps(src_update))
        assert from_json(resp.data) == {'message': resp_msgs.DOC_UPDATED,
                                        STATUS_CODE: app_status.OK}
        assert resp.status_code == http_status.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        res = filter(lambda b: b.get('new_field') == 100, books)
        assert len(res) == 5


    def test_update_with_dot(self):
        src = {"cources.one": 2}
        resp = self.app.put(API_V1 + '/books/5', data=json.dumps(src))
        assert resp.status_code == http_status.OK

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
        assert resp.status_code == http_status.CREATED
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
        assert resp.status_code == http_status.OK

        resp = self.app.get(API_V1 + '/books')
        assert resp.status_code == http_status.NOT_FOUND
        assert from_json(resp.data) == {'message': resp_msgs.DOC_NOT_EXISTS,
                                        STATUS_CODE: app_status.NOT_FOUND}

    def test_delete_all_with_wrong_filter(self):
        resp = self.app.get(API_V1 + '/books?filter=all')
        assert from_json(resp.data) == {'message': 'Invalid json object "all"',
                                        STATUS_CODE: app_status.BAD_REQUEST}

    def test_delete_two_by_age(self):
        filter_opts = '{"age":10}'
        resp = self.app.delete(API_V1 + '/books?filter=' + filter_opts)
        assert from_json(resp.data) == {'message': resp_msgs.DOC_DELETED}
        assert resp.status_code == http_status.OK

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
        assert resp.status_code == http_status.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 4


    def test_delete_by_LT_filter(self):
        filter_opts = '{"age": { "$lt" : 15 }}'
        resp = self.app.delete(API_V1 + '/books?filter=' + filter_opts)
        assert from_json(resp.data) == {'message': resp_msgs.DOC_DELETED}
        assert resp.status_code == http_status.OK

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
        assert resp.status_code == http_status.OK

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
        assert resp.status_code == http_status.OK

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
        assert resp.status_code == http_status.OK

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
                                         STATUS_CODE: app_status.NOT_FOUND}
        assert resp.status_code == http_status.NOT_FOUND

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 5


    def test_delete_with_broken_json(self):
        filter_opts = '{"age":10, name:"Sergey"all}'

        resp = self.app.delete(API_V1 + '/books?filter=' + filter_opts)
        resp = from_json(resp.data)
        expected = {'message': 'Invalid json object \"{"age":10, name:"Sergey"all}\"',
                    STATUS_CODE: app_status.BAD_REQUEST}
        assert resp == expected


    def test_delete_without_filter_opts(self):
        filter_opts = '{}'
        resp = self.app.delete(API_V1 + '/books?filter=' + filter_opts)
        resp = from_json(resp.data)
        print resp
        expected = {'message': 'Invalid request syntax. Filter options were not specified',
                    STATUS_CODE: app_status.BAD_REQUEST}
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
        assert res['message'] == 'Invalid request syntax. '\
                                 'Parameters skip or limit have invalid value.'
        assert rv.status_code == http_status.BAD_REQUEST

        rv = self.app.get(API_V1 + '/books?filter=%s&limit=10&skip=-1' % json.dumps(filter))
        res = from_json(rv.data)
        assert res['message'] == 'Invalid request syntax. '\
                                 'Parameters skip or limit have invalid value.'
        assert rv.status_code == http_status.BAD_REQUEST

        rv = self.app.get(API_V1 + '/books?filter=%s&limit=-1&skip=0' % json.dumps(filter))
        res = from_json(rv.data)
        assert res['message'] == 'Invalid request syntax. '\
                                 'Parameters skip or limit have invalid value.'
        assert rv.status_code == http_status.BAD_REQUEST


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
        assert res.status_code == http_status.NOT_FOUND


        filter = {'b.__b.c': {'_d': {'e__': 10}}}
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        assert from_json(res.data)['message'] == 'Document key has invalid format [e__,__b]'


    def test_post_wrong_key_format(self):
        data = {"a": 50, 'b': {'b*s': [1,2,3]}}
        resp = self.app.post(API_V1 + '/books',
            data=json.dumps(data))
        data = from_json(resp.data)
        assert resp.status_code == http_status.BAD_REQUEST
        assert data['message'] == "Document key has invalid format [b*s]"


        data = {"a": 50, 'b': {'b*s': [1,2,3]}, 'c': {'d#2':{'%s*w':'a'}}}
        resp = self.app.post(API_V1 + '/books',
            data=json.dumps(data))
        data = from_json(resp.data)
        assert resp.status_code == http_status.BAD_REQUEST
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
        assert resp.status_code == http_status.NOT_FOUND


        data = {"-a":{"-b": 50}, 'b': [1,2,3], 'c':10}
        resp = self.app.post(API_V1 + '/books',
            data = json.dumps(data))
        assert resp.status_code == http_status.BAD_REQUEST

        filter = {"-a.-b": 50, '$and': [{'b': [1,2,3]}, {'c':10}]}
        resp = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        assert resp.status_code == http_status.BAD_REQUEST
        data = from_json(resp.data)
        assert data['message'] == "Document key has invalid format [-a,-b]"

        filter = {'$and': [{'_id': {'$gt': 20}}, {'_id': {'$lt': 80}, 'a':[1,2, {'$where':1}]}]}
        resp = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        assert resp.status_code == http_status.BAD_REQUEST
        assert from_json(resp.data)['message'] ==\
               "Document contains forbidden fields [_id,$where]"


    def test_request_with_unusual_key(self):

        data = {"a":{"b": 50}, 'b': [1,2,3], 'c':10}
        resp = self.app.post(API_V1 + '/books/*key1',
            data = json.dumps(data))
        assert resp.status_code == http_status.CREATED
        resp = self.app.post(API_V1 + '/books/|',
            data = json.dumps(data))
        assert resp.status_code == http_status.CREATED

        resp = self.app.get(API_V1 + '/books/*key1')
        assert resp.status_code == http_status.OK

        resp = self.app.get(API_V1 + '/books/|')
        assert resp.status_code == http_status.OK

        resp = self.app.get(API_V1 + '/books/-ke|y1_')
        assert resp.status_code == http_status.NOT_FOUND


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

        filter = {reservedf.CREATED_AT: {'$gt': {TYPE_FIELD: type_codes.DATE, 'iso': now.isoformat()}}}
        filter = self.to_json(filter)
        res = self.app.get(API_V1 + '/books?filter=%s' % filter)
        res = from_json(res.data)['response']
        v = datetime.datetime.strptime(res[0][reservedf.CREATED_AT], '%Y-%m-%dT%H:%M:%S.%f')
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


class CustomDataTypesCase(ApiBaseTestClass):
    def setUp(self):
        super(CustomDataTypesCase, self).setUpClass()

    def tearDown(self):
        super(CustomDataTypesCase, self).tearDownClass()


    def test_date_save(self):
        dt = datetime.datetime.utcnow().isoformat()
        res = self.app.post(API_V1 + '/books/1',
            data=json.dumps({'a':1, 'b': dt, 'c': {TYPE_FIELD: type_codes.DATE, 'iso': dt}}),
            follow_redirects=True
        )
        key = from_json(res.data)[extf.KEY]
        res = self.app.get(API_V1 + '/books/%s' % key)
        res = from_json(res.data)
        assert res['b'] == dt
        assert isinstance(res[reservedf.CREATED_AT], basestring)
        assert 'iso' in res['c'] and TYPE_FIELD in res['c']

        obj = storage.get(v1.get_app_id(), v1.get_user_id(), 'books', key)
        assert isinstance(obj['b'], basestring)
        assert isinstance(obj['c'], datetime.datetime)
        assert isinstance(obj[reservedf.CREATED_AT], datetime.datetime)

    def test_list_date(self):
        dt = datetime.datetime.utcnow().isoformat()
        self.app.post(API_V1 + '/books/1',
            data=json.dumps({'a':1, 'b': dt,
                             'c': [{TYPE_FIELD: type_codes.DATE, 'iso': dt},
                                   {TYPE_FIELD: type_codes.DATE, 'iso': dt}]}),
            follow_redirects=True
        )
        res = self.app.get(API_V1 + '/books/1')
        res = from_json(res.data)
        assert type(res['c']) == list
        for v in res['c']:
            assert 'iso' in v and TYPE_FIELD in v

        obj = storage.get(v1.get_app_id(), v1.get_user_id(), 'books', '1')
        assert isinstance(obj[reservedf.CREATED_AT], datetime.datetime)
        assert type(obj['c']) == list
        for v in obj['c']:
            assert isinstance(v, datetime.datetime)


    def test_date_filter(self):
        dt = datetime.datetime(2012, 1, 20, 10, 10, 20).isoformat()
        self.app.post(API_V1 + '/books',
            data=json.dumps({'a':1, 'b': dt, 'c': {TYPE_FIELD: type_codes.DATE, 'iso': dt}}),
            follow_redirects=True
        )
        dt = datetime.datetime(2012, 1, 20, 10, 10, 10).isoformat()
        self.app.post(API_V1 + '/books',
            data=json.dumps({'a':1, 'b': dt, 'c': {TYPE_FIELD: type_codes.DATE, 'iso': dt}}),
            follow_redirects=True
        )
        dt = datetime.datetime(2012, 1, 20, 10, 10, 15).isoformat()
        filter = {'c': {'$gt': {TYPE_FIELD: type_codes.DATE, 'iso': dt}}}
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1

        dt = datetime.datetime(2012, 1, 20, 10, 10, 20).isoformat()
        filter = {'c': {'$lte': {TYPE_FIELD: type_codes.DATE, 'iso': dt}}}
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 2

    def test_list_date_filter(self):
        dt1 = datetime.datetime(2012, 1, 20, 10, 10, 20).isoformat()
        dt2 = datetime.datetime(2012, 1, 20, 10, 10, 30).isoformat()
        self.app.post(API_V1 + '/books',
            data=json.dumps({'a':1, 'c':
                [{TYPE_FIELD: type_codes.DATE, 'iso': dt1}, {TYPE_FIELD: type_codes.DATE, 'iso': dt2}]}),
            follow_redirects=True
        )
        dt1 = datetime.datetime(2012, 1, 20, 10, 10, 30).isoformat()
        dt2 = datetime.datetime(2012, 1, 20, 10, 10, 40).isoformat()
        self.app.post(API_V1 + '/books',
            data=json.dumps({'a':2, 'c':
                [{TYPE_FIELD: type_codes.DATE, 'iso': dt1}, {TYPE_FIELD: type_codes.DATE, 'iso': dt2}]}),
            follow_redirects=True
        )
        dt = datetime.datetime(2012, 1, 20, 10, 10, 35).isoformat()
        filter = {'c': {'$gt': {TYPE_FIELD: type_codes.DATE, 'iso': dt}}}
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1
        assert res[0]['a'] == 2


    def test_date_update(self):
        dt = datetime.datetime(2012, 1, 20, 10, 10, 20).isoformat()
        self.app.post(API_V1 + '/books/1',
            data=json.dumps({'a':1, 'b': dt, 'c': {TYPE_FIELD: type_codes.DATE, 'iso': dt}}),
            follow_redirects=True
        )
        dt = datetime.datetime(2012, 1, 20, 10, 10, 10).isoformat()
        self.app.put(API_V1 + '/books/1',
            data=json.dumps({'c': {TYPE_FIELD: type_codes.DATE, 'iso': dt}}),
            follow_redirects=True
        )
        res = self.app.get(API_V1 + '/books/1')
        res = from_json(res.data)
        assert reservedf.UPDATED_AT in res and res['c']['iso'] == dt


    def test_pointer_save(self):
        self.app.post(API_V1 + '/books/1',
            data=json.dumps({'a': 1, 'c': 2}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/boobs/1',
            data=json.dumps({'c': {TYPE_FIELD: type_codes.POINTER, Pointer.BUCKET: 'books', Pointer.KEY: '1'}}),
            follow_redirects=True
        )
        res = self.app.get(API_V1 + '/boobs/1')
        res = from_json(res.data)
        assert TYPE_FIELD in res['c'] and Pointer.BUCKET in res['c'] and Pointer.KEY in res['c']

        old_to_ext = storage_module._to_external
        storage_module._to_external = lambda x: x
        obj = storage.get(v1.get_app_id(), v1.get_user_id(), 'boobs', '1')
        c = obj['c']
        assert isinstance(c, DBRef)
        assert c.collection == 'books'
        assert c.id == appstorage._internal_id(v1.get_app_id(), v1.get_user_id(), 'books', 0, '1')
        storage_module._to_external = old_to_ext


    def test_list_pointer_save(self):
        self.app.post(API_V1 + '/books/1',
            data=json.dumps({'a': 1, 'c': 2}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/orders/1',
            data=json.dumps({'c':
                [{TYPE_FIELD: type_codes.POINTER, Pointer.BUCKET: 'books', Pointer.KEY: '1'},
                {TYPE_FIELD: type_codes.POINTER, Pointer.BUCKET: 'books', Pointer.KEY: '1'}]}),
            follow_redirects=True
        )
        res = self.app.get(API_V1 + '/orders/1')
        res = from_json(res.data)

        assert type(res['c']) == list
        for v in res['c']:
            assert Pointer.KEY in v and Pointer.BUCKET in v

        old_to_ext = storage_module._to_external
        storage_module._to_external = lambda x: x

        obj = storage.get(v1.get_app_id(), v1.get_user_id(), 'orders', '1')
        assert type(obj['c']) == list
        for v in obj['c']:
            assert isinstance(v, DBRef)
            assert v.collection == 'books'
            assert v.id == appstorage._internal_id(v1.get_app_id(), v1.get_user_id(), 'books', 0, '1')
        storage_module._to_external = old_to_ext

    def test_pointer_filter(self):
        self.app.post(API_V1 + '/books/1',
            data=json.dumps({'a': 1, 'c': 2}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/boobs',
            data=json.dumps({'c': {TYPE_FIELD: type_codes.POINTER, Pointer.BUCKET: 'books', Pointer.KEY: '1'}}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/boobs',
            data=json.dumps({'c': {TYPE_FIELD: type_codes.POINTER, Pointer.BUCKET: 'books', Pointer.KEY: '2'}}),
            follow_redirects=True
        )
        res = self.app.get(API_V1 + '/boobs')
        res = from_json(res.data)['response']
        assert len(res) == 2
        filter = {'c': {TYPE_FIELD: type_codes.POINTER, Pointer.BUCKET: 'books', Pointer.KEY: '1'}}
        res = self.app.get(API_V1 + '/boobs?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1
        res = res[0]
        assert res['c'][Pointer.BUCKET] == 'books' and res['c'][Pointer.KEY] == '1'

    def test_list_pointer_filter(self):
        self.app.post(API_V1 + '/orders',
            data=json.dumps({'a':1, 'c':
                                 [{TYPE_FIELD: type_codes.POINTER, Pointer.BUCKET: 'books', Pointer.KEY: '1'},
                                {TYPE_FIELD: type_codes.POINTER, Pointer.BUCKET: 'books', Pointer.KEY: '2'}]}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/orders',
            data=json.dumps({'a':2, 'c':
                [{TYPE_FIELD: type_codes.POINTER, Pointer.BUCKET: 'books', Pointer.KEY: '3'},
                        {TYPE_FIELD: type_codes.POINTER, Pointer.BUCKET: 'books', Pointer.KEY: '4'}]}),
            follow_redirects=True
        )
        filter = {'c': {TYPE_FIELD: type_codes.POINTER, Pointer.BUCKET: 'books', Pointer.KEY: '3'}}
        res = self.app.get(API_V1 + '/orders?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']

        assert len(res) == 1
        assert type(res[0]['c']) == list
        assert res[0]['a'] == 2

    def test_pointer_update(self):
        self.app.post(API_V1 + '/books/1',
            data=json.dumps({'a': 1, 'c': 2}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/boobs/1',
            data=json.dumps({'c': {TYPE_FIELD: type_codes.POINTER, Pointer.BUCKET: 'books', Pointer.KEY: '1'}}),
            follow_redirects=True
        )
        self.app.put(API_V1 + '/boobs/1',
            data=json.dumps({'c': {TYPE_FIELD: type_codes.POINTER, Pointer.BUCKET: 'books', Pointer.KEY: '2'}}),
            follow_redirects=True
        )
        res = self.app.get(API_V1 + '/boobs/1')
        res = from_json(res.data)
        assert res['c'][Pointer.BUCKET] == 'books' and res['c'][Pointer.KEY] == '2'

    def test_blob_save(self):
        source = 'This is an encoded string'
        encoded = base64.encodestring(source)

        self.app.post(API_V1 + '/books/1',
            data=json.dumps({'a': 1, 'c': {TYPE_FIELD: type_codes.BLOB,
                                           Blob.BASE64: encoded}}),
            follow_redirects=True
        )
        res = self.app.get(API_V1 + '/books/1')
        res = from_json(res.data)
        binary_field = base64.decodestring(res['c'][Blob.BASE64])

        assert source == binary_field

        old_to_ext = storage_module._to_external
        storage_module._to_external = lambda x: x
        obj = storage.get(v1.get_app_id(), v1.get_user_id(), 'books', '1')
        c = obj['c']
        assert isinstance(c, Binary)
        storage_module._to_external = old_to_ext

    def test_list_blob_save(self):
        source = 'This is an encoded string'
        encoded = base64.encodestring(source)

        self.app.post(API_V1 + '/books/1',
            data=json.dumps({'a': 1, 'c':
                    [{TYPE_FIELD: type_codes.BLOB, Blob.BASE64: encoded},
                    {TYPE_FIELD: type_codes.BLOB, Blob.BASE64: encoded}]}),
            follow_redirects=True
        )
        res = self.app.get(API_V1 + '/books/1')
        res = from_json(res.data)
        assert type(res['c']) == list
        assert len(res['c']) == 2
        assert base64.decodestring(res['c'][0][Blob.BASE64]) == \
               base64.decodestring(res['c'][1][Blob.BASE64])

        binary_field = base64.decodestring(res['c'][0][Blob.BASE64])
        assert source == binary_field

        old_to_ext = storage_module._to_external
        storage_module._to_external = lambda x: x
        obj = storage.get(v1.get_app_id(), v1.get_user_id(), 'books', '1')
        c = obj['c'][0]
        assert isinstance(c, Binary)
        storage_module._to_external = old_to_ext

    def test_geo_save(self):
        self.app.post(API_V1 + '/books/1',
            data=json.dumps({'a': 1, 'c':
                    {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 10, GeoPoint.LONGITUDE: 10}}),
            follow_redirects=True
        )
        res = self.app.get(API_V1 + '/books/1')
        res = from_json(res.data)
        assert res['c'] == {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 10, GeoPoint.LONGITUDE: 10}

        old_to_ext = storage_module._to_external
        storage_module._to_external = lambda x: x
        obj = storage.get(v1.get_app_id(), v1.get_user_id(), 'books', '1')
        c = obj['__geo_c']
        assert c == {GeoPoint.LATITUDE: 10, GeoPoint.LONGITUDE: 10}
        storage_module._to_external = old_to_ext

    def test_list_geo_save(self):
        self.app.post(API_V1 + '/books/1',
            data=json.dumps({'a': 1, 'c':
          [{'geo': {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 10, GeoPoint.LONGITUDE: 10}},
           {'geo': {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 10, GeoPoint.LONGITUDE: 10}}]}),
            follow_redirects=True
        )
        res = self.app.get(API_V1 + '/books/1')
        res = from_json(res.data)
        assert type(res['c']) == list and len(res['c']) == 2
        for v in res['c']:
            assert v['geo'] == {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 10, GeoPoint.LONGITUDE: 10}

        old_to_ext = storage_module._to_external
        storage_module._to_external = lambda x: x
        obj = storage.get(v1.get_app_id(), v1.get_user_id(), 'books', '1')
        c = obj['c']
        for v in c:
            assert v['__geo_geo'] == {GeoPoint.LATITUDE: 10, GeoPoint.LONGITUDE: 10}
        storage_module._to_external = old_to_ext

    def test_geo_filter(self):
        storage.entities.ensure_index([("__geo_c", GEO2D)])
        self.app.post(API_V1 + '/books/1',
            data=json.dumps({'a': 1, 'c':
                    {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 2, GeoPoint.LONGITUDE: 2}}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/books/2',
            data=json.dumps({'a': 1, 'c':
                    {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 5, GeoPoint.LONGITUDE: 5}}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/books/3',
            data=json.dumps({'a': 1, 'c':
                    {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 3, GeoPoint.LONGITUDE: 3}}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/books/4',
            data=json.dumps({'a': 1, 'c':
                    {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 4.786, GeoPoint.LONGITUDE: 4}}),
            follow_redirects=True
        )
        filter = {'c':{"$nearSphere": {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 2, GeoPoint.LONGITUDE: 2}}}
        res = self.app.get(API_V1 + '/books?limit=3&filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 3

        filter = {'c':{"$nearSphere": {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 2, GeoPoint.LONGITUDE: 2},
                       '$maxDistanceInKilometers': 10000}}
        res = self.app.get(API_V1 + '/books?limit=3&filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 3

        filter = {'c':{"$nearSphere": {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 2, GeoPoint.LONGITUDE: 2},
                       '$maxDistanceInMiles': 70000}}
        res = self.app.get(API_V1 + '/books?limit=3&filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 3

        filter = {'c':{"$nearSphere": {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 2, GeoPoint.LONGITUDE: 2},
                       '$maxDistanceInRadians': 3}}
        res = self.app.get(API_V1 + '/books?limit=3&filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 3

    def test_list_geo_filter(self):

        self.app.post(API_V1 + '/books/1',
            data=json.dumps({'a': 1, 'c':
                [{'geo': {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 2, GeoPoint.LONGITUDE: 2}},
                        {'geo': {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 3, GeoPoint.LONGITUDE: 3}}]}),
            follow_redirects=True
        )
        storage.entities.ensure_index([("c.__geo_geo", GEO2D)])
        self.app.post(API_V1 + '/books/2',
            data=json.dumps({'a': 1, 'c':
                [{'geo': {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 5, GeoPoint.LONGITUDE: 5}},
                        {'geo': {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 6, GeoPoint.LONGITUDE: 6}}]}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/books/3',
            data=json.dumps({'a': 1, 'c':
                [{'geo': {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 3, GeoPoint.LONGITUDE: 3}},
                        {'geo': {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 4, GeoPoint.LONGITUDE: 4}}]}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/books/4',
            data=json.dumps({'a': 1, 'c':
                [{'geo': {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 4, GeoPoint.LONGITUDE: 4}},
                        {'geo': {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 5, GeoPoint.LONGITUDE: 5}}]}),
            follow_redirects=True
        )
        filter = {'c': {'geo':{"$nearSphere": {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 2, GeoPoint.LONGITUDE: 2}}}}
        res = self.app.get(API_V1 + '/books?limit=3&filter=%s' % json.dumps(filter))
        assert res.status_code == http_status.NOT_FOUND
        #It is better not to use list of geopoint because of searching is not working now

    def test_geo_update(self):
        storage.entities.ensure_index([("__geo_c", GEO2D)])
        self.app.post(API_V1 + '/books/1',
            data=json.dumps({'a': 1, 'c':
                    {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 2, GeoPoint.LONGITUDE: 2}}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/books/2',
            data=json.dumps({'a': 1, 'c':
                    {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 5, GeoPoint.LONGITUDE: 5}}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/books/3',
            data=json.dumps({'a': 1, 'c':
                    {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 3, GeoPoint.LONGITUDE: 3}}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/books/4',
            data=json.dumps({'a': 1, 'c':
                    {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 4.786, GeoPoint.LONGITUDE: 4}}),
            follow_redirects=True
        )
        filter = {'c':{"$nearSphere": {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 2, GeoPoint.LONGITUDE: 2},
                       '$maxDistanceInKilometers': 10000}}
        res = self.app.put(API_V1 + '/books?limit=3&filter=%s' % json.dumps(filter),
            data=json.dumps({'b': 10}),
            follow_redirects=True)
        assert res.status_code == http_status.OK

        filter = {'c':{"$nearSphere": {TYPE_FIELD: type_codes.GEO_POINT, GeoPoint.LATITUDE: 2, GeoPoint.LONGITUDE: 2},
                       '$maxDistanceInKilometers': 10000}}
        res = self.app.get(API_V1 + '/books?limit=3&filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        for r in res:
            assert r['b'] == 10


class FetchWithCountCase(ApiBaseTestClass):

    def setUp(self):
        super(FetchWithCountCase, self).setUpClass()

        for i in range(10):
            self.app.post(API_V1 + '/books',
                data=json.dumps({'a':10, 'b': i}),
                follow_redirects=True)

    def tearDown(self):
        super(FetchWithCountCase, self).tearDownClass()

    def test_count_only(self):
        res = self.app.get(API_V1 + '/books?count=true&limit=0&filter=%s' % json.dumps({'b': {'$lt': 5}}))
        res = from_json(res.data)
        assert res == {'response':[], 'count': 5}

    def test_count_with_data(self):
        res = self.app.get(API_V1 + '/books?count=true&filter=%s' % json.dumps({'b': {'$lt': 5}}))
        res = from_json(res.data)
        assert len(res['response']) == res['count'] == 5


class IncrementDecrementVarsCase(ApiBaseTestClass):

    def setUp(self):
        super(IncrementDecrementVarsCase, self).setUpClass()

        for i in range(10):
            self.app.post(API_V1 + '/books',
                data=json.dumps({'a':10, 'b': i, 's': 15, 'arr1': [1,2,3], 'arr2': [4,5,6]}),
                follow_redirects=True)

    def tearDown(self):
        super(IncrementDecrementVarsCase, self).tearDownClass()

    def test_increment(self):
        filter = {'b': {'$gt': 8}}
        update = {'c': 20, 'd':{'e':30}, '$inc': {'a':1}}
        self.app.put(API_V1 + '/books?filter=%s' % json.dumps(filter),
            data=json.dumps(update),
            follow_redirects=True)
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1
        res = res[0]
        assert res['a'] == 11 and res['c'] and res['d']['e']

    def test_decrement(self):
        filter = {'b': {'$gt': 8}}
        update = {'c': 20, 'd':{'e':30}, '$inc': {'a':-1, 'b': 1}}
        self.app.put(API_V1 + '/books?filter=%s' % json.dumps(filter),
            data=json.dumps(update),
            follow_redirects=True)
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1
        res = res[0]
        assert res['a'] == 9 and res['b'] == 10 and res['c'] and res['d']['e']

    def test_unset(self):
        filter = {'b': {'$gt': 8}}
        update = {'c': 20, 'd':{'e':30}, '$unset': {'a': 1, 's': 15}, '$inc': {'b': 1}}
        self.app.put(API_V1 + '/books?filter=%s' % json.dumps(filter),
            data=json.dumps(update),
            follow_redirects=True)
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1
        res = res[0]
        assert not res.get('a') and \
               not res.get('s') and \
               res['b'] == 10 and \
               res['c'] and res['d']['e']

    def test_push(self):
        filter = {'b': {'$gt': 8}}
        update = {'c': 20, 'd':{'e':30}, '$push': {'arr1': 4, 'arr2': 7}}
        self.app.put(API_V1 + '/books?filter=%s' % json.dumps(filter),
            data=json.dumps(update),
            follow_redirects=True)
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1
        res = res[0]
        assert res['arr1'] == [1,2,3,4] and res['arr2'] == [4,5,6,7]

    def test_pushAll(self):
        filter = {'b': {'$gt': 8}}
        update = {'c': 20, 'd':{'e':30}, '$pushAll': {'arr1': [4,5,6], 'arr2': [7,8,9]}}
        self.app.put(API_V1 + '/books?filter=%s' % json.dumps(filter),
            data=json.dumps(update),
            follow_redirects=True)
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1
        res = res[0]
        assert res['arr1'] == [1,2,3,4,5,6] and res['arr2'] == [4,5,6,7,8,9]

    def test_pop(self):
        filter = {'b': {'$gt': 8}}
        update = {'c': 20, 'd':{'e':30}, '$pop': {'arr1': 1, 'arr2': -1}}
        self.app.put(API_V1 + '/books?filter=%s' % json.dumps(filter),
            data=json.dumps(update),
            follow_redirects=True)
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1
        res = res[0]
        assert res['arr1'] == [1,2] and res['arr2'] == [5,6]

    def test_pull(self):
        filter = {'b': {'$gt': 8}}
        update = {'c': 20, 'd':{'e':30}, '$gt':10, '$pull': {'arr1': 2, 'arr2': {'$mod': [2, 1]}}}
        self.app.put(API_V1 + '/books?filter=%s' % json.dumps(filter),
            data=json.dumps(update),
            follow_redirects=True)
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1
        res = res[0]
        assert res['arr1'] == [1,3] and res['arr2'] == [4, 6]

    def test_pullAll(self):
        filter = {'b': {'$gt': 8}}
        update = {'c': 20, 'd':{'e':30}, '$gt':10, '$pullAll': {'arr1': [1,2], 'arr2': [4,5]}}
        self.app.put(API_V1 + '/books?filter=%s' % json.dumps(filter),
            data=json.dumps(update),
            follow_redirects=True)
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1
        res = res[0]
        assert res['arr1'] == [3] and res['arr2'] == [6]

    def test_addToSet(self):
        filter = {'b': {'$gt': 8}}
        update = {'c': 20, 'd':{'e':30}, '$gt':10, '$addToSet': {'arr1': { '$each' :[1,2,4]}, 'arr2': 6}}
        self.app.put(API_V1 + '/books?filter=%s' % json.dumps(filter),
            data=json.dumps(update),
            follow_redirects=True)
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1
        res = res[0]
        assert res['arr1'] == [1,2,3,4] and res['arr2'] == [4,5,6]


class SortFieldsCase(ApiBaseTestClass):

    def setUp(self):
        super(SortFieldsCase, self).setUpClass()

        for i in range(20):
            self.app.post(API_V1 + '/books',
                data=json.dumps({'b': i, 's': i}),
                follow_redirects=True)

    def tearDown(self):
        super(SortFieldsCase, self).tearDownClass()

    def test_desc_sort(self):
        res = self.app.get(API_V1 + '/books?limit=5&sort=-b')
        res = from_json(res.data)['response']
        assert len(res) == 5
        for i in range(5):
            assert res[i]['b'] == 19 - i

    def test_asc_sort(self):
        res = self.app.get(API_V1 + '/books?limit=5&sort=s')
        res = from_json(res.data)['response']
        assert len(res) == 5
        for i in range(5):
            assert res[i]['s'] == i


class FetchEmbedDocsCase(ApiBaseTestClass):

    def setUp(self):
        super(FetchEmbedDocsCase, self).setUpClass()

    def tearDown(self):
        super(FetchEmbedDocsCase, self).tearDownClass()

    def test_pointer_fetch_embed(self):
        source1 = {'title': 'Java', 'price': 200}
        self.app.post(API_V1 + '/books/1',
            data=json.dumps(source1),
            follow_redirects=True
        )
        source2 = {'title': 'Python', 'price': 200}
        self.app.post(API_V1 + '/books/2',
            data=json.dumps(source2),
            follow_redirects=True
        )
        book1 = {TYPE_FIELD: type_codes.POINTER, Pointer.BUCKET: 'books', Pointer.KEY: '1'}
        book2 = {TYPE_FIELD: type_codes.POINTER, Pointer.BUCKET: 'books', Pointer.KEY: '2'}
        self.app.post(API_V1 + '/order/1',
            data=json.dumps({'user': 'Programmer',
                'book1': book1,
                'book2': book2,
                'books': [book1, {'a': 10}, book2]}),
            follow_redirects=True
        )

        res = self.app.get(API_V1 + '/order/1?include=book1')
        res = from_json(res.data)
        assert res['book1'][TYPE_FIELD] == 'Object'
        assert res['book2'][TYPE_FIELD] == type_codes.POINTER
        for k,v in source1.items():
            assert res['book1'][k] == v

        res = self.app.get(API_V1 + '/order/1?include=book1, book2, books')
        res = from_json(res.data)
        assert res['book1'][TYPE_FIELD] == 'Object'
        assert res['book2'][TYPE_FIELD] == 'Object'
        assert res['books'][0][TYPE_FIELD] == 'Object'
        assert res['books'][1] == {'a': 10}
        assert res['books'][2][TYPE_FIELD] == 'Object'
        for k,v in source1.items():
            assert res['book1'][k] == v
            assert res['books'][0][k] == v
        for k,v in source2.items():
            assert res['book2'][k] == v
            assert res['books'][2][k] == v


class RegexFiltersCase(ApiBaseTestClass):

    def setUp(self):
        super(RegexFiltersCase, self).setUpClass()
        self.app.post(API_V1 + '/books/1',
            data=json.dumps({'a':10, 'b': 'acmeblahcorp'}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/books/2',
            data=json.dumps({'a':10, 'b': 'acmeblaahcorp'}),
            follow_redirects=True
        )
        self.app.post(API_V1 + '/books/3',
            data=json.dumps({'a':10, 'b': 'acmeblabahcorp'}),
            follow_redirects=True
        )


    def tearDown(self):
        super(RegexFiltersCase, self).tearDownClass()

    def test_simple_regex(self):
        filter = {'b':  {'$regex' : 'acme.*corp'}}
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 3

    def test_regex_with_options(self):
        filter = {'b':  {'$regex' : 'acme.*corp', '$nin': ['acmeblaahcorp', 'acmeblabahcorp']}}
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1
        assert res[0]['b'] == 'acmeblahcorp'

    def test_regex_case_insensitive(self):
        self.app.post(API_V1 + '/books/4',
            data=json.dumps({'a':10, 'b': 'AcMeBlaBahCorP'}),
            follow_redirects=True
        )
        filter = {'b':  {'$regex' : 'acme.*corp', '$options': 'i', '$nin': ['acmeblaahcorp', 'acmeblabahcorp']}}
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 2
        assert res[0]['b'] == 'acmeblahcorp'
        assert res[1]['b'] == 'AcMeBlaBahCorP'

    def test_regex_another(self):
        self.app.post(API_V1 + '/books/4',
            data=json.dumps({'a':10, 'b': 'ABC5678'}),
            follow_redirects=True
        )
        filter = {'b':  {'$regex' : '^[A-Z]{3}[\d]{4}$'}}
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1
        assert res[0]['b'] == 'ABC5678'

        filter = {'b':  {'$regex' : '^[A-Z]{4}[\d]{4}$'}}
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        assert res.status_code == http_status.NOT_FOUND

        filter = {'b':  {'$regex' : '^[A-Z]{3}[\d]{2}'}}
        res = self.app.get(API_V1 + '/books?filter=%s' % json.dumps(filter))
        res = from_json(res.data)['response']
        assert len(res) == 1
        assert res[0]['b'] == 'ABC5678'

        
if __name__ == '__main__':
    unittest.main()