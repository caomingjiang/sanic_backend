from apps import flask_app
from scripts.init_data import init_main
from apps.auth.view import bp as auth_bp
from apps.user.view import bp as user_bp
from apps.home.view import bp as home_bp
from apps.single_data.view import bp as single_data_bp
from gevent import monkey
monkey.patch_all()


flask_app.register_blueprint(auth_bp)
flask_app.register_blueprint(user_bp)
flask_app.register_blueprint(home_bp)
flask_app.register_blueprint(single_data_bp)

init_main()


if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=9000)

