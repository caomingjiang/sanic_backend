from flask import Blueprint, request
from apps.expert_setting.atic_pkg_confs.control import AticPkgConfsData, get_current_car_file_data
from common.common import JsonResponse, login_required, view_exception
from db import CarInfo, SCarFileData
from common import data_validate
from datetime import datetime

bp = Blueprint('atic_pkg_confs', __name__, url_prefix='/api/v1/atic_pkg_confs/')


@bp.route('data', methods=['GET'])
@login_required
@view_exception(fail_msg='get_atic_pkg_confs_data failed', db_session=True)
def get_atic_pkg_confs_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')
    ret_data = get_current_car_file_data(se, car_info)
    return JsonResponse.success(ret_data)


@bp.route('data', methods=['POST'])
@login_required
@view_exception(fail_msg='save_atic_pkg_confs_data failed', db_session=True)
def save_atic_pkg_confs_data(se):
    req_data = data_validate.SaveAticPkgConfsData(**request.json)
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')

    file_name = req_data.name
    file_path = req_data.url
    save_obj = AticPkgConfsData(file_path, car_info.id, se)
    save_obj.save_data()

    now = datetime.now()
    s_car_file = se.query(SCarFileData).filter(
        SCarFileData.car_info_id == car_info.id
    ).first()
    if s_car_file:
        s_car_file.file_name = file_name
        s_car_file.file_path = file_path
        s_car_file.update_time = now
    else:
        s_car_file = SCarFileData(
            car_info_id=car_info.id, file_name=file_name, file_path=file_path,
            update_time=now, create_time=now
        )
        se.add(s_car_file)
    se.commit()
    return JsonResponse.success()

