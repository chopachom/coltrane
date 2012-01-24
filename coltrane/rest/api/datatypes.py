import abc
from datetime import datetime as dt
from functools import wraps
from coltrane.appstorage import try_convert_to_date, reservedf
from coltrane.appstorage.datatypes import Pointer, Blob, GeoPoint
from coltrane.rest import exceptions
from coltrane.utils import traverse, Enum

__author__ = 'pshkitin'

TYPE_FIELD = '_type'

class type_codes(Enum):
    DATE = 'Date'
    POINTER = 'Pointer'
    GEO_POINT = 'GeoPoint'
    BLOB = 'Blob'


class BaseCaster(object):
    __metaclass__ = abc.ABCMeta

    @classmethod
    @abc.abstractmethod
    def serialize(cls, key, obj):
        """For transforming data from external document format to JSON format"""
        raise NotImplementedError("This function must be performed in subclasses")

    @classmethod
    @abc.abstractmethod
    def deserialize(cls, obj):
        """For transforming data from JSON format to external document"""
        raise NotImplementedError("This function must be performed in subclasses")


class DateCaster(BaseCaster):
    @classmethod
    def serialize(cls, key, date):
        """
        :param date: python datetime object,
        :return: datetime iso format
        """
        iso = date.isoformat()
        if key in reservedf.values():
            return iso
        return {TYPE_FIELD: type_codes.DATE, 'iso': iso}

    @classmethod
    def deserialize(cls, obj):
        """Try convert string object into datetime python object."""
        return try_convert_to_date(obj.get('iso'))


class PointerCaster(BaseCaster):
    @classmethod
    def serialize(cls, key, pointer):
        """
        :param pointer: coltrane.appstorage.datatypes.Pointer,
        :return: pointer view for client
        """
        pview = {TYPE_FIELD: type_codes.POINTER,
                 Pointer.BUCKET: pointer.bucket, Pointer.KEY: pointer.key}
        return pview

    @classmethod
    def deserialize(cls, obj):
        bucket = obj.get(Pointer.BUCKET)
        key = obj.get(Pointer.KEY)
        if not bucket or not key:
            raise exceptions.InvalidRequestError(
                'For Date type you should pass bucket and key fields')
        return Pointer(bucket, key)

class BlobCaster(BaseCaster):
    @classmethod
    def serialize(cls, key, blob):
        """
        :param blob: coltrane.appstorage.datatypes.Blob,
        :return: blob view for client
        """
        bview = {TYPE_FIELD: type_codes.BLOB,
                 Blob.BASE64: blob.base64}
        return bview

    @classmethod
    def deserialize(cls, obj):
        base64 = obj.get(Blob.BASE64)
        if not base64:
            raise exceptions.InvalidRequestError(
                'For Blob type you should pass base64 string field')
        return Blob(base64)


class GeoPointCaster(BaseCaster):
    @classmethod
    def serialize(cls, key, geo_point):
        """
        :param geo_point: coltrane.appstorage.datatypes.GeoPoint,
        :return: geo point view for client
        """
        gp_view = {TYPE_FIELD: type_codes.GEO_POINT,
                 GeoPoint.LATITUDE: geo_point.latitude,
                 GeoPoint.LONGITUDE: geo_point.longitude}
        return gp_view

    @classmethod
    def deserialize(cls, obj):
        searching = {GeoPoint.SEARCHING: False}
        if GeoPoint.NEAR_SPHERE in obj:
            searching[GeoPoint.SEARCHING] = True # setting flag up signalling about searching but not saving or put
            for max_dist in GeoPoint.MAX_DISTANCES:
                if max_dist in obj:
                    searching[GeoPoint.MAX_DISTANCE_TYPE] = max_dist # set up max distance type (km, miles, radians)
                    searching[GeoPoint.MAX_DISTANCE] = obj[max_dist] # set up max distance value
            obj = obj.get(GeoPoint.NEAR_SPHERE)  # here we have geo params under $nearSphere key
        latitude = obj.get(GeoPoint.LATITUDE)  # if it is not searching request then geo params are in top level
        longitude = obj.get(GeoPoint.LONGITUDE)
        if not latitude or not longitude:
            raise exceptions.InvalidRequestError(
                'For GeoPoint type you should pass latitude and longitude fields')
        return GeoPoint(latitude, longitude, searching)

SERIALISATORS = {
    dt: DateCaster,
    Pointer: PointerCaster,
    Blob: BlobCaster,
    GeoPoint: GeoPointCaster,
}

DESERIALISATORS = {
    type_codes.DATE: DateCaster,
    type_codes.POINTER: PointerCaster,
    type_codes.BLOB: BlobCaster,
    type_codes.GEO_POINT: GeoPointCaster
}

def serialize(f):
    def walker(key, value):
        caster = serialisator(value)
        if caster:
            return key, caster.serialize(key, value)

    @wraps(f)
    def wrapper(*args, **kwargs):
        resp = f(*args, **kwargs)
        body, code = resp
        return traverse(body, walker), code
    return wrapper


def deserialize(obj):
    def walker(key, value):
        if isinstance(value, dict):
            caster = deserialisator(value)
            if caster:
                return key, caster.deserialize(value)
    return traverse(obj, walker)


def serialisator(obj):
    """
    :param obj: external obj to serialize,
    :return: special caster
    :rtype: :class:`BaseCaster`
    """
    return SERIALISATORS.get(obj.__class__)


def deserialisator(obj):
    """
    :param obj: external obj to deserialize,
    :return: special type caster
    :rtype: :class:`BaseCaster`
    """
    if GeoPoint.NEAR_SPHERE in obj:
        obj = obj.get(GeoPoint.NEAR_SPHERE)
        if type(obj) is not dict:
            return None
    if TYPE_FIELD in obj:
        return DESERIALISATORS.get(obj[TYPE_FIELD])

