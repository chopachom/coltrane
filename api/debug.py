from app import create_app
from config import DebugConfig


__author__ = 'pshkitin'

if __name__ == '__main__':
    app = create_app(config=DebugConfig)
    app.run()