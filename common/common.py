from flask import jsonify, request
import hashlib
import functools
from confs.config import SECRET_KEY
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import string
import random
from common.loggers import code_log
from pydantic import ValidationError
import json
from db import Session


class JsonResponse:
    @staticmethod
    def fail(msg, code=-1):
        res = jsonify({
            "code": code,
            "msg": msg,
            "data": {}
        })
        if code == 401:
            return res, code
        else:
            return res

    @staticmethod
    def success(data=None, msg=""):
        res = jsonify({
            "code": 0,
            "msg": msg,
            "data": {} if data is None else data
        })
        return res


def get_md5(pwd):
    m2 = hashlib.md5()
    m2.update(pwd.encode("utf-8"))
    return m2.hexdigest()


def login_required(view_func):
    @functools.wraps(view_func)
    def verify_token(*args, **kwargs):
        try:
            # 在请求头上拿到token
            token = request.headers["token"]
        except Exception:
            # 没接收的到token,给前端抛出错误
            return JsonResponse.fail('未登录', code=401)

        s = Serializer(SECRET_KEY)
        try:
            ud = s.loads(token)
            user_id = ud.get('user_id')
            setattr(request, 'user_id', user_id)
        except Exception:
            return JsonResponse.fail("登录已过期", code=401)

        return view_func(*args, **kwargs)

    return verify_token


def get_new_file_name(old_file_name):
    randstr = ''.join(random.sample(string.ascii_letters + string.digits, 7))
    split_fs = old_file_name.rsplit('.', maxsplit=1)
    if len(split_fs) == 2:
        new_file_name = '{0}_{1}.{2}'.format(split_fs[0], randstr, split_fs[1])
    else:
        new_file_name = '{0}_{1}'.format(old_file_name, randstr)
    return new_file_name


def view_exception(*wargs, **wkwargs):
    # Project Imports
    def view_f(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            db_session = wkwargs.get('db_session', False)
            se = None
            try:
                if db_session:
                    se = Session()
                    return view_func(*args, **kwargs, se=se)
                else:
                    return view_func(*args, **kwargs)
            except ValidationError as e:
                valid_dic = json.loads(e.json())[0]
                msg = f"{' --> '.join(valid_dic['loc'])}: {valid_dic['msg']}"
                req_data = json.dumps(request.args.to_dict(), ensure_ascii=False) if \
                    request.method == 'GET' else json.dumps(request.json, ensure_ascii=False)
                code_log.error(f'url: {request.path}, method: {request.method}, req_data: {req_data}, error_msg: {msg}')
                return JsonResponse.fail(msg)
            except Exception:
                code_log.exception(wkwargs["fail_msg"])
                return JsonResponse.fail("系统错误，请联系管理员")
            finally:
                if db_session:
                    se.close()
        return wrapper
    return view_f


def get_orm_comment_dic(base_model):
    ret_data = {}
    for column in base_model.__table__.columns:
        comment = getattr(base_model, column.name).comment
        if comment:
            ret_data[comment] = column.name
    return ret_data

