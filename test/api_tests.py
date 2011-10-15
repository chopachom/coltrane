import unittest
from app import create_app

__author__ = 'Pasha'

class ApiTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app(dict_config=dict(
            DEBUG=False,
            TESTING=True
        ))
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_getAll_request(self):
        rv = self.app.get('/books/')
        print "Get all: " + rv.data
        #assert 'No entries here so far' in rv.data

    def test_getById_request(self):
        rv = self.app.get('/books/1')
        print "Get by id: " + rv.data

    def test_post_request(self):
        rv = self.app.post('/books/', data=dict(
            data='{"id":3, "title": "Title3", "author": "Pasha Shkitin"}'
        ), follow_redirects=True)
        print "Post1: " + rv.data

    def test_success_delete_request(self):
        rv = self.app.delete('/books/2')
        print "Success delete: " + rv.data

    def test_fail_delete_request(self):
        rv = self.app.delete('/books/4')
        print "Fail delete: " + rv.data

    def test_put_request(self):
        rv = self.app.put('/books/', data=dict(
            data='{"id":2, "title": "Title3", "author": "Vasya Shkitin"}'
        ), follow_redirects=True)
        print 'Put1: ' + rv.data
    
if __name__ == '__main__':
    unittest.main()