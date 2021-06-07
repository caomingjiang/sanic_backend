from flask import Blueprint
from common.common import JsonResponse, login_required, view_exception
from db import User

bp = Blueprint('admin', __name__, url_prefix='/api/v1/user/')


@bp.route('/<int:user_id>', methods=['GET'])
@login_required
@view_exception(fail_msg='get_user failed', db_session=True)
def get_user(user_id, se):
    user = se.query(User).filter(User.id == user_id).first()
    ret_data = {
        'account': user.account,
        'username': user.username,
        'create_time': user.create_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    return JsonResponse.success(ret_data)

