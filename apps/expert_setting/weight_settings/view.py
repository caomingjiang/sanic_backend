from flask import Blueprint, request
from apps.expert_setting.weight_settings.control import WSaveExcelData, get_current_car_excel_data
from common.common import JsonResponse, login_required, view_exception
from db import WCarExcelData
from common import data_validate
from datetime import datetime

bp = Blueprint('weight_settings', __name__, url_prefix='/api/v1/weight_settings/')


@bp.route('data', methods=['GET'])
@login_required
@view_exception(fail_msg='get_weight_settings_data failed', db_session=True)
def get_weight_settings_data(se):
    req_data = data_validate.GetWeightSettingsData(**request.args.to_dict())
    car_excels = get_current_car_excel_data(se, req_data.bs_type)
    ret_data = {
        'car_excels': car_excels,
    }
    return JsonResponse.success(ret_data)


@bp.route('data', methods=['POST'])
@login_required
@view_exception(fail_msg='save_weight_settings_data failed', db_session=True)
def save_weight_settings_data(se):
    req_data = data_validate.SaveWeightSettingsData(**request.json)

    now = datetime.now()
    excel_name, excel_path = None, None
    if req_data.excel_info:
        excel_name = req_data.excel_info[0].name
        excel_path = req_data.excel_info[0].url
        save_obj = WSaveExcelData(excel_path, req_data.bs_type, se)
        getattr(save_obj, f'save_{req_data.save_type}')()

    active_car_excel = se.query(WCarExcelData).filter(
        WCarExcelData.bs_type == req_data.bs_type, WCarExcelData.data_type == req_data.save_type
    ).first()
    if active_car_excel:
        active_car_excel.excel_name = excel_name
        active_car_excel.excel_path = excel_path
        active_car_excel.update_time = now
    else:
        active_car_excel = WCarExcelData(
            bs_type=req_data.bs_type, data_type=req_data.save_type,
            excel_name=excel_name, excel_path=excel_path, update_time=now, create_time=now
        )
        se.add(active_car_excel)
    se.commit()
    return JsonResponse.success()

