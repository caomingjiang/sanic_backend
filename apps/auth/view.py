from flask import request, Blueprint, redirect
from common.common import get_md5, JsonResponse, login_required, view_exception
from common import data_validate
from db import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from confs.config import env_config
from datetime import datetime, timedelta

bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth/')


@bp.route('login', methods=['POST'])
@view_exception(fail_msg='login failed', db_session=True)
def login(se):
    req_data = data_validate.LoginValidate(**request.json)

    db_user = se.query(User).filter(User.account == req_data.account).first()
    if not db_user:
        return JsonResponse.fail("该账号不存在")

    if db_user.password == get_md5(req_data.password):
        s = Serializer(env_config.SECRET_KEY, expires_in=env_config.TOKEN_EXPIRES)
        token = s.dumps({'user_id': db_user.id}).decode()
        create_time = db_user.create_time.strftime('%Y-%m-%d %H:%M:%S')
        ret_data = {
            'token': token,
            'user_info': {
                'account': req_data.account,
                'username': db_user.username,
                'role_code': db_user.role.code,
                'user_id': db_user.id,
                'create_time': create_time
            }
        }
        return JsonResponse.success(ret_data)
    else:
        return JsonResponse.fail("密码错误")


# @bp.route('register', methods=['POST'])
# def register():
#     s = db_session()
#     try:
#         account = request.json.get("account", "")  # 登录账号
#         username = request.json.get("username", "")  # 用户姓名
#         status = request.json.get("status", "0")  # 用户状态
#         password = request.json.get("password", "")  # 密码
#         role_id = request.json.get("role_id", 0)  # 角色
#
#         if not all([account, username, status, password, role_id]):
#             return JsonResponse.fail("登录账号、用户姓名、用户状态、密码、角色不能为空")
#
#         exists = s.query(User).filter(User.account == account).first()
#         if exists:
#             return JsonResponse.fail(f"{account}已被注册")
#
#         new_user = User(
#             account=account, username=username, status=status, password=get_md5(password), role_id=role_id
#         )
#         s.add(new_user)
#         s.commit()
#         return JsonResponse.success()
#     finally:
#         s.close()


@bp.route('update_pwd', methods=['POST'])
@login_required
@view_exception(fail_msg='update_pwd failed', db_session=True)
def update_pwd(se):
    req_data = data_validate.UpdateUserPassword(**request.json)
    user_id = getattr(request, 'user_id')

    user_obj = se.query(User).filter(User.id == user_id).first()
    if get_md5(req_data.old_pwd) != user_obj.password:
        return JsonResponse.fail('当前密码错误!')
    else:
        user_obj.password = get_md5(req_data.new_pwd)
        user_obj.update_time = datetime.now()
        se.commit()
    return JsonResponse.success()

