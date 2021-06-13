import os
from flask import Blueprint, request
from confs.config import UPLOAD_DIR
from common.common import JsonResponse, login_required, view_exception
from common.common import get_new_file_name
from datetime import datetime


bp = Blueprint('common', __name__, url_prefix='/api/v1/common/')


@bp.route('upload', methods=['POST'])
@login_required
@view_exception(fail_msg="upload_file failed")
def upload_file():
    user_id = getattr(request, 'user_id')
    file = request.files.get('file')
    file_name = get_new_file_name(file.filename)
    today = datetime.now().strftime('%Y%m%d')
    save_dir = os.path.join(UPLOAD_DIR, str(user_id), today)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    file_path = os.path.join(save_dir, file_name)
    file.save(file_path)
    ret_data = {
        'name': file.filename,
        'url': f'/media/{user_id}/{today}/{file_name}'
    }
    return JsonResponse.success(ret_data)

