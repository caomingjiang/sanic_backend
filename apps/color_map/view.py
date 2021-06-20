# from flask import Blueprint, request, Response
# from common.common import JsonResponse, login_required, view_exception
# from apps.car_body.control import ExportCarBodyData
# from db import CarInfo, CarBody
# from common import data_validate
# from datetime import datetime
#
# bp = Blueprint('car_body', __name__, url_prefix='/api/v1/car_body/')
#
#
# @bp.route('update_data', methods=['POST'])
# @login_required
# @view_exception(fail_msg='save_car_body_data failed', db_session=True)
# def save_car_body_data(se):
#     req_data = data_validate.SaveCarBodyData(**request.json)
#     car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
#     if not car_info:
#         return JsonResponse.fail('请先设置当前车型')
#
#     now = datetime.now()
#     insert_list = []
#     for data_type, cb_obj in req_data:
#         insert_list.append(CarBody(
#             data_type=data_type, value=cb_obj.value, score=cb_obj.score,
#             update_time=now, create_time=now, car_info=car_info
#         ))
#     se.query(CarBody).filter(CarBody.car_info == car_info).delete()
#     se.add_all(insert_list)
#     se.commit()
#     return JsonResponse.success()
#
