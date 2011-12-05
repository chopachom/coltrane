# -*- coding: utf-8 -*-
from app import create_app
from config import DebugConfig

app = create_app(config=DebugConfig)

if __name__ == '__main__':
    app.run(port=6002)