import os
import json
import re
from flask import Blueprint, request, Response
from common.common import JsonResponse, login_required, view_exception
from apps.single_data.car_body.control import ExportCarBodyData
from db import CarInfo, CarBody, WCarFileData, DataConfigs
from ai.noise_algo_func import single_cheshen_func
from confs.config import UPLOAD_DIR
from common.loggers import code_log
from common import data_validate
from datetime import datetime

bp = Blueprint('car_body', __name__, url_prefix='/api/v1/car_body/')


@bp.route('update_data', methods=['POST'])
@login_required
@view_exception(fail_msg='save_car_body_data failed', db_session=True)
def save_car_body_data(se):
    req_data = data_validate.SaveCarBodyData(**request.json)
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')

    now = datetime.now()
    insert_list = []
    for data_type, cb_obj in req_data:
        insert_list.append(CarBody(
            data_type=data_type, value=cb_obj.value, score=cb_obj.score,
            update_time=now, create_time=now, car_info=car_info
        ))
    se.query(CarBody).filter(CarBody.car_info == car_info).delete()
    se.add_all(insert_list)
    se.commit()
    return JsonResponse.success()


@bp.route('get_data', methods=['GET'])
@login_required
@view_exception(fail_msg='get_car_body_data failed', db_session=True)
def get_car_body_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')
    ret_data = {
        data_type: {
            'value': None, 'score': 0
        } if data_type.endswith('_vc') else {
            'value': 0, 'score': 0
        } for data_type, type_name in CarBody.DATA_TYPE_CHOICES
    }
    car_body_data = se.query(CarBody).filter(CarBody.car_info == car_info)
    for car_body in car_body_data:
        data_type = car_body.data_type.code
        if data_type.endswith('_vc'):
            ret_data[data_type].update({
                'value': car_body.value, 'score': car_body.score
            })
        else:
            ret_data[data_type].update({
                'value': float(car_body.value), 'score': car_body.score
            })
    return JsonResponse.success(ret_data)


@bp.route('cal_score', methods=['POST'])
@login_required
@view_exception(fail_msg='car_body_cal_score failed', db_session=True)
def car_body_cal_score(se):
    req_data = data_validate.CalculateCarBodyScore(**request.json)
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')
    backend_suspension = car_info.backend_suspension
    bs_type = DataConfigs.BACKEND_SUSPENSION_CONFS[backend_suspension]
    w_car_file = se.query(WCarFileData).filter(
        WCarFileData.bs_type == bs_type, WCarFileData.data_type == 'car_body'
    ).first()
    if not w_car_file:
        return JsonResponse.fail("缺少专家设定数据")
    car_file_url = w_car_file.file_path or ''
    car_file_path = os.path.join(UPLOAD_DIR, car_file_url)
    if not os.path.exists(car_file_path):
        return JsonResponse.fail("缺少专家设定数据")
    with open(car_file_path, 'rb+') as f:
        cheshen = json.loads(f.read())
    comment_dic = dict(CarBody.DATA_TYPE_CHOICES)
    type_name = comment_dic[req_data.cal_type].replace(' -- ', '_')
    req_value = float(req_data.value) if re.findall('\d', req_data.value) else req_data.value
    score = single_cheshen_func(type_name, req_value, cheshen)
    if score == 'error':
        code_log.error(f'分值算法出错，single_cheshen_func("{type_name}", {req_data.value}, '
                       f'{json.dumps(cheshen, ensure_ascii=False)})')
        return JsonResponse.fail('分值算法出错，请联系管理员')
    return JsonResponse.success(score)


@bp.route('export_data', methods=['GET'])
@login_required
@view_exception(fail_msg='export_car_body_data failed', db_session=True)
def export_car_body_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')

    export_data_obj = ExportCarBodyData(se, car_info)
    ret_value = export_data_obj.export()

    response = Response(ret_value, content_type='application/octet-stream')
    response.headers['Content-Disposition'] = 'attachment;filename="{0}"'.format('车身数据.xls'.encode().decode("latin1"))
    return response
