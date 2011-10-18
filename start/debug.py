from app import create_app

if __name__ == '__main__':
    app = create_app(dict_config=dict(
        DEBUG=True
    ))
    app.run()