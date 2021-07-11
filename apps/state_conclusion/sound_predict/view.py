from flask import Blueprint, Response
from common.common import JsonResponse, login_required, view_exception
from db import CarInfo
from apps.state_conclusion.sound_predict.control import get_base_data, export_excel

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
