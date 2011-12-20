""" Run app in DEBUG mode with STUB version of Guard module. """

from app import create_app
from config import DebugConfig
from coltrane.rest.api import api_v1, v1
from coltrane.rest.extensions import mongodb

__author__ = 'nik'

if __name__ == '__main__':

    v1.get_app_id = lambda : 'dbg_app_id'
    v1.get_remote_ip = lambda : '127.0.0.1'
    v1.get_user_id = lambda : 'dbg_user_id'

    app = create_app(
        modules=((api_v1, '/v1'),),
        exts=(mongodb,),
        config=DebugConfig
    )
    app.run(debug=True)