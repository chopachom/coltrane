from coltrane.appstorage import reservedf, extf

__author__ = 'pshkitin'

class BaseType(object):
    pass

class Pointer(BaseType):
    BUCKET = 'bucket'
    KEY = 'key'

    def __init__(self, bucket, key):
        self.bucket = bucket
        self.key = key

class Blob(BaseType):
    BASE64 = 'base64'

    def __init__(self, base64):
        self.base64 = base64

class GeoPoint(BaseType):
    NEAR_SPHERE = '$nearSphere' # key that should be set up for searching
    # max distance (radius) from start point.
    # Found points should be not more far from start point then $maxDistance
    MAX_DISTANCE = '$maxDistance'

    # key name of object containing all searching params
    SEARCHING = 'searching'

    # key name that contains max distance type (by km, mile, radians)
    MAX_DISTANCE_TYPE = 'search_type'

    MAX_DISTANCE_IN_MILES = '$maxDistanceInMiles'
    MAX_DISTANCE_IN_KM = '$maxDistanceInKilometers'
    MAX_DISTANCE_IN_RADIANS = '$maxDistanceInRadians'
    MAX_DISTANCES = (MAX_DISTANCE_IN_RADIANS, MAX_DISTANCE_IN_KM, MAX_DISTANCE_IN_MILES)

    LATITUDE = 'latitude' # key name for latitude that should be in GeoPoint object
    LONGITUDE = 'longitude' # key name for longitude that should be in GeoPoint object

    def __init__(self, latitude, longitude, searching=None):
        self.latitude = latitude
        self.longitude = longitude
        self.searching = searching