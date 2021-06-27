from flask import Blueprint, request, Response
from common.common import JsonResponse, login_required, view_exception
from apps.acoustic_package.control import ExportAcousticPackage
from db import CarInfo, AticPkgConfs
from common import data_validate
from collections import defaultdict
from datetime import datetime


bp = Blueprint('acoustic_package', __name__, url_prefix='/api/v1/acoustic_package/')


@bp.route('data', methods=['GET'])
@login_required
@view_exception(fail_msg='get_acoustic_package_data failed', db_session=True)
def get_acoustic_package_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')
    apc_objs = se.query(AticPkgConfs).filter(AticPkgConfs.car_info == car_info)
    apc_obj_dic = defaultdict(dict)
    for apc_obj in apc_objs:
        apc_obj_dic[apc_obj.data_type][apc_obj.conf_item] = {
            'weight': apc_obj.weight, 'score': apc_obj.score, 'cost': apc_obj.cost,
            'is_active': apc_obj.is_active
        }
    ret_data = {}
    for data_type, type_name in AticPkgConfs.DATA_TYPE_ITEMS:
        single_data_dic = apc_obj_dic.get(data_type)
        conf_items = {}
        active_conf = ''
        weight, score, cost = 0, 0, 0
        if single_data_dic:
            conf_items = {}
            for key, value in single_data_dic.items():
                is_active = value.pop('is_active')
                conf_items[key] = value
                if is_active:
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


@bp.route('data', methods=['POST'])
@login_required
@view_exception(fail_msg='save_acoustic_package_data failed', db_session=True)
def save_acoustic_package_data(se):
    req_data = data_validate.SaveAcousticPackageData(**request.json)
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')
    apc_objs = se.query(AticPkgConfs).filter(AticPkgConfs.car_info == car_info)
    if not apc_objs:
        return JsonResponse.fail('未设置当前声学包的配置')

    now = datetime.now()
    apc_obj_dic = defaultdict(dict)
    for apc_obj in apc_objs:
        apc_obj_dic[apc_obj.data_type][apc_obj.conf_item] = apc_obj
    se.query(AticPkgConfs).filter(AticPkgConfs.car_info == car_info).update({
        'is_active': False, 'update_time': now
    })
    se.commit()
    for data_type, value in req_data.dict().items():
        active_conf = value['active_conf']
        apc_obj = apc_obj_dic[data_type][active_conf]
        apc_obj.is_active = True
        apc_obj.update_time = now
    se.commit()
    return JsonResponse.success()


@bp.route('export_data', methods=['GET'])
@login_required
@view_exception(fail_msg='export_acoustic_package_data failed', db_session=True)
def export_acoustic_package_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')

    export_data_obj = ExportAcousticPackage(se, car_info)
    ret_value = export_data_obj.export()

    response = Response(ret_value, content_type='application/octet-stream')
    response.headers['Content-Disposition'] = 'attachment;filename="{0}"'.format('声学包.xls'.encode().decode("latin1"))
    return response

