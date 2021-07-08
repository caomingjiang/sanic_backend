import os
from flask import Blueprint, send_file
from common.common import JsonResponse, login_required, view_exception
from confs.config import UPLOAD_DIR
from db import CarInfo, WAticPkgConfs, DataConfigs, WSCarFileData
from collections import defaultdict


bp = Blueprint('acoustic_package', __name__, url_prefix='/api/v1/acoustic_package/')


@bp.route('data', methods=['GET'])
@login_required
@view_exception(fail_msg='get_acoustic_package_data failed', db_session=True)
def get_acoustic_package_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')
    backend_suspension = car_info.backend_suspension
    bs_type = DataConfigs.BACKEND_SUSPENSION_CONFS[backend_suspension]
    apc_objs = se.query(WAticPkgConfs).filter(WAticPkgConfs.bs_type == bs_type)
    apc_obj_dic = defaultdict(dict)
    for apc_obj in apc_objs:
        apc_obj_dic[apc_obj.data_type][apc_obj.conf_item] = {
            'weight': apc_obj.weight, 'score': apc_obj.score, 'cost': apc_obj.cost
        }
    ret_data = {}
    for data_type, type_name in WAticPkgConfs.DATA_TYPE_CHOICES:
        single_data_dic = apc_obj_dic.get(data_type)
        conf_items = {}
        active_conf = ''
        weight, score, cost = 0, 0, 0
        if single_data_dic:
            conf_items = {}
            for index, (key, value) in enumerate(single_data_dic.items()):
                conf_items[key] = value
                if index == 0:
                    active_conf = key
                    weight = value['weight']
                    score = value['score']
                    cost = value['cost']
        ret_data[data_type] = {
            'active_conf': active_conf,
            'conf_items': conf_items,
            'weight': weight,
            'score': score,
            'cost': cost,
        }
    return JsonResponse.success(ret_data)


@bp.route('export_data', methods=['GET'])
@login_required
@view_exception(fail_msg='export_acoustic_package_data failed', db_session=True)
def export_acoustic_package_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')
    backend_suspension = car_info.backend_suspension
    bs_type = DataConfigs.BACKEND_SUSPENSION_CONFS[backend_suspension]
    w_s_car_file = se.query(WSCarFileData).filter(WSCarFileData.bs_type == bs_type).first()
    file_path = w_s_car_file.file_path
    if file_path:
        full_path = os.path.join(UPLOAD_DIR, file_path)
        return send_file(full_path)
    else:
        return JsonResponse.fail('无声学包数据！')

