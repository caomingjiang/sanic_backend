from flask import Blueprint
from common.common import JsonResponse, login_required, view_exception
from apps.state_conclusion.risk_tik.control import get_risk_tik_dict, get_modal_map_risk_dic, \
    get_dr_risk, get_rr_risk
from db import CarInfo, ColorMapNtfDr, ColorMapNtfRr, ColorMapDstiff, ColorMapSpindleNtfDr, \
    ColorMapSpindleNtfRr
import math

bp = Blueprint('risk_tik', __name__, url_prefix='/api/v1/risk_tik/')


@bp.route('get_data', methods=['GET'])
@login_required
@view_exception(fail_msg='get_risk_tik_data failed', db_session=True)
def get_risk_tik_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')

    modal_map_dic = get_modal_map_risk_dic(se, car_info)
    dstiff_dic = get_risk_tik_dict(se, ColorMapDstiff, car_info, 'Dstiff')
    ntf_dr_dic = get_risk_tik_dict(se, ColorMapNtfDr, car_info, 'NTF DR')
    ntf_rr_dic = get_risk_tik_dict(se, ColorMapNtfRr, car_info, 'NTF RR')
    spindle_ntf_dr_dic = get_risk_tik_dict(se, ColorMapSpindleNtfDr, car_info, 'Spindle NTF DR')
    spindle_ntf_rr_dic = get_risk_tik_dict(se, ColorMapSpindleNtfRr, car_info, 'Spindle NTF RR')

    dr_risk = get_dr_risk(modal_map_dic, dstiff_dic, ntf_dr_dic, spindle_ntf_dr_dic)
    rr_risk = get_rr_risk(modal_map_dic, dstiff_dic, ntf_rr_dic, spindle_ntf_rr_dic)
    ret_data = {
        'dr_risk': dr_risk,
        'rr_risk': rr_risk,
    }
    return JsonResponse.success(ret_data)
