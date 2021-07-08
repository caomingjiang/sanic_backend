from flask import Blueprint, request
from apps.expert_setting.atic_pkg_confs.control import AticPkgConfsData, get_current_car_file_data
from common.common import JsonResponse, login_required, view_exception
from db import CarInfo, WSCarFileData
from common import data_validate
from datetime import datetime

bp = Blueprint('atic_pkg_confs', __name__, url_prefix='/api/v1/atic_pkg_confs/')


@bp.route('data', methods=['GET'])
@login_required
@view_exception(fail_msg='get_atic_pkg_confs_data failed', db_session=True)
def get_atic_pkg_confs_data(se):
    req_data = data_validate.GetAticPkgConfsData(**request.args.to_dict())
    ret_data = get_current_car_file_data(se, req_data.bs_type)
    return JsonResponse.success(ret_data)


@bp.route('data', methods=['POST'])
@login_required
@view_exception(fail_msg='save_atic_pkg_confs_data failed', db_session=True)
def save_atic_pkg_confs_data(se):
    req_data = data_validate.SaveAticPkgConfsData(**request.json)

    file_name = req_data.name
    file_path = req_data.url
    save_obj = AticPkgConfsData(file_path, req_data.bs_type, se)
    save_obj.save_data()

    now = datetime.now()
    s_car_file = se.query(WSCarFileData).filter(
        WSCarFileData.bs_type == req_data.bs_type
    ).first()
    if s_car_file:
        s_car_file.file_name = file_name
        s_car_file.file_path = file_path
        s_car_file.update_time = now
    else:
        s_car_file = WSCarFileData(
            bs_type=req_data.bs_type, file_name=file_name, file_path=file_path,
            update_time=now, create_time=now
        )
        se.add(s_car_file)
    se.commit()
    return JsonResponse.success()

