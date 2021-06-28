from flask import Blueprint, request
from common.common import JsonResponse, login_required, view_exception
from db import CarInfo, DesignLibrary
from common import data_validate
from datetime import datetime
from apps.expert_setting.design_library.control import AnalysisDesignLibraryZip
import json

bp = Blueprint('design_library', __name__, url_prefix='/api/v1/design_library/')


@bp.route('save_data', methods=['POST'])
@login_required
@view_exception(fail_msg='save_design_library_data failed', db_session=True)
def save_design_library_data(se):
    req_data = data_validate.SaveDesignLibrary(**request.json)
    car_info = se.query(CarInfo).filter(CarInfo.id == req_data.car_id).first()

    dl_obj = se.query(DesignLibrary).filter(
        DesignLibrary.car_info == car_info, DesignLibrary.data_type == req_data.data_type
    ).first()
    now = datetime.now()
    save_data = json.dumps([im.dict() for im in req_data.images], ensure_ascii=False)
    if dl_obj:
        setattr(dl_obj, req_data.col, save_data)
        dl_obj.update_time = now
    else:
        save_dic = {
            'car_info': car_info, 'data_type': req_data.data_type,
            req_data.col: save_data, 'update_time': now, 'create_time': now
        }
        se.add(DesignLibrary(**save_dic))
    se.commit()
    return JsonResponse.success()


@bp.route('get_data', methods=['GET'])
@login_required
@view_exception(fail_msg='get_design_library_data failed', db_session=True)
def get_design_library_data(se):
    req_data = data_validate.GetDesignLibrary(**request.args.to_dict())
    car_info = se.query(CarInfo).filter(CarInfo.id == req_data.car_id).first()
    dls = se.query(DesignLibrary).filter(DesignLibrary.car_info == car_info)
    dl_dic = {
        dl.data_type.code: dl for dl in dls
    }
    ret_data = {}
    for data_type, type_name in DesignLibrary.DATA_TYPE_CHOICES:
        single_data = dl_dic.get(data_type)
        if single_data:
            poor_design_1 = single_data.poor_design_1 or '[]'
            poor_design_2 = single_data.poor_design_2 or '[]'
            low_cost_scheme = single_data.low_cost_scheme or '[]'
            optimal_scheme_1 = single_data.optimal_scheme_1 or '[]'
            optimal_scheme_2 = single_data.optimal_scheme_2 or '[]'
            ret_data[data_type] = {
                'name': type_name,
                'colomns': {
                    'poor_design_1': json.loads(poor_design_1),
                    'poor_design_2': json.loads(poor_design_2),
                    'low_cost_scheme': json.loads(low_cost_scheme),
                    'optimal_scheme_1': json.loads(optimal_scheme_1),
                    'optimal_scheme_2': json.loads(optimal_scheme_2),
                }
            }
        else:
            ret_data[data_type] = {
                'name': type_name,
                'colomns': {
                    'poor_design_1': [],
                    'poor_design_2': [],
                    'low_cost_scheme': [],
                    'optimal_scheme_1': [],
                    'optimal_scheme_2': [],
                }
            }
    return JsonResponse.success(ret_data)


@bp.route('analysis_zip', methods=['POST'])
@login_required
@view_exception(fail_msg='analysis_design_library_zip failed', db_session=True)
def analysis_design_library_zip(se):
    req_data = data_validate.AnalysisDesignLibraryZip(**request.json)
    car_info = se.query(CarInfo).filter(CarInfo.id == req_data.car_id).first()

    adlz_obj = AnalysisDesignLibraryZip(se, car_info, req_data.url)
    adlz_obj.save_zip()
    return JsonResponse.success()

