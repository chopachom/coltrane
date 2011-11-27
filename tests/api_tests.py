import json
import unittest
from api import api_v1
from api import v1
from api.v1 import from_json, forbidden_fields
from api.statuses import app, STATUS_CODE
from app import create_app
from ds import storage
import errors
from extensions import mongodb
from ds.storage import ext_fields, int_fields

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


    def test_response_after_post(self):
        rv = self.app.post(API_V1 + '/books/key_1', data=dict(
            data='{"title": "Title3", "author": "Pasha Shkitin"}'
        ), follow_redirects=True)

        rv = self.app.get(API_V1 + '/books/key_1, key_2, key_3')
        res = from_json(rv.data)['response']
        assert len(res) == 1

        o = res[0]
        for key in o.keys():
            assert key not in int_fields.values()

        del o[ext_fields.KEY]
        del o[ext_fields.CREATED_AT]
        del o[ext_fields.BUCKET]
        del o['author']
        del o['title']
        assert len(o) == 0


    def test_get_fail_request(self):
        rv = self.app.get(API_V1 + '/books?filter="all"')
        res = from_json(rv.data)
        assert res['error'][STATUS_CODE] == app.BAD_REQUEST


    def test_get_all_request(self):
        rv = self.app.get(API_V1 + '/books')
        res = from_json(rv.data)
        assert res == {'response': []}

    def test_get_by_not_existing_key(self):
        rv = self.app.get(API_V1 + '/books/1')
        res = from_json(rv.data)
        assert res['response'] == []

    def test_get_by_multiple_keys(self):
        rv = self.app.post(API_V1 + '/books/key_1', data=dict(
            data='{"title": "Title3", "author": "Pasha Shkitin"}'
        ), follow_redirects=True)
        assert from_json(rv.data)['response']['key'] == 'key_1'

        rv = self.app.post(API_V1 + '/books/key_2', data=dict(
            data='{"title": "Title2", "author": "Pushkin"}'
        ), follow_redirects=True)
        assert from_json(rv.data)['response']['key'] == 'key_2'

        rv = self.app.post(API_V1 + '/books/key_4', data=dict(
            data='{"title": "Title2", "author": "Pushkin"}'
        ), follow_redirects=True)
        assert from_json(rv.data)['response']['key'] == 'key_4'

        rv = self.app.get(API_V1 + '/books/key_1, key_2, key_3')
        res = from_json(rv.data)['response']
        assert len(res) == 2


    def test_get_with_no_keys(self):
        rv = self.app.get(API_V1 + '/books/  ,  ')
        assert  from_json(rv.data)['error'] == {'message': "At least one key must be passed.", "code": app.BAD_REQUEST}


    def test_post_request_without_specified_key(self):
        rv = self.app.post(API_V1 + '/books', data=dict(
            data='{"title": "Title3", "author": "Pasha Shkitin"}'
        ), follow_redirects=True)
        key = from_json(rv.data)['response']['key']
        assert key is not None and isinstance(key, basestring) and len(key) > 0

    def test_success_delete_request(self):
        src = {'a': [1, 2, 3]}
        key = 'key_2'
        data = json.dumps(src)

        resp = self.app.post(API_V1 + '/books/' + key, data={'data': data}, follow_redirects=True)
        assert from_json(resp.data)['response']['key'] == key

        resp = self.app.delete(API_V1 + '/books/' + key)
        assert from_json(resp.data)['response'] == [{key: app.OK}]

    def test_fail_delete_request(self):
        rv = self.app.delete(API_V1 + '/books/4')
        assert  from_json(rv.data)['response'] == [{'4': app.NOT_FOUND}]


    def test_forbidden_where_field(self):
        rv = self.app.post(API_V1 + '/books', data=dict(
            data=json.dumps({int_fields.ID:'id', 'a':{'d': {'e': {forbidden_fields.WHERE:[1,2,3]}}}})
        ), follow_redirects=True)
        res = from_json(rv.data)['error']
        assert res == {"message": "Document contains forbidden fields [%s,%s]" %
                                  (int_fields.ID, forbidden_fields.WHERE), "code": 1}

        filter = {'a':21, int_fields.APP_ID:'app_id', 'b':[1,2,3],
                  'c': {'d': {'e': {forbidden_fields.WHERE:[1,2,3]}}}}
        rv = self.app.get(API_V1 + '/books?filter=' + json.dumps(filter))
        res = from_json(rv.data)['error']
        assert res == {"message": "Document contains forbidden fields [%s,%s]" %
                                  (int_fields.APP_ID, forbidden_fields.WHERE), "code": 1}

        filter = {'a':21, int_fields.APP_ID:'app_id', 'b':[1,2,3],
                  'c': {'d': {'e': {forbidden_fields.WHERE:[1,2,3]}}}}
        rv = self.app.delete(API_V1 + '/books?filter=' + json.dumps(filter))
        res = from_json(rv.data)['error']
        assert res == {"message": "Document contains forbidden fields [%s,%s]" %
                                  (int_fields.APP_ID, forbidden_fields.WHERE), "code": 1}

        filter = {'a':21, int_fields.APP_ID:'app_id', 'b':[1,2,3],
                  'c': {'d': {'e': {forbidden_fields.WHERE:[1,2,3]}}}}
        rv = self.app.put(API_V1 + '/books?filter=' + json.dumps(filter), data=dict(
            data=json.dumps({'a':'b'})
        ), follow_redirects=True)
        res = from_json(rv.data)['error']
        assert res == {"message": "Document contains forbidden fields [%s,%s]" %
                                  (int_fields.APP_ID, forbidden_fields.WHERE), "code": 1}


        filter = {'a':21, 'b':[1,2,3],
                  'c': {'d': {'e': [1,2,3]}}}
        rv = self.app.put(API_V1 + '/books?filter=' + json.dumps(filter), data=dict(
            data=json.dumps({int_fields.APP_ID:'app_id', 'a':{'d': {'e': {forbidden_fields.WHERE:[1,2,3]}}}})
        ), follow_redirects=True)
        res = from_json(rv.data)['error']
        assert res == {"message": "Document contains forbidden fields [%s,%s]" %
                                  (int_fields.APP_ID, forbidden_fields.WHERE), "code":1}


    def test_where_field_as_string(self):
        self.app.post(API_V1 + '/books', data=dict(
            data=json.dumps({'a':1})
        ), follow_redirects=True)
        self.app.post(API_V1 + '/books', data=dict(
            data=json.dumps({'a':3})
        ), follow_redirects=True)
        self.app.post(API_V1 + '/books', data=dict(
            data=json.dumps({'a':5})
        ), follow_redirects=True)
        self.app.post(API_V1 + '/books', data=dict(
            data=json.dumps({'a':7})
        ), follow_redirects=True)

        rv = self.app.get(API_V1 + '/books?filter=\'this.a > 3\'')
        res = from_json(rv.data)['error']
        assert res == {"message": "Invalid json object \"\'this.a > 3\'\"", "code": 1}



class ApiUpdateManyCase(unittest.TestCase):
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
        self.app.post(API_V1 + '/books', data=dict(
            data='{"_key":"1" ,"title": "Title1", "author": "author1", "age":10, "name":"Pasha", "cources":{"one":1, "two":2}}'
        ), follow_redirects=True)
        self.app.post(API_V1 + '/books', data=dict(
            data='{"_key":"2" ,"title": "Title2", "author": "author2", "age":20, "name":"Sasha", "cources":{"one":2, "two":2}}'
        ), follow_redirects=True)
        self.app.post(API_V1 + '/books', data=dict(
            data='{"_key":"3" ,"title": "Title3", "author": "author3", "age":15, "name":"Nikita", "cources":{"one":3, "two":2}}'
        ), follow_redirects=True)
        self.app.post(API_V1 + '/books', data=dict(
            data='{"_key":"4" ,"title": "Title4", "author": "author4", "age":10, "name":"Sasha", "cources":{"one":4, "two":2}}'
        ), follow_redirects=True)
        self.app.post(API_V1 + '/books', data=dict(
            data='{"_key":"5" ,"title": "Title4", "author": "author4", "age":15, "name":"Sasha", "cources":{"one":1, "two":2}}'
        ), follow_redirects=True)

    def tearDown(self):
        storage._entities.drop()

    def test_put_not_existing_document(self):
        src_key = "my_key"
        src = {"title": "Title3", "author": "Vasya Shkitin"}
        rv = self.app.put(API_V1 + '/books/' + src_key, data=dict(
            data=json.dumps(src)
        ), follow_redirects=True)

        print rv.data
        data = from_json(rv.data)
        res = data['response']
        assert res == [{src_key: app.NOT_FOUND}]


    def test_put_with_forbidden_fields(self):
        src_key = "my_key"
        src = {ext_fields.KEY: src_key, int_fields.APP_ID: "123", ext_fields.BUCKET: "books",
               int_fields.CREATED_AT: "12.12.1222", "title": "Title3", "author": "Vasya Shkitin"}
        rv = self.app.put(API_V1 + '/books/' + src_key, data=dict(
            data=json.dumps(src)
        ), follow_redirects=True)

        print rv.data
        data = from_json(rv.data)
        res = data['error']['message']
        assert res == errors.InvalidDocumentError.FORBIDDEN_FIELDS_MSG % ','.join([
            int_fields.CREATED_AT, int_fields.APP_ID])


    def test_put_by_filter_with_force(self):
        src_key = "my_key"
        src = {ext_fields.KEY: src_key, "a": "Math", "b": "Programming", "title": "Souls", "author": "Gogol"}
        rv = self.app.put(API_V1 + '/books?force=true&filter=' + json.dumps({"a": "Programming"}), data=dict(
            data=json.dumps(src)
        ), follow_redirects=True)

        print rv.data
        data = from_json(rv.data)
        print data


    def test_put_not_existing_document_with_key_in_url(self):
        src_key = "my_key"
        src = {"title": "Title3", "author": "Vasya Shkitin"}
        rv = self.app.put(API_V1 + '/books/new_key', data=dict(
            data=json.dumps(src)
        ), follow_redirects=True)

        print rv.data
        data = from_json(rv.data)
        res = data['response']
        assert res == [{'new_key': app.NOT_FOUND}]


    def test_put_existing_document(self):
        src = {"_key": "my_key", "title": "Title3", "author": "Pasha Shkitin"}
        rv = self.app.post(API_V1 + '/books', data=dict(
            data=json.dumps(src)
        ), follow_redirects=True)
        del src['_key']

        data = from_json(rv.data)
        key = data['response']['key']
        assert isinstance(key, basestring) and len(key) > 0 and key == 'my_key'

        src['author'] = 'Nikita Shmakov'
        rv = self.app.put(API_V1 + '/books/my_key', data=dict(
            data=json.dumps(src)
        ), follow_redirects=True)

        data = from_json(rv.data)
        assert data['response'] == [{'my_key': app.OK}]

    def test_update_all(self):
        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 5

        src_update = {"age": 50}
        filter_opts = '   all   '
        resp = self.app.put(API_V1 + '/books',
                            data=dict(data=json.dumps(src_update)))
        status = from_json(resp.data)['response']
        assert status == {STATUS_CODE: app.OK}

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        for b in books:
            assert b['age'] == 50


    def test_update_filter1(self):
        src_update = {"age": 50}
        filter_opts = {"age": {"$lt": 20}}
        resp = self.app.put(API_V1 + '/books?filter=' + json.dumps(filter_opts),
                            data=dict(data=json.dumps(src_update)))
        status = from_json(resp.data)['response']
        assert status == {STATUS_CODE: app.OK}

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        res = filter(lambda b: b['age'] == 50, books)
        assert len(res) == 4

    def test_update_filter2(self):
        src_update = {"age": 50}
        filter_opts = {"age": {"$lt": 20}, "name": "Pasha"}
        resp = self.app.put(API_V1 + '/books?filter=' + json.dumps(filter_opts),
                            data=dict(data=json.dumps(src_update)))
        status = from_json(resp.data)['response']
        assert status == {STATUS_CODE: app.OK}

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        res = filter(lambda b: b['age'] == 50 and b['name'] == 'Pasha', books)
        assert len(res) == 1

    def test_update_filter3(self):
        src_update = {"age": 50, "cources.two": 5}
        filter_opts = {"age": {"$lt": 20}, "cources.one": {"$lt": 3}}
        resp = self.app.put(API_V1 + '/books?filter=' + json.dumps(filter_opts),
                            data=dict(data=json.dumps(src_update)))
        status = from_json(resp.data)['response']
        assert status == {STATUS_CODE: app.OK}

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        res = filter(lambda b: b['age'] == 50 and b['cources']['two'] == 5, books)
        assert len(res) == 2


    def test_update_newfield(self):
        src_update = {"new_field": 100}
        resp = self.app.put(API_V1 + '/books',
                            data=dict(data=json.dumps(src_update)))
        status = from_json(resp.data)['response']
        assert status == {STATUS_CODE: app.OK}

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
                            data=dict(data=json.dumps(src_update)))
        status = from_json(resp.data)['response']
        assert status == [{'1': app.OK}, {'2': app.OK}, {'5': app.OK}, {'not_existing': app.NOT_FOUND}]

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        for b in books:
            if b['_key'] in ['1', '2', '5', 'not_existing']:
                assert b['age'] == 50
            else:
                assert b['age'] != 50


class ApiDeleteManyCase(unittest.TestCase):
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
        self.app.post(API_V1 + '/books', data=dict(
            data='{"title": "Title1", "author": "author1", "age":10, "name":"Pasha"}'
        ), follow_redirects=True)
        self.app.post(API_V1 + '/books', data=dict(
            data='{"title": "Title2", "author": "author2", "age":20, "name":"Sasha"}'
        ), follow_redirects=True)
        self.app.post(API_V1 + '/books', data=dict(
            data='{"title": "Title3", "author": "author3", "age":15, "name":"Nikita"}'
        ), follow_redirects=True)
        self.app.post(API_V1 + '/books', data=dict(
            data='{"title": "Title4", "author": "author4", "age":10, "name":"Sasha"}'
        ), follow_redirects=True)
        self.app.post(API_V1 + '/books', data=dict(
            data='{"title": "Title4", "author": "author4", "age":15, "name":"Sasha"}'
        ), follow_redirects=True)

    def tearDown(self):
        storage._entities.drop()

    def test_delete_all_with_filter_opts(self):
        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 5

        resp = self.app.delete(API_V1 + '/books')
        status = from_json(resp.data)['response']
        assert status == app.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 0

    def test_delete_all_with_wrong_filter(self):
        resp = self.app.get(API_V1 + '/books?filter=all')
        assert from_json(resp.data)['error'] == {'message': 'Invalid json object "all"', 'code': app.BAD_REQUEST}

    def test_delete_two_by_age(self):
        filter_opts = '{"age":10}'
        resp = self.app.delete(API_V1 + '/books?filter=' + filter_opts)
        status = from_json(resp.data)['response']
        assert status == app.OK

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
        status = from_json(resp.data)['response']
        assert status == app.OK

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 4


    def test_delete_by_LT_filter(self):
        filter_opts = '{"age": { "$lt" : 15 }}'
        resp = self.app.delete(API_V1 + '/books?filter=' + filter_opts)
        status = from_json(resp.data)['response']
        assert status == app.OK

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
        status = from_json(resp.data)['response']
        assert status == app.OK

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
        status = from_json(resp.data)['response']
        assert status == app.OK

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
        status = from_json(resp.data)['response']
        assert status == app.OK

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
        error_code = from_json(resp.data)['response']
        assert error_code == app.NOT_FOUND

        resp = self.app.get(API_V1 + '/books')
        books = from_json(resp.data)['response']
        assert len(books) == 5


    def test_delete_with_broken_json(self):
        filter_opts = '{"age":10, name:"Sergey"all}'

        resp = self.app.delete(API_V1 + '/books?filter=' + filter_opts)
        resp = from_json(resp.data)
        expected = {
            'error': {STATUS_CODE: app.BAD_REQUEST, 'message': 'Invalid json object \"{"age":10, name:"Sergey"all}\"'}}
        assert resp == expected


    def test_delete_without_filter_opts(self):
        filter_opts = '{}'
        resp = self.app.delete(API_V1 + '/books?filter=' + filter_opts)
        resp = from_json(resp.data)
        print resp
        expected = {
            'error': {STATUS_CODE: app.BAD_REQUEST, 'message': 'Invalid request syntax. Filter options were not specified'}}
        assert resp == expected


class ApiSpecialEndpointsCase(unittest.TestCase):
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

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()