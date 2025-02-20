import os
from flask import Blueprint, request, Response, send_file
from confs.config import env_config
from common.common import JsonResponse, login_required, view_exception
from common.common import get_new_file_name
from datetime import datetime
from common import data_validate
from db import CarInfo, CarTestInfo, DataConfigs


bp = Blueprint('common', __name__, url_prefix='/api/v1/common/')


@bp.route('upload', methods=['POST'])
@login_required
@view_exception(fail_msg="upload_file failed")
def upload_file():
    user_id = getattr(request, 'user_id')
    file = request.files.get('file')
    file_name = get_new_file_name(file.filename)
    today = datetime.now().strftime('%Y%m%d')
    save_dir = os.path.join(env_config.UPLOAD_DIR, str(user_id), today)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    file_path = os.path.join(save_dir, file_name)
    file.save(file_path)
    ret_data = {
        'name': file.filename,
        'url': f'{user_id}/{today}/{file_name}'
    }
    return JsonResponse.success(ret_data)


@bp.route('excel/modal/download/<file_name>', methods=['GET'])
@login_required
@view_exception(fail_msg="download_modal failed")
def download_modal(file_name):
    full_path = os.path.join(env_config.EXCEL_MODAL_DIR, file_name)
    # with open(full_path, 'rb+') as f:
    #     ret_value = f.read()
    # response = Response(ret_value, content_type='application/octet-stream')
    # response.headers['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name.encode().decode("latin1"))
    # return response
    return send_file(full_path)


@bp.route('media', methods=['GET'])
@login_required
@view_exception(fail_msg="download_file failed")
def download_file():
    req_data = data_validate.DownloadFileParams(**request.args.to_dict())
    full_path = os.path.join(env_config.UPLOAD_DIR, req_data.fp)
    if not os.path.exists(full_path):
        return JsonResponse.fail('文件不存在')
    return send_file(full_path)


@bp.route('bs_type_selects', methods=['GET'])
@login_required
@view_exception(fail_msg="common get_bs_type_selects failed")
def common_get_bs_type_selects():
    ret_data = dict(DataConfigs.BS_TYPE_CHOICES)
    return JsonResponse.success(ret_data)
