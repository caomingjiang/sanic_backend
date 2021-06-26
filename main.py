from apps import flask_app
from scripts.init_data import init_main
from apps.auth.view import bp as auth_bp
from apps.user.view import bp as user_bp
from apps.home.view import bp as home_bp
from apps.single_data.view import bp as single_data_bp
from apps.freq_data.view import bp as freq_data_bp
from apps.common.view import bp as common_bp
from apps.car_body.view import bp as car_body_bp
from apps.color_map.view import bp as color_map_bp
from apps.design_library.view import bp as design_library_bp
from apps.weight_settings.view import bp as weight_settings_bp
from gevent import monkey
monkey.patch_all()


flask_app.register_blueprint(auth_bp)
flask_app.register_blueprint(user_bp)
flask_app.register_blueprint(home_bp)
flask_app.register_blueprint(single_data_bp)
flask_app.register_blueprint(freq_data_bp)
flask_app.register_blueprint(common_bp)
flask_app.register_blueprint(car_body_bp)
flask_app.register_blueprint(color_map_bp)
flask_app.register_blueprint(design_library_bp)
flask_app.register_blueprint(weight_settings_bp)

init_main()


if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=9000)

