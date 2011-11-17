# -*- coding: utf-8 -*-
from app import create_app

app = create_app(dict_config=dict(
    DEBUG=True,
    MONGODB_DB = 'coltrane',
#   MONGODB_USERNAME
#   MONGODB_PASSWORD', None),
#   MONGODB_HOST', None),
#   MONGODB_PORT
))

if __name__ == '__main__':
    app.run(port=6002)