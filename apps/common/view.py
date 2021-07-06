import os
from flask import Blueprint, request, Response, send_file
from confs.config import UPLOAD_DIR, EXCEL_MODAL_DIR
from common.common import JsonResponse, login_required, view_exception
from common.common import get_new_file_name
from datetime import datetime
from common import data_validate
from db import CarInfo, CarTestInfo


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
        'url': f'{user_id}/{today}/{file_name}'
    }
    return JsonResponse.success(ret_data)


@bp.route('excel/modal/download/<file_name>', methods=['GET'])
@login_required
@view_exception(fail_msg="download_modal failed")
def download_modal(file_name):
    full_path = os.path.join(EXCEL_MODAL_DIR, file_name)
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
    full_path = os.path.join(UPLOAD_DIR, req_data.fp)
    if not os.path.exists(full_path):
        return JsonResponse.fail('文件不存在')
    return send_file(full_path)


@bp.route('car_info', methods=['GET'])
@login_required
@view_exception(fail_msg="common get_car_info failed", db_session=True)
def common_get_car_info(se):
    req_data = data_validate.CommonGetCarInfo(**request.args.to_dict())
    if req_data.car_id:
        car_obj = se.query(CarInfo).filter(CarInfo.id == req_data.car_id).first()
    else:
        car_obj = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
        if not car_obj:
            car_obj = se.query(CarInfo).first()
    if not car_obj:
        return JsonResponse.fail('请增加车型')
    car_test_obj = se.query(CarTestInfo).filter(
        CarTestInfo.car_info == car_obj, CarTestInfo.dev_stage == car_obj.dev_stage
    ).first()
    test_time = car_test_obj.test_time if car_test_obj else None
    ret_data = {
        'id': car_obj.id,
        'car_name': car_obj.car_name,
        'test_time': test_time.strftime('%Y-%m-%d %H:%M:%S') if test_time else '',
        'dev_stage': car_obj.dev_stage.name,
        'test_user': car_test_obj.test_user or ''
    }
    return JsonResponse.success(ret_data)
