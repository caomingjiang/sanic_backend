import flask
from flask_cors import CORS
from confs.config import BASE_DIR
from flask import request
from common.loggers import access_log
import time

flask_app = flask.Flask(__name__, root_path=BASE_DIR)
CORS(flask_app, supports_credentials=True)
flask_app.jinja_env.auto_reload = True


@flask_app.before_request
def before_request():
    setattr(request, 'start_time', time.time())


@flask_app.after_request
def after_request(response):
    if request.method == "OPTIONS":
        return response

    status_code = response.status_code
    request_time = int(1000 * (time.time() - getattr(request, 'start_time', 0)))
    r_ips = request.access_route
    remote_ip = r_ips[0] if r_ips else request.remote_addr
    method = request.method
    request_url = request.path
    if method == 'GET' and request.args:
        params_list = list()
        for key in request.args:
            params_list.append(key + '=' + request.args[key])
        request_url += '?' + '&'.join(params_list)
    access_log.info("{0} {1}ms {2} {3} {4}".format(str(status_code), str(request_time), request.method, request_url, remote_ip))
    return response