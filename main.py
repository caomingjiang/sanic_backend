from apps import flask_app
from apps.auth.view import bp as auth_bp


flask_app.register_blueprint(auth_bp)


if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=9000)

