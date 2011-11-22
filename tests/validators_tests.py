import unittest
from api.validators import SimpleValidator, RecursiveValidator
from ds.storage import int_fields, ext_fields

__author__ = 'Pasha'

class SimpleValidatorTestCase(unittest.TestCase):

    def test_simple1(self):
        doc = {'a': 10, int_fields.BUCKET: 'bucket', 'b': 20, ext_fields.KEY: 'key'}
        fields = int_fields + ext_fields
        valid = SimpleValidator(doc, fields)

        try:
            valid.validate()
        except Exception, e:
            assert e.message == 'Document contains forbidden fields [%s,%s]' % \
                                (int_fields.BUCKET, ext_fields.KEY)

    def test_chain(self):
        doc = {'a': 10, int_fields.BUCKET: 'bucket', 'b': 20, ext_fields.KEY: 'key'}
        valid1 = SimpleValidator(doc, ext_fields.values())
        valid2 = SimpleValidator(doc, int_fields.values(), valid1)

        try:
            valid2.validate()
        except Exception, e:
            assert e.message == 'Document contains forbidden fields [%s,%s]' % \
                                (int_fields.BUCKET, ext_fields.KEY)

    def test_no_duplicate_fields(self):
        doc = {'a': 10, 'd': 'bucket', 'b': 20, ext_fields.KEY: 'key'}
        valid1 = SimpleValidator(doc, ext_fields.values())
        valid2 = SimpleValidator(doc, ext_fields.values(), valid1)
        try:
            valid2.validate()
        except Exception, e:
            assert e.message == 'Document contains forbidden fields [%s]' % ext_fields.KEY

    def test_fields_not_found(self):
        doc = {'a': 10, 'd': 'bucket', 'b': 20, ext_fields.KEY: 'key'}
        valid = SimpleValidator(doc, int_fields.values())
        valid.validate()


class RecursiveValidatorTestCase(unittest.TestCase):

    def test_simple1(self):
        doc = {'a': 10, 'd': {'bucket': {int_fields.BUCKET: 'yes!!!'}}, 'b': 20, ext_fields.KEY: 'key'}
        fields = ext_fields + int_fields
        valid = RecursiveValidator(doc, fields)

        try:
            valid.validate()
        except Exception, e:
            assert e.message == 'Document contains forbidden fields [%s,%s]' % \
                                (ext_fields.KEY, int_fields.BUCKET)

    def test_chain_and_duplicate(self):
        doc = {'a': 10, 'd': {'bucket': {int_fields.BUCKET: 'yes!!!'}},
               'b': 20, ext_fields.KEY: 'key',
               'd2': {'bucket2': {int_fields.BUCKET: 'no!!!'}},
               'd3': {'bucket3': {ext_fields.BUCKET: 'yes!!!'}}}
        valid1 = RecursiveValidator(doc, int_fields.values())
        valid2 = RecursiveValidator(doc, ext_fields.values(), valid1)
        valid3 = RecursiveValidator(doc, int_fields.values(), valid2)

        try:
            valid3.validate()
        except Exception, e:
            assert e.message == 'Document contains forbidden fields [%s,%s,%s]' % \
                                (int_fields.BUCKET, ext_fields.KEY, ext_fields.BUCKET)

    def test_fields_not_found(self):
        doc = {'a': 10, 'd': {'bucket': {int_fields.BUCKET: 'yes!!!'}},
               'b': 20, 'done': 'key',
               'd2': {'bucket2': {int_fields.BUCKET: 'no!!!'}},
               'd3': {'bucket3': {int_fields.BUCKET: 'yes!!!'}}}
        valid1 = SimpleValidator(doc, ext_fields.values())
        valid2 = SimpleValidator(doc, ext_fields.values(), valid1)
        valid2.validate()

        
class MixedValidationTestCase(unittest.TestCase):

    def test_chain_and_duplicate(self):
        doc = {'a': 10, 'd': {'bucket': {int_fields.BUCKET: 'yes!!!'}},
               'b': 20, ext_fields.KEY: 'key',
               'd2': {'bucket2': {int_fields.BUCKET: 'no!!!'}},
               'd3': {'bucket3': {ext_fields.BUCKET: 'yes!!!'}}}
        valid1 = RecursiveValidator(doc, int_fields.values())
        valid2 = SimpleValidator(doc, ext_fields.values(), valid1)
        valid3 = RecursiveValidator(doc, int_fields.values(), valid2)

        try:
            valid3.validate()
        except Exception, e:
            assert e.message == 'Document contains forbidden fields [%s,%s]' % \
                                (int_fields.BUCKET, ext_fields.KEY)

    def test_fields_not_found(self):
        doc = {'a': 10, 'd': {'bucket': {'a': 'yes!!!'}},
               'b': 20, 's': {ext_fields.KEY: 'key'},
               'd2': {'bucket2': {'a': 'no!!!'}},
               'd3': {'bucket3': {ext_fields.BUCKET: 'yes!!!'}}}
        valid1 = RecursiveValidator(doc, int_fields.values())
        valid2 = SimpleValidator(doc, ext_fields.values(), valid1)
        valid3 = RecursiveValidator(doc, int_fields.values(), valid2)
        valid3.validate()


if __name__ == '__main__':
    unittest.main()