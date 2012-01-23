import base64
from datetime import datetime
import abc
from bson.binary import Binary
from bson.dbref import DBRef
from coltrane.appstorage import _internal_id, _external_key
from coltrane.appstorage.datatypes import Pointer, Blob, GeoPoint

__author__ = 'pshkitin'

class BaseConverter(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, obj):
        self.obj = obj

    @classmethod
    @abc.abstractmethod
    def to_internal(cls, key, ext_obj, *args, **kwargs):
        """Transform document from external format to internal"""
        raise NotImplementedError("This function must be performed in subclasses")

    @classmethod
    @abc.abstractmethod
    def to_external(cls, key, int_obj, *args, **kwargs):
        """Transform document from internal format to external"""
        raise NotImplementedError("This function must be performed in subclasses")


class PointerConverter(BaseConverter):

    @classmethod
    def to_internal(cls, key, pointer, *args, **kwargs):
        """
        :param key: document key,
        :param pointer: coltrane.appstorage.datatypes.Pointer
        :return: internal view of Pointer
        :rtype: :class:`DbRef`
        """
        bucket = pointer.bucket
        document_key = pointer.key
        id = _internal_id(*args, bucket=bucket, deleted=0, document_key=document_key)
        return key, DBRef(bucket, id)

    @classmethod
    def to_external(cls, key, dbref, *args, **kwargs):
        """
        :param key: document key,
        :param dbref: bson.dbref.DBRef
        :return: external view of DBRef
        :rtype: :class:`Pointer`
        """
        bucket = dbref.collection
        id = dbref.id
        document_key = _external_key(id)
        return key, Pointer(bucket, document_key)


class BlobConverter(BaseConverter):
    @classmethod
    def to_internal(cls, key, blob, *args, **kwargs):
        """
        :param key: document key,
        :param blob: coltrane.appstorage.datatypes.Blob
        :return: internal view of Blob
        :rtype: :class:`bson.binary.Binary`
        """
        data = base64.decodestring(blob.base64)
        return key, Binary(data)

    @classmethod
    def to_external(cls, key, binary, *args, **kwargs):
        """
        :param key: document key,
        :param binary: bson.binary.Binary
        :return: external view of binary data
        :rtype: :class:`Blob`
        """
        base64str = base64.encodestring(binary)
        return key, Blob(base64str)


class GeoPointConverter(BaseConverter):
    """This converter used for converting Pointer object into internal format PyMongo works with.
    Due to PyMongo has simple dict object format for geo point we need to make special structure of object:
    key whom object contains geo information should be prefixed with '__geo_ word'.
    We do it for ability to recognize geo data type when making fetching"""

    START_FOR_GEO_KEY = '__geo_'

    EARTH_RADIUS_KM = 6371.0
    EARTH_RADIUS_MILE = 3959.0

    #We need DIVISORS for transforming km and miles into radians which mongodb works only with
    # Formula for transforming: radians = unit / EARTH_RADIUS_UNIT
    DIVISORS = {GeoPoint.MAX_DISTANCE_IN_KM: EARTH_RADIUS_KM,
                GeoPoint.MAX_DISTANCE_IN_MILES: EARTH_RADIUS_MILE,
                GeoPoint.MAX_DISTANCE_IN_RADIANS: 1.0}

    def __init__(self, key, val):
        super(GeoPointConverter, self).__init__(val)
        self.key = key

    @classmethod
    def to_internal(cls, key, point, *args, **kwargs):
        """
        :param key: document key,
        :param point: coltrane.appstorage.datatypes.GeoPoint
        :return: internal view of geo point that corresponds special format
        :rtype: :class:`dict`
        """
        key = cls.START_FOR_GEO_KEY + key
        geo_data = {GeoPoint.LATITUDE: point.latitude,
                    GeoPoint.LONGITUDE: point.longitude}
        res = {}
        searching = point.searching
        if searching[GeoPoint.SEARCHING]:
            max_dist_type = searching.get(GeoPoint.MAX_DISTANCE_TYPE)
            if max_dist_type:
                divisor = cls.DIVISORS[max_dist_type]
                res[GeoPoint.MAX_DISTANCE] = searching[GeoPoint.MAX_DISTANCE] / divisor
            res[GeoPoint.NEAR_SPHERE] = geo_data
        else:
            res = geo_data
        return key, res

    @classmethod
    def to_external(cls, key, value, *args, **kwargs):
        """
        :param key: document key,
        :return: external view
        :rtype: :class:`coltrane.appstorage.datatypes.GeoPoint`
        """
        key = key[len(cls.START_FOR_GEO_KEY):]
        latitude = value.get(GeoPoint.LATITUDE)
        longitude = value.get(GeoPoint.LONGITUDE)
        value = GeoPoint(latitude, longitude)
        return key, value


# datetime is internal and external format simultaneously
# so we don't need any converters for that
MAPPING = ((DBRef, Pointer, PointerConverter),
           (Binary, Blob, BlobConverter),
           (dict, GeoPoint, GeoPointConverter),
           (datetime, datetime, None))


def try_get_geopoint_external_converter(key):
    """If key start with geo prefix than make geo point external converter"""
    if key.startswith(GeoPointConverter.START_FOR_GEO_KEY):
        return GeoPointConverter
    return None

def get_internal_converter(ext_obj):
    """
        :param ext_obj: coltrane.appstorage.datatypes.BaseType
        :return: converter for ext_obj
        :rtype: :class:`BaseConverter`
        """
    obj_class = ext_obj.__class__
    for v in MAPPING:
        if obj_class == v[1]:
            return v[2]
    return None


def get_external_converter(int_obj):
    """
        :param int_obj: internal date type such as datetime, DBRef, Binary, etc.
        :return: converter for int_obj
        :rtype: :class:`BaseConverter`
        """
    obj_class = int_obj.__class__
    for v in MAPPING:
        if obj_class == v[0]:
            return v[2]
    return None