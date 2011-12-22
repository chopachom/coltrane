from coltrane.appstorage.storage import intf
from coltrane.utils import Enum

__author__ = 'pshkitin'

class resp_msgs(Enum):
    DOC_NOT_EXISTS  = "Document doesn't exist"
    DOC_WAS_CREATED = "Document was created"
    DOC_WAS_DELETED = "Document was deleted"
    DOC_WAS_UPDATED = "Document was updated"
    INTERNAL_ERROR  = "Internal server error"


class forbidden_fields(Enum):
    WHERE      = '$where'
    ID         = intf.ID