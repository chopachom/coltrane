import unittest
from coltrane.appstorage import reservedf
from coltrane.rest.exceptions import InvalidKeyNameError, InvalidDocumentFieldsError
from coltrane.rest.validators import SimpleValidator, RecursiveValidator, UpdateDocumentKeysValidator, SaveDocumentKeysValidator, FilterKeysValidator
from coltrane.appstorage.storage import intf, extf

__author__ = 'Pasha'

class SimpleValidatorTestCase(unittest.TestCase):

    def test_simple1(self):
        doc = {'a': 10, reservedf.BUCKET: 'bucket', 'b': 20, extf.KEY: 'key'}
        fields = intf + extf + reservedf.values()
        valid = SimpleValidator(doc, fields)

        try:
            valid.validate()
        except Exception, e:
            assert e.message == 'Document contains forbidden fields [%s,%s]' % \
                                (extf.KEY, reservedf.BUCKET)

    def test_chain(self):
        doc = {'a': 10, reservedf.BUCKET: 'bucket', 'b': 20, extf.KEY: 'key'}
        valid1 = SimpleValidator(doc, extf.values())
        valid2 = SimpleValidator(doc, reservedf.values(), valid1)

        try:
            valid2.validate()
        except Exception, e:
            assert e.message == 'Document contains forbidden fields [%s,%s]' % \
                                (extf.KEY, reservedf.BUCKET)

    def test_no_duplicate_fields(self):
        doc = {'a': 10, 'd': 'bucket', 'b': 20, extf.KEY: 'key'}
        valid1 = SimpleValidator(doc, extf.values())
        valid2 = SimpleValidator(doc, extf.values(), valid1)
        try:
            valid2.validate()
        except Exception, e:
            assert e.message == 'Document contains forbidden fields [%s]' % extf.KEY

    def test_fields_not_found(self):
        doc = {'a': 10, 'd': 'bucket', 'b': 20, extf.KEY: 'key'}
        valid = SimpleValidator(doc, intf.values())
        valid.validate()


class RecursiveValidatorTestCase(unittest.TestCase):

    def test_simple1(self):
        doc = {'a': 10, 'd': {'bucket': {reservedf.BUCKET: 'yes!!!'}}, 'b': 20, extf.KEY: 'key'}
        fields = extf + intf + reservedf.values()
        valid = RecursiveValidator(doc, fields)

        try:
            valid.validate()
        except Exception, e:
            assert e.message == 'Document contains forbidden fields [%s,%s]' % \
                                (extf.KEY, reservedf.BUCKET)

    def test_chain_and_duplicate(self):
        doc = {'a': 10, 'd': {'bucket': {reservedf.BUCKET: 'yes!!!'}},
               'b': 20, extf.KEY: 'key',
               'd2': {'bucket2': {reservedf.BUCKET: 'no!!!'}},
               'd3': {'bucket3': {reservedf.BUCKET: 'yes!!!'}}}
        valid1 = RecursiveValidator(doc, intf.values())
        valid2 = RecursiveValidator(doc, extf.values(), valid1)
        valid3 = RecursiveValidator(doc, reservedf.values(), valid2)

        try:
            valid3.validate()
        except Exception, e:
            assert e.message == 'Document contains forbidden fields [%s,%s]' % \
                                (extf.KEY, reservedf.BUCKET)

    def test_forbidden(self):
        filter = {'$and': [{'_id': {'$gt': 20}}, {'_id': {'$lt': 80}, 'a':[1,2, {'$where':1}]}]}
        with self.assertRaises(InvalidDocumentFieldsError) as context:
            RecursiveValidator(filter, ['_id', '$where']).validate()
        assert context.exception.message == 'Document contains forbidden fields [_id,$where]'


    def test_fields_not_found(self):
        doc = {'a': 10, 'd': {'bucket': {reservedf.BUCKET: 'yes!!!'}},
               'b': 20, 'done': 'key',
               'd2': {'bucket2': {reservedf.BUCKET: 'no!!!'}},
               'd3': {'bucket3': {reservedf.BUCKET: 'yes!!!'}}}
        valid1 = SimpleValidator(doc, extf.values())
        valid2 = SimpleValidator(doc, extf.values(), valid1)
        valid2.validate()

        
class MixedValidationTestCase(unittest.TestCase):

    def test_chain_and_duplicate(self):
        doc = {'a': 10, 'd': {'bucket': {reservedf.BUCKET: 'yes!!!'}},
               'b': 20, extf.KEY: 'key',
               'd2': {'bucket2': {reservedf.BUCKET: 'no!!!'}},
               'd3': {'bucket3': {reservedf.BUCKET: 'yes!!!'}}}
        valid1 = RecursiveValidator(doc, reservedf.values())
        valid2 = SimpleValidator(doc, extf.values(), valid1)
        valid3 = RecursiveValidator(doc, intf.values(), valid2)

        try:
            valid3.validate()
        except Exception, e:
            assert e.message == 'Document contains forbidden fields [%s,%s]' % \
                                (extf.KEY, reservedf.BUCKET)

    def test_fields_not_found(self):
        doc = {'a': 10, 'd': {'bucket': {'a': 'yes!!!'}},
               'b': 20, 's': {extf.KEY: 'key'},
               'd2': {'bucket2': {'a': 'no!!!'}},
               'd3': {'bucket3': {reservedf.BUCKET: 'yes!!!'}}}
        valid1 = RecursiveValidator(doc, intf.values())
        valid2 = SimpleValidator(doc, reservedf.values(), valid1)
        valid3 = RecursiveValidator(doc, intf.values(), valid2)
        valid3.validate()


class KeyValidationTestCase(unittest.TestCase):

    def test_key_save_doc_validation(self):
        doc = {'__a_': 1, '_b___c_': 10}
        with self.assertRaises(InvalidKeyNameError) as context:
            SaveDocumentKeysValidator(doc).validate()
        assert context.exception.message == 'Document key has invalid format [__a_]'

        doc = {'__a_': 1, '_b___c_': 10, 'c':{'d':{'e':{'__i__':5}}}}
        with self.assertRaises(InvalidKeyNameError) as context:
            SaveDocumentKeysValidator(doc).validate()
        assert context.exception.message == 'Document key has invalid format [__i__,__a_]'


    def test_key_filter_doc_validation(self):
        filter = {'b.b.c': {'_d': {'e__': 10}}}
        with self.assertRaises(InvalidKeyNameError) as context:
            FilterKeysValidator(filter).validate()
        assert context.exception.message == 'Document key has invalid format [e__]'


    def test_key_update_doc_validation(self):
        doc = {'a.b.c': 3}
        UpdateDocumentKeysValidator(doc).validate()

        doc = {'a.b.c': 3, 'b': {'c': {'__sa-6767_': [10, 10]}}}
        with self.assertRaises(InvalidKeyNameError) as context:
            UpdateDocumentKeysValidator(doc).validate()
        assert context.exception.message == 'Document key has invalid format [__sa-6767_]'


    def test_strong_key_validation(self):
        doc = {'a.b.c': [[{'key^2':2}, {'a':2}],{'__key':2}]}
        with self.assertRaises(InvalidKeyNameError) as context:
            UpdateDocumentKeysValidator(doc).validate()
        assert context.exception.message == 'Document key has invalid format [__key,key^2]'


if __name__ == '__main__':
    unittest.main()