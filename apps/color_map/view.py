from flask import Blueprint, request, Response
from common.common import JsonResponse, login_required, view_exception
from db import CarInfo
from common import data_validate
from datetime import datetime

bp = Blueprint('color_map', __name__, url_prefix='/api/v1/color_map/')


@bp.route('get_data', methods=['POST'])
@login_required
@view_exception(fail_msg='get_color_map_data failed', db_session=True)
def get_color_map_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')

    return JsonResponse.success()

