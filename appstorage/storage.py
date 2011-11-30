__author__ = 'qweqwe'

import json

from datetime import datetime
from uuid import uuid4

from errors import *
from utils import Enum


class intf(Enum):
    APP_ID      = '__app_id__'
    USER_ID     = '__user_id__'
    BUCKET      = '__bucket__'
    ID          = '_id'
    DELETED     = '__deleted__'
    CREATED_AT  = '__created_at__'
    UPDATED_AT  = '__updated_at__'
    IP_ADDRESS  = '__ip_address__'

class extf(Enum):
    KEY         = '_key'
    BUCKET      = '_bucket'
    CREATED_AT  = '_created'


# internal constants
DICT_TYPE = type(dict())
DOCUMENT_ID_FORMAT = '{app_id}|{user_id}|{bucket}|{document_key}'



class AppdataStorage(object):

    def __init__(self, entities):
        """
            :param entities: MongoDB collection object
        """
        self.entities = entities

    def create(self, app_id, user_id, ip_address, document, bucket):
        """ Create operation for CRUD.
         Saves entity to db in this format:
         {
             app_id: $app_id,
             user_id: $user_id,
             bucket: $bucket,
             _id: $id
             $document
         }
         $document saves in root of document.
         Function creations new id and set it to _id field, when _id is not filled in user document.
         If user document's _id already exists, InvalidDocumentIdError will be raised.
         Parameters:
         app_id: String, application id
         user_id: String, user id
         document: Dict, user document
         bucket: String, document type (bucket)

         Returns key of inserted entity """

        # validations
        if app_id is None:
            raise InvalidAppIdError('app_id must be not null')
        if user_id is None:
            raise InvalidUserIdError('user_id must be not null')
        if document is None:
            raise InvalidDocumentError('Document must be not null')
        if type(document) is not DICT_TYPE:
            raise InvalidDocumentError('Document must be instance of dict type')


        # check if a key is already exists, if it isn't - generate new
        if extf.KEY in document:
            document_id = self._internal_id(app_id, user_id, bucket,
                                         document[extf.KEY])
            criteria = {intf.ID: document_id}
            if self._is_document_exists(criteria):
                raise InvalidDocumentKeyError(
                    'Document with key [%s] already exists' % document[extf.KEY])
        else:
         document_id = self._internal_id(app_id, user_id, bucket, uuid4())

        document = self._filter_ext_fields(document)
        # add required fields to document
        document[intf.ID] = document_id
        document[intf.APP_ID] = app_id
        document[intf.USER_ID] = user_id
        document[intf.CREATED_AT] = datetime.utcnow()
        document[intf.IP_ADDRESS] = ip_address
        document[intf.BUCKET] = bucket
        document[intf.DELETED] = False

        self.entities.insert(document)

        return self._external_key(document_id)


    def get(self, app_id, user_id, bucket, key):
        """ Read operation for CRUD service.
         Parameters:
         app_id: String, application id
         user_id: String, user id
         document_key: String, document key
         bucket: String, type of document

         Returns founded document or None if object not found """

        # validations
        if app_id is None:
            raise InvalidAppIdError('app_id must be not null')
        if user_id is None:
            raise InvalidUserIdError('user_id must be not null')
        if key is None:
            raise InvalidDocumentKeyError('document_key must be not null')

        # logic

        document_id = self._internal_id(app_id, user_id, bucket, key)
        res = self.entities.find_one({intf.ID: document_id, intf.DELETED: False})
        if res is None:
            return None

        return self._to_external(res)


    def find(self, app_id, user_id, bucket, filter_opts=None):
        if app_id is None:
            raise InvalidAppIdError('app_id must be not null')
        if user_id is None:
            raise InvalidUserIdError('user_id must be not null')

        criteria = self._generate_criteria(app_id, user_id, bucket,
                                        filter_opts=filter_opts)
        documents = list(self.entities.find(criteria))
        return map(self._to_external, documents)


    def update(self, app_id, user_id, ip_address, bucket, document,
                key=None, filter_opts=None):
        """ Update operation for CRUD.
            Parameters:
            app_id: String, application id
            user_id: String, user id
            document: Dict, document with given _id will be updated in db
            bucket: String, document type """

        # validations
        if app_id is None:
            raise InvalidAppIdError('app_id must be not null')
        if user_id is None:
            raise InvalidUserIdError('user_id must be not null')
        if document is None:
            raise InvalidDocumentError('Document for update cannot be null')
        if type(document) is not DICT_TYPE:
            raise InvalidDocumentError('Document must be instance of dict type')


        if key:
            criteria = self._generate_criteria(app_id, user_id, bucket,
                                               filter_opts={extf.KEY: key})
        else:
            criteria = self._generate_criteria(app_id, user_id, bucket,
                                               filter_opts=filter_opts)

        document_to_update = self._filter_int_fields(
            self._filter_ext_fields(document)
        )
        document_to_update[intf.IP_ADDRESS] = ip_address
        document_to_update[intf.UPDATED_AT] = datetime.utcnow()
        self.entities.update(criteria, {'$set': document_to_update}, multi=True)


    def delete(self, app_id, user_id, ip_address, bucket,
               key=None, filter_opts=None):

        # validations
        if app_id is None:
            raise InvalidAppIdError('app_id must be not null')
        if user_id is None:
            raise InvalidUserIdError('user_id must be not null')

        if key:
            criteria = self._generate_criteria(app_id, user_id, bucket,
                                                filter_opts={extf.KEY: key})
        else:
            criteria = self._generate_criteria(app_id, user_id, bucket,
                                               filter_opts=filter_opts)

        self.entities.update(
             criteria,
             {'$set': self._fields_to_update_on_delete(ip_address)},
             multi=True
        )



     #TODO: REFUCK this FUNC
    def is_document_exists(self, app_id, user_id, bucket, criteria=None):
        """ Function for the external performing
        """
        if criteria and extf.KEY in criteria:
            doc_id = self._internal_id(app_id, user_id, bucket,criteria[extf.KEY])
            kwargs = dict(document_id=doc_id)
        else:
            kwargs = dict(filter_opts=criteria)
        res_criteria = self._generate_criteria(app_id, user_id, bucket,**kwargs)
        return self._is_document_exists(res_criteria)


    def _is_document_exists(self, criteria):
         """ Function for the internal performing
             This function checks whether db contains document with specified id.
                Parameters:
                document_id: String, document id.
                Returns: True if document is exists with specified id and False if not."""

         if not criteria:
             raise RuntimeError('Criteria object must not be None')

         # query document with one field (_id) to decrease network traffic. It is necessary fields minimum.
         found =  self.entities.find_one(criteria,  fields=['_id'])
         if found:
             return True
         else:
             return False


    def _internal_id(self, app_id, user_id, bucket, document_key):
         return DOCUMENT_ID_FORMAT.format(app_id=app_id, user_id=user_id,
                                          bucket=bucket, document_key=document_key)


    def _external_key(self, internal_id):
         return '|'.join(substr for substr in internal_id.split('|')[3:])


    def _generate_criteria(self, app_id, user_id, bucket, document_id=None,
                           filter_opts=None):
        criteria = {
            intf.DELETED: False,
        }

        if document_id:
            criteria[intf.ID] = document_id
        else:
            criteria.update({
                intf.APP_ID: str(app_id),
                intf.USER_ID: str(user_id),
                intf.BUCKET: str(bucket),
            })

        if filter_opts:
            filter_opts = self._from_external_to_internal(filter_opts, app_id,
                                                          user_id, bucket)
            for opt_key in filter_opts.keys():
                criteria[opt_key] = filter_opts[opt_key]

        return criteria


    def _fields_to_update_on_delete(self, ip_address):
        return {
            intf.DELETED:True,
            intf.IP_ADDRESS:ip_address,
            intf.UPDATED_AT:datetime.utcnow()
        }


    def _to_external(self, document):
        if not document:
            return None

        external = self._filter_int_fields(document)
        external[extf.KEY] = self._external_key(document[intf.ID])
        external[extf.BUCKET]      = document[intf.BUCKET]
        external[extf.CREATED_AT]  = document[intf.CREATED_AT]

        return external


    def _filter_int_fields(self, document):
        """
        Filter out all internal fields
        """
        return {k: v for k, v in document.items()
                 if not k in intf.values()}


    def _filter_ext_fields(self, document):
        """
        Filter out all external fields
        """
        return {k: v for k, v in document.items()
                 if not k in extf.values()}


    def _from_external_to_internal(self, doc, app_id, user_id, bucket):
        """
        Convert document from external view to the internal.
        Deletes any internal fields at start.
        If document contains external fields, convert its values to the internal fields.
        """
        internal = {}
        doc = self._filter_int_fields(doc)
        for key in doc:
            if key not in extf.values():
                internal[key] = doc[key]
            else:
                if key == extf.BUCKET:
                    internal[intf.BUCKET] = doc[key]
                elif key == extf.CREATED_AT:
                    internal[intf.CREATED_AT] = doc[key]
                elif key == extf.KEY:
                    document_key = doc[key]
                    document_id = self._internal_id(app_id, user_id, bucket,
                                                    document_key)
                    internal[intf.ID] = document_id
        return internal


    def _assert_exists(self, bucket, criteria, document_key=None):
        if not self._is_document_exists(criteria):
            if document_key:
                raise DocumentNotFoundError(
                    message=DocumentNotFoundError.DOCUMENT_BY_KEY,
                    key=document_key, bucket=bucket
                )
            else:
                raise DocumentNotFoundError(criteria=json.dumps(criteria),
                                            bucket=bucket)
