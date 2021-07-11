from flask import Blueprint, request, Response
from common.common import JsonResponse, login_required, view_exception
from apps.single_data.acoustic_package.control import ExportAcousticPackage
from common import data_validate
from db import CarInfo, WAticPkgConfs, DataConfigs, AticPkgConfs
from collections import defaultdict
from datetime import datetime
import copy


bp = Blueprint('acoustic_package', __name__, url_prefix='/api/v1/acoustic_package/')


@bp.route('data', methods=['GET'])
@login_required
@view_exception(fail_msg='get_acoustic_package_data failed', db_session=True)
def get_acoustic_package_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')

    apc_objs = se.query(AticPkgConfs).filter(AticPkgConfs.car_info == car_info)
    apc_dic = {}
    for apc_obj in apc_objs:
        apc_dic[apc_obj.data_type.code] = {
            'conf_item': apc_obj.conf_item,
            'weight': apc_obj.weight,
            'score': apc_obj.score,
            'cost': apc_obj.cost
        }

    backend_suspension = car_info.backend_suspension
    bs_type = DataConfigs.BACKEND_SUSPENSION_CONFS[backend_suspension]
    w_apc_objs = se.query(WAticPkgConfs).filter(WAticPkgConfs.bs_type == bs_type)
    apc_obj_dic = defaultdict(dict)
    for w_apc_obj in w_apc_objs:
        apc_obj_dic[w_apc_obj.data_type.code][w_apc_obj.conf_item] = {
            'weight': w_apc_obj.weight, 'score': w_apc_obj.score, 'cost': w_apc_obj.cost
        }
    ret_data = {}
    for data_type, type_name in WAticPkgConfs.DATA_TYPE_CHOICES:
        single_data_dic = apc_obj_dic.get(data_type)
        conf_items = {}
        active_dic = apc_dic.get(data_type, {})
        if single_data_dic:
            conf_items = {}
            for index, (key, value) in enumerate(single_data_dic.items()):
                conf_items[key] = value
                if index == 0 and not active_dic:
                    active_dic = copy.deepcopy(value)
                    active_dic['conf_item'] = key
        ret_data[data_type] = {
            'active_conf': active_dic.get('conf_item'),
            'conf_items': conf_items,
            'weight': active_dic.get('weight'),
            'score': active_dic.get('score'),
            'cost': active_dic.get('cost'),
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
    insert_list = []
    for data_type, value in req_data.dict().items():
        insert_list.append(AticPkgConfs(
            car_info=car_info, data_type=data_type, conf_item=value['active_conf'],
            weight=value['weight'], score=value['score'], cost=value['cost'],
            update_time=now, create_time=now
        ))
    se.query(AticPkgConfs).filter(AticPkgConfs.car_info == car_info).delete()
    se.add_all(insert_list)
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

