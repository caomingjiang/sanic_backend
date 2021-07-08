from flask import Blueprint, request
from common.common import JsonResponse, login_required, view_exception
from apps.expert_setting.single_data_confs.control import SingleDataConfsMethods, get_current_car_file_data
from db import WCarFileData
from common import data_validate
from datetime import datetime


bp = Blueprint('single_data_confs', __name__, url_prefix='/api/v1/single_data_confs/')


@bp.route('data', methods=['POST'])
@login_required
@view_exception(fail_msg='save_single_data_confs_data failed', db_session=True)
def save_single_data_confs_data(se):
    req_data = data_validate.SaveSingleDataConfsData(**request.json)

    now = datetime.now()
    file_name, file_path = None, None
    if req_data.files:
        file_name = req_data.files[0].name
        file_path = req_data.files[0].url
        save_obj = SingleDataConfsMethods(file_path, req_data.bs_type, se)
        getattr(save_obj, f'save_{req_data.save_type}')()

    active_file = se.query(WCarFileData).filter(
        WCarFileData.bs_type == req_data.bs_type, WCarFileData.data_type == req_data.save_type
    ).first()
    if active_file:
        active_file.file_name = file_name
        active_file.file_path = file_path
        active_file.update_time = now
    else:
        active_file = WCarFileData(
            bs_type=req_data.bs_type, data_type=req_data.save_type,
            file_name=file_name, file_path=file_path, update_time=now, create_time=now
        )
        se.add(active_file)
    se.commit()
    return JsonResponse.success()


@bp.route('data', methods=['GET'])
@login_required
@view_exception(fail_msg='get_single_data_confs_data failed', db_session=True)
def get_single_data_confs_data(se):
    req_data = data_validate.GetSingleDataConfsData(**request.args.to_dict())
    ret_data = get_current_car_file_data(se, req_data.bs_type)
    return JsonResponse.success(ret_data)

