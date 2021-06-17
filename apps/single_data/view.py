from flask import Blueprint, request
from common.common import JsonResponse, login_required, view_exception
from db import CarInfo, ChassisBase, ChassisDetail
from common import data_validate
from datetime import datetime

bp = Blueprint('single_data', __name__, url_prefix='/api/v1/single_data/')


@bp.route('chassis', methods=['GET'])
@login_required
@view_exception(fail_msg='get_chassis_info failed', db_session=True)
def get_chassis_info(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')

    chassis_base = se.query(ChassisBase).filter(ChassisBase.car_info == car_info).first()
    chassis_detail = se.query(ChassisDetail).filter(ChassisDetail.car_info == car_info).first()

    chassis_base_info = {}
    chassis_detail_info = {}
    if chassis_base:
        chassis_base_info = chassis_base.to_dict()
    if chassis_detail:
        chassis_detail_info = chassis_detail.to_dict()

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

    chassis_base_info = req_data.chassis_base_info.dict()
    chassis_detail_info = req_data.chassis_detail_info.dict()
    now = datetime.now()
    chassis_base_info['update_time'] = now
    chassis_detail_info['update_time'] = now
    chassis_base = se.query(ChassisBase).filter(ChassisBase.car_info == car_info)
    chassis_detail = se.query(ChassisDetail).filter(ChassisDetail.car_info == car_info)
    if chassis_base.first():
        chassis_base.update(chassis_base_info)
    else:
        chassis_base_info['create_time'] = now
        chassis_base_info['car_info'] = car_info
        se.add(ChassisBase(**chassis_base_info))

    if chassis_detail.first():
        chassis_detail.update(chassis_detail_info)
    else:
        chassis_detail_info['create_time'] = now
        chassis_detail_info['car_info'] = car_info
        se.add(ChassisDetail(**chassis_detail_info))
    se.commit()
    return JsonResponse.success()


@bp.route('tire_score', methods=['POST'])
@login_required
@view_exception(fail_msg='calculate_tire_score failed')
def calculate_tire_score():
    req_data = data_validate.ChassisBaseValidate(**request.json)
    return JsonResponse.success()
