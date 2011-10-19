import storage
import unittest
from app import create_app


class StorageTestCase(unittest.TestCase):

    def setUp(self):
        storage.get_app_id = lambda : u'TheAppID'
        storage.get_user_id = lambda : u'TheUserId'
        self.app  = create_app(dict_config=dict(
            DEBUG=True
        ))
        self.ctx = self.app.test_request_context('/')
        self.ctx.push()
        self.bucket = u'bucket1'

    def test_create_and_read_documents(self):
        data = {'author': 'qweqwe'}
        key = storage.save(bucket=self.bucket, document=data)
        doc = storage.get(bucket=self.bucket, key=key)
        assert doc[u'_id'] == key
        assert doc[u'author'] == u'qweqwe'


    def test_delete_document(self):
        data = {'author': 'qweqwe'}
        key = storage.save(bucket=self.bucket, document=data)
        storage.delete(bucket=self.bucket, key=key)
        doc = storage.get(bucket=self.bucket, key=key)
        print doc
        assert doc is None