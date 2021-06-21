from flask import Blueprint, request, Response
from common.common import JsonResponse, login_required, view_exception
from apps.single_data.control import ExportSingleData
from db import CarInfo, ChassisBase, ChassisDetail
from common import data_validate
from datetime import datetime
from ai.noise_algo_func import single_fuchejia_all_func

bp = Blueprint('single_data', __name__, url_prefix='/api/v1/single_data/')


@bp.route('chassis', methods=['GET'])
@login_required
@view_exception(fail_msg='get_chassis_info failed', db_session=True)
def get_chassis_info(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')

    chassis_bases = se.query(ChassisBase).filter(ChassisBase.car_info == car_info)
    chassis_details = se.query(ChassisDetail).filter(ChassisDetail.car_info == car_info)

    chassis_base_info = {
        data_type: {
            'value': 0, 'score': 0
        } if data_type != 'tire_score' else 0 for data_type, type_name in ChassisBase.DATA_TYPE_CHOICES
    }
    chassis_detail_info = {
        data_type: {
            'molecule': 0, 'denominator': 0, 'stiffness_ratio': 0, 'score': 0
        } for data_type, type_name in ChassisDetail.DATA_TYPE_CHOICES
    }
    for chassis_base in chassis_bases:
        if chassis_base.data_type == 'tire_score':
            chassis_base_info['tire_score'] = chassis_base.value
            continue
        chassis_base_info.update({
            chassis_base.data_type: {
                'value': chassis_base.value,
                'score': chassis_base.score
            }
        })
    for chassis_detail in chassis_details:
        chassis_detail_info.update({
            chassis_detail.data_type: {
                'molecule': chassis_detail.molecule,
                'denominator': chassis_detail.denominator,
                'stiffness_ratio': chassis_detail.stiffness_ratio,
                'score': chassis_detail.score,
            }
        })
    ret_data = {
        'chassis_base_info': chassis_base_info,
        'chassis_detail_info': chassis_detail_info
    }
    return JsonResponse.success(ret_data)


@bp.route('chassis', methods=['POST'])
@login_required
@view_exception(fail_msg='update_chassis_info failed', db_session=True)
def update_chassis_info(se):
    req_data = data_validate.ChassisUpdateValidate(**request.json)
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')

    chassis_base_info = req_data.chassis_base_info
    chassis_detail_info = req_data.chassis_detail_info
    now = datetime.now()
    insert_list = []
    for data_type, cb_obj in chassis_base_info:
        insert_list.append(ChassisBase(
            data_type=data_type, value=cb_obj.value, score=cb_obj.score,
            update_time=now, create_time=now, car_info=car_info
        ))
    se.query(ChassisBase).filter(ChassisBase.car_info == car_info).delete()
    se.add_all(insert_list)

    insert_list = []
    for data_type, cd_obj in chassis_detail_info:
        insert_list.append(ChassisDetail(
            data_type=data_type, molecule=cd_obj.molecule, denominator=cd_obj.denominator,
            stiffness_ratio=cd_obj.stiffness_ratio, score=cd_obj.score,
            update_time=now, create_time=now, car_info=car_info
        ))
    se.query(ChassisDetail).filter(ChassisDetail.car_info == car_info).delete()
    se.add_all(insert_list)
    se.commit()
    return JsonResponse.success()


@bp.route('tire_score', methods=['POST'])
@login_required
@view_exception(fail_msg='calculate_tire_score failed')
def calculate_tire_score():
    req_data = data_validate.ChassisBaseValidate(**request.json)
    cal_src_data = {data_type: base_obj.value for data_type, base_obj in req_data if data_type != 'tire_score'}
    ret_num = round(single_fuchejia_all_func(cal_src_data), 2)
    return JsonResponse.success(ret_num)


@bp.route('cal_base_score', methods=['POST'])
@login_required
@view_exception(fail_msg='cal_base_score failed')
def cal_base_score():
    req_data = data_validate.CalculateBaseScore(**request.json)
    return JsonResponse.success(req_data.num)


@bp.route('cal_detail_score', methods=['POST'])
@login_required
@view_exception(fail_msg='cal_detail_score failed')
def cal_detail_score():
    req_data = data_validate.CalculateDetailScore(**request.json)
    if req_data.denominator == 0:
        stiffness_ratio = 0
    else:
        stiffness_ratio = round(req_data.molecule / req_data.denominator, 2)
    ret_data = {
        'stiffness_ratio': stiffness_ratio,
        'score': stiffness_ratio
    }
    return JsonResponse.success(ret_data)


@bp.route('export_data', methods=['GET'])
@login_required
@view_exception(fail_msg='export_single_data failed', db_session=True)
def export_single_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')

    export_data_obj = ExportSingleData(se, car_info)
    ret_value = export_data_obj.export()

    response = Response(ret_value, content_type='application/octet-stream')
    response.headers['Content-Disposition'] = 'attachment;filename="{0}"'.format('单值数据.xls'.encode().decode("latin1"))
    return response
