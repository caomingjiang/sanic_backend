from flask import Blueprint
from common.common import JsonResponse, login_required, view_exception
from db import CarInfo, ColorMapActualTestData, TotalColorMapData, DataConfigs, SubsystemScoring
from apps.state_conclusion.sound_predict.control import cal_total_color_map
from confs.config import CommonThreadPool

bp = Blueprint('sound_predict', __name__, url_prefix='/api/v1/sound_predict/')


@bp.route('get_data', methods=['GET'])
@login_required
@view_exception(fail_msg='get_sound_predict_data failed', db_session=True)
def get_sound_predict_data(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('请先设置当前车型')
    cma_datas = se.query(ColorMapActualTestData).filter(
        ColorMapActualTestData.car_info == car_info
    ).order_by(ColorMapActualTestData.id.asc())
    tcm_datas = se.query(TotalColorMapData).filter(
        TotalColorMapData.car_info == car_info
    ).order_by(TotalColorMapData.id.asc()).all()

    if not tcm_datas:
        backend_suspension = car_info.backend_suspension
        bs_type = DataConfigs.BACKEND_SUSPENSION_CONFS[backend_suspension]
        CommonThreadPool.submit(cal_total_color_map, car_info.id, bs_type)

    xaxis_list = []
    cma_dr_list, cma_rr_list = [], []
    for cma_data in cma_datas:
        xaxis_list.append(cma_data.frequency_range)
        cma_dr_list.append(cma_data.dr_value)
        cma_rr_list.append(cma_data.rr_value)
    tcm_dr_list, tcm_rr_list = [], []
    new_xaxis_list = []
    for tcm_data in tcm_datas:
        new_xaxis_list.append(tcm_data.frequency_range)
        tcm_dr_list.append(tcm_data.dr_value)
        tcm_rr_list.append(tcm_data.rr_value)

    sub_score_objs = se.query(SubsystemScoring).filter(SubsystemScoring.car_info_id == car_info.id)
    sub_score_data = []
    sub_comment_dic = dict(SubsystemScoring.DATA_TYPE_CHOICES)
    for sub_score_obj in sub_score_objs:
        sub_score_data.append({
            'data_type': sub_comment_dic[sub_score_obj.data_type.code],
            'value': sub_score_obj.value
        })
    ret_data = {
        'xaxis_list': xaxis_list or new_xaxis_list,
        'cma_dr_list': cma_dr_list,
        'cma_rr_list': cma_rr_list,
        'tcm_dr_list': tcm_dr_list,
        'tcm_rr_list': tcm_rr_list,
        'sub_score_data': sub_score_data
    }
    return JsonResponse.success(ret_data)

