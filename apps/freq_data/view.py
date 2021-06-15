from flask import Blueprint, request
from apps.freq_data.control import SaveExcelData
from common.common import JsonResponse, login_required, view_exception
from confs.config import CommonThreadPool
from db import CarInfo, CarExcelData
from common import data_validate
from datetime import datetime

bp = Blueprint('freq_data', __name__, url_prefix='/api/v1/freq_data/')


@bp.route('active_data', methods=['GET'])
@login_required
@view_exception(fail_msg='get_active_data failed', db_session=True)
def get_active_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')

    # data_type_dic = {
    #     'modal_map': ModalMap, 'dstiff': Dstiff, 'ntf_dr': NtfDr, 'ntf_rr': NtfRr,
    #     'spindle_ntf_dr': SpindleNtfDr, 'spindle_ntf_rr': SpindleNtfRr,
    #     'actual_test_data': ActualTestData
    # }

    data_type_list = [
        'modal_map', 'dstiff', 'ntf_dr', 'ntf_rr', 'spindle_ntf_dr', 'spindle_ntf_rr',
        'actual_test_data'
    ]

    car_excels = se.query(CarExcelData).filter(CarExcelData.car_info == car_info).all()
    car_excels_dic = {data.data_type: data for data in car_excels}

    ret_data = {}
    for data_type in data_type_list:
        current_data = car_excels_dic.get(data_type)

        active_car_id = car_info.id
        excel_name = None
        excel_path = None
        if current_data:
            active_data = se.query(CarExcelData).filter(CarExcelData.id == current_data.active_id).first()
            active_car_id = active_data.car_info.id
            excel_name = active_data.excel_name
            excel_path = active_data.excel_path
            ret_data[data_type] = {
                'active_car_id': active_data.car_info.id,
                'excel_info': [{
                    'name': active_data.excel_name or '',
                    'url': active_data.excel_path or ''
                }]
            }
        excel_info = [{'name': excel_name, 'url': excel_path}] if excel_name else []

        ret_data[data_type] = {
            'active_car_id': active_car_id,
            'excel_info': excel_info
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

    now = datetime.now()
    excel_name, excel_path = None, None
    if req_data.excel_info:
        excel_name = req_data.excel_info[0].name
        excel_path = req_data.excel_info[0].url
        save_obj = SaveExcelData(excel_path, req_data.active_car_id, se)
        CommonThreadPool.submit(getattr(save_obj, f'save_{req_data.save_type}'))

    active_car_excel = se.query(CarExcelData).filter(
        CarExcelData.car_info_id == req_data.active_car_id, CarExcelData.data_type == req_data.save_type
    ).first()
    if active_car_excel:
        active_car_excel.excel_name = excel_name
        active_car_excel.excel_path = excel_path
        active_car_excel.update_time = now
        se.commit()
    else:
        active_car_excel = CarExcelData(
            car_info_id=req_data.active_car_id, data_type=req_data.save_type,
            excel_name=excel_name, excel_path=excel_path, update_time=now, create_time=now
        )
        se.add(active_car_excel)
        se.commit()
        se.flush()
        active_car_excel.active_id = active_car_excel.id
        se.commit()

    car_excel = se.query(CarExcelData).filter(
        CarExcelData.car_info == car_info, CarExcelData.data_type == req_data.save_type
    ).first()
    if car_excel:
        car_excel.active_id = active_car_excel.id
        car_excel.update_time = now
    else:
        car_excel = CarExcelData(
            car_info=car_info, data_type=req_data.save_type, active_id=active_car_excel.id,
            update_time=now, create_time=now
        )
        se.add(car_excel)
    se.commit()
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
