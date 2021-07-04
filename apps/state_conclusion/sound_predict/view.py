from flask import Blueprint
from common.common import JsonResponse, login_required, view_exception
from db import CarInfo, ColorMapActualTestData, TotalColorMapData

bp = Blueprint('sound_predict', __name__, url_prefix='/api/v1/sound_predict/')


@bp.route('get_data', methods=['GET'])
@login_required
@view_exception(fail_msg='get_sound_predict_data failed', db_session=True)
def get_sound_predict_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')
    cma_datas = se.query(ColorMapActualTestData).filter(ColorMapActualTestData.car_info == car_info)
    tcm_datas = se.query(TotalColorMapData).filter(TotalColorMapData.car_info == car_info)
    xaxis_list = []
    cma_dr_list, cma_rr_list = [], []
    for cma_data in cma_datas:
        xaxis_list.append(cma_data.frequency_range)
        cma_dr_list.append(cma_data.dr_value)
        cma_rr_list.append(cma_data.rr_value)
    tcm_dr_list, tcm_rr_list = [], []
    for tcm_data in tcm_datas:
        tcm_dr_list.append(tcm_data.dr_value)
        tcm_rr_list.append(tcm_data.rr_value)
    ret_data = {
        'xaxis_list': xaxis_list,
        'cma_dr_list': cma_dr_list,
        'cma_rr_list': cma_rr_list,
        'tcm_dr_list': tcm_dr_list,
        'tcm_rr_list': tcm_rr_list
    }
    return JsonResponse.success(ret_data)

