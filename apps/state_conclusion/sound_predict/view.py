from flask import Blueprint, Response
from common.common import JsonResponse, login_required, view_exception
from db import CarInfo, DataConfigs
from apps.state_conclusion.sound_predict.control import get_base_data, export_excel, cal_total_color_map

bp = Blueprint('sound_predict', __name__, url_prefix='/api/v1/sound_predict/')


@bp.route('get_data', methods=['GET'])
@login_required
@view_exception(fail_msg='get_sound_predict_data failed', db_session=True)
def get_sound_predict_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')
    ret_data = get_base_data(se, car_info)
    return JsonResponse.success(ret_data)


@bp.route('export_data', methods=['GET'])
@login_required
@view_exception(fail_msg='export_acoustic_package_data failed', db_session=True)
def export_acoustic_package_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')
    ret_value = export_excel(se, car_info)

    response = Response(ret_value, content_type='application/octet-stream')
    response.headers['Content-Disposition'] = 'attachment;filename="{0}"'.format('声压预测.xls'.encode().decode("latin1"))
    return response


@bp.route('refresh_data', methods=['GET'])
@login_required
@view_exception(fail_msg='sound_predict refresh_data failed', db_session=True)
def refresh_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')
    backend_suspension = car_info.backend_suspension
    bs_type = DataConfigs.BACKEND_SUSPENSION_CONFS[backend_suspension]
    flag, msg = cal_total_color_map(car_info.id, bs_type)
    if not flag:
        return JsonResponse.fail(msg)
    return JsonResponse.success()
