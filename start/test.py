import unittest
from app import create_app
from db.crud import crud

__author__ = 'pshkitin'

class AppTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app(exts=(crud,), dict_config=dict(
            DEBUG=True,
            TESTING=True
        ))
        app.test_client()

#    def tearDown(self):
#        os.close(self.db_fd)
#        os.unlink(flaskr.app.config['DATABASE'])

#with app.test_request_context('/hello', method='POST'):
#    # now you can do something with the request until the
#    # end of the with block, such as basic assertions:
#    assert request.path == '/hello'
#    assert request.method == 'POST'
#
#if __name__ == '__main__':
#    app = create_app(dict_config=dict(
#        DEBUG=True
#    ))
#    app.run()

if __name__ == '__main__':
    unittest.main()