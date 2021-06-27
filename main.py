from apps import flask_app
from scripts.init_data import init_main
from apps.auth.view import bp as auth_bp
from apps.user.view import bp as user_bp
from apps.home.view import bp as home_bp
from apps.common.view import bp as common_bp
from apps.single_data.single_data.view import bp as single_data_bp
from apps.single_data.freq_data.view import bp as freq_data_bp
from apps.single_data.car_body.view import bp as car_body_bp
from apps.state_conclusion.color_map.view import bp as color_map_bp
from apps.expert_setting.design_library.view import bp as design_library_bp
from apps.expert_setting.weight_settings.view import bp as weight_settings_bp
from apps.expert_setting.atic_pkg_confs.view import bp as atic_pkg_confs_bp
from apps.single_data.acoustic_package.view import bp as acoustic_package_bp
from apps.expert_setting.single_data_confs.view import bp as single_data_confs_bp
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
flask_app.register_blueprint(atic_pkg_confs_bp)
flask_app.register_blueprint(acoustic_package_bp)
flask_app.register_blueprint(single_data_confs_bp)

init_main()


if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=9000)

