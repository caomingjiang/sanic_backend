from flask import Blueprint, Response
from common.common import JsonResponse, login_required, view_exception
from apps.state_conclusion.color_map.control import ColorMapData
from db import CarInfo

bp = Blueprint('color_map', __name__, url_prefix='/api/v1/color_map/')


@bp.route('get_data', methods=['GET'])
@login_required
@view_exception(fail_msg='get_color_map_data failed', db_session=True)
def get_color_map_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')
    color_map = ColorMapData(se, car_info)
    ret_data = color_map.get_data()
    return JsonResponse.success(ret_data)


@bp.route('export_data', methods=['GET'])
@login_required
@view_exception(fail_msg='export_acoustic_package_data failed', db_session=True)
def export_acoustic_package_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')
    color_map = ColorMapData(se, car_info)
    ret_value = color_map.export_excel()

    response = Response(ret_value, content_type='application/octet-stream')
    response.headers['Content-Disposition'] = 'attachment;filename="{0}"'.format('color_map.xls'.encode().decode("latin1"))
    return response

