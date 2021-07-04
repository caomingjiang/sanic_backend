from flask import Blueprint
from common.common import JsonResponse, login_required, view_exception
from apps.state_conclusion.risk_tik.control import get_risk_tik_list
from db import CarInfo, ColorMapNtfDr, ColorMapNtfRr, ColorMapDstiff, ColorMapSpindleNtfDr, ColorMapSpindleNtfRr
import math

bp = Blueprint('risk_tik', __name__, url_prefix='/api/v1/risk_tik/')


@bp.route('get_data', methods=['GET'])
@login_required
@view_exception(fail_msg='get_risk_tik_data failed', db_session=True)
def get_risk_tik_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')

    ret_list = []
    ret_list.extend(get_risk_tik_list(se, ColorMapDstiff, car_info))
    ret_list.extend(get_risk_tik_list(se, ColorMapNtfDr, car_info))
    ret_list.extend(get_risk_tik_list(se, ColorMapNtfRr, car_info))
    ret_list.extend(get_risk_tik_list(se, ColorMapSpindleNtfDr, car_info))
    ret_list.extend(get_risk_tik_list(se, ColorMapSpindleNtfRr, car_info))

    single_num = math.ceil(len(ret_list) / 3)
    ret_list = [ret_list[i: i + single_num] for i in range(0, len(ret_list), single_num)]

    return JsonResponse.success(ret_list)

