from flask import Blueprint, request
from apps.single_data.freq_data.control import SaveExcelData, get_current_car_excel_data, get_freq_data_car_selects
from apps.state_conclusion.sound_predict.control import cal_total_color_map
from common.common import JsonResponse, login_required, view_exception
from confs.config import CommonThreadPool
from db import CarInfo, CarExcelData, DataConfigs
from common import data_validate
from datetime import datetime

bp = Blueprint('freq_data', __name__, url_prefix='/api/v1/freq_data/')


@bp.route('active_data', methods=['GET'])
@login_required
@view_exception(fail_msg='get_freq_active_data failed', db_session=True)
def get_freq_active_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')
    car_excels = get_current_car_excel_data(se, car_info)
    car_selects = get_freq_data_car_selects(se)
    ret_data = {
        'car_excels': car_excels,
        'car_selects': car_selects
    }
    return JsonResponse.success(ret_data)


@bp.route('save_data', methods=['POST'])
@login_required
@view_exception(fail_msg='save_freq_data failed', db_session=True)
def save_freq_data(se):
    req_data = data_validate.SaveFreqData(**request.json)
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')
    backend_suspension = car_info.backend_suspension
    bs_type = DataConfigs.BACKEND_SUSPENSION_CONFS[backend_suspension]

    now = datetime.now()
    excel_name, excel_path = None, None
    if req_data.excel_info:
        excel_name = req_data.excel_info[0].name
        excel_path = req_data.excel_info[0].url
        save_obj = SaveExcelData(excel_path, car_info.id, bs_type, se)
        getattr(save_obj, f'save_{req_data.save_type}')()

    active_car_excel = se.query(CarExcelData).filter(
        CarExcelData.car_info_id == car_info.id, CarExcelData.data_type == req_data.save_type
    ).first()
    if active_car_excel:
        active_car_excel.excel_name = excel_name
        active_car_excel.excel_path = excel_path
        active_car_excel.update_time = now
    else:
        active_car_excel = CarExcelData(
            car_info_id=car_info.id, data_type=req_data.save_type,
            excel_name=excel_name, excel_path=excel_path, update_time=now, create_time=now
        )
        se.add(active_car_excel)
    se.commit()

    backend_suspension = car_info.backend_suspension
    bs_type = DataConfigs.BACKEND_SUSPENSION_CONFS[backend_suspension]
    CommonThreadPool.submit(cal_total_color_map, car_info.id, bs_type)
    return JsonResponse.success()


@bp.route('select', methods=['GET'])
@login_required
@view_exception(fail_msg='get_select_freq_data failed', db_session=True)
def get_select_freq_data(se):
    req_data = data_validate.GetSelectFreqData(**request.args.to_dict())

    car_excel_data = se.query(CarExcelData).filter(
        CarExcelData.car_info_id == req_data.select_car_id, CarExcelData.data_type == req_data.select_type
    ).first()
    req_data = []
    if car_excel_data:
        excel_name = car_excel_data.excel_name
        excel_path = car_excel_data.excel_path
        if excel_name:
            req_data = [{
                'name': excel_name,
                'url': excel_path
            }]
    return JsonResponse.success(req_data)
