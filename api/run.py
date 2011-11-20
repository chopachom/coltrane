from app import create_app

__author__ = 'pshkitin'

if __name__ == '__main__':
    app = create_app(dict_config=dict(
        DEBUG=False
    ))
    app.run()