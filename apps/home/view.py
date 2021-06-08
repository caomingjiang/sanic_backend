from flask import request, Blueprint
from common.common import JsonResponse, login_required, view_exception
from common import data_validate
from db import CarInfo, DevStage, CarTestInfo
from datetime import datetime

bp = Blueprint('home', __name__, url_prefix='/api/v1/home/')


@bp.route('car_info', methods=['POST'])
@login_required
@view_exception(fail_msg='add_car_info failed', db_session=True)
def add_car_info(se):
    req_data = data_validate.AddCarInfo(**request.json)
    car_info = se.query(CarInfo).filter(CarInfo.car_name == req_data.car_name).first()
    if car_info:
        return JsonResponse.fail("新增失败：车型名称已存在")
    now = datetime.now()
    new_car = CarInfo(
        car_name=req_data.car_name, dev_stage_id=req_data.dev_stage_id, car_body=req_data.car_body,
        front_suspension=req_data.front_suspension, front_subframe=req_data.front_subframe,
        backend_suspension=req_data.backend_suspension, backend_subframe=req_data.backend_subframe,
        update_time=now, create_time=now
    )
    se.add(new_car)
    se.commit()
    se.flush()
    test_time = req_data.test_time
    new_car_test_info = CarTestInfo(
        car_info=new_car, dev_stage_id=req_data.dev_stage_id, data_source=req_data.data_source,
        test_time=datetime.strptime(test_time, '%Y-%m-%d %H:%M:%S') if test_time else None,
        test_user=req_data.test_user, update_time=now, create_time=now
    )
    se.add(new_car_test_info)
    se.commit()
    return JsonResponse.success()


@bp.route('car_info', methods=['GET'])
@login_required
@view_exception(fail_msg='get_dev_car_info failed', db_session=True)
def get_dev_car_info(se):
    car_info = se.query(CarInfo).filter(CarInfo.is_dev == 1).first()
    if not car_info:
        return JsonResponse.fail('未设置当前车型')
    car_test_info = se.query(CarTestInfo).filter(
        CarTestInfo.dev_stage == car_info.dev_stage, CarTestInfo.car_info == car_info
    ).first()

    ret_data = {
        'id': car_info.id,
        'car_name': car_info.car_name,
        'dev_stage_id': car_info.dev_stage_id,
        'data_source': car_test_info.data_source or '',
        'test_time': car_test_info.test_time.strftime('%Y-%m-%d %H:%M:%S') if car_test_info.test_time else '',
        'test_user': car_test_info.test_user or '',
        'car_body': car_info.car_body,
        'front_suspension': car_info.front_suspension,
        'front_subframe': car_info.front_subframe,
        'backend_suspension': car_info.backend_suspension,
        'backend_subframe': car_info.backend_subframe,
    }
    return JsonResponse.success(ret_data)


@bp.route('car_info/<car_id>', methods=['PUT'])
@login_required
@view_exception(fail_msg='put_dev_car_info failed', db_session=True)
def put_dev_car_info(car_id, se):
    req_data = data_validate.AddCarInfo(**request.json)

    exist = se.query(CarInfo).filter(CarInfo.car_name == req_data.car_name, CarInfo.id != car_id).first()
    if exist:
        return JsonResponse.fail("车型名称重复，请修改！")

    now = datetime.now()
    update_data = {
        'data_source': req_data.data_source,
        'test_time': datetime.strptime(req_data.test_time, '%Y-%m-%d %H:%M:%S') if req_data.test_time else None,
        'test_user': req_data.test_user,
        'update_time': now
    }
    car_test_info = se.query(CarTestInfo).filter(
        CarTestInfo.car_info_id == car_id, CarTestInfo.dev_stage_id == req_data.dev_stage_id
    )
    if car_test_info.first():
        car_test_info.update(update_data)
    else:
        update_data.update({
            'car_info_id': car_id, 'dev_stage_id': req_data.dev_stage_id, 'create_time': now
        })
        se.add(CarTestInfo(**update_data))

    se.query(CarInfo).filter(CarInfo.id == car_id).update(
        {
            'car_name': req_data.car_name, 'dev_stage_id': req_data.dev_stage_id, 'car_body': req_data.car_body,
            'front_suspension': req_data.front_suspension, 'front_subframe': req_data.front_subframe,
            'backend_suspension': req_data.backend_suspension, 'backend_subframe': req_data.backend_subframe,
            'update_time': now
         }
    )
    se.commit()
    return JsonResponse.success()


@bp.route('update_dev_car/<car_id>', methods=['PUT'])
@login_required
@view_exception(fail_msg='update_dev_car failed', db_session=True)
def update_dev_car(car_id, se):
    se.query(CarInfo).update({'is_dev': 0})
    se.commit()
    se.query(CarInfo).filter(CarInfo.id == car_id).update({'is_dev': 1})
    se.commit()
    return JsonResponse.success()


@bp.route('get_car_test_info/<car_id>', methods=['GET'])
@login_required
@view_exception(fail_msg='get_car_test_info failed', db_session=True)
def get_car_test_info(car_id, se):
    req_data = data_validate.GetCarTestInfo(**request.args.to_dict())
    car_test_info = se.query(CarTestInfo).filter(
        CarTestInfo.car_info_id == car_id, CarTestInfo.dev_stage_id == req_data.dev_stage_id
    ).first()
    data_source, test_time, test_user = '', '', ''
    if car_test_info:
        data_source = car_test_info.data_source
        test_time = car_test_info.test_time
        test_time = test_time.strftime('%Y-%m-%d %H:%M:%S') if test_time else ''
        test_user = car_test_info.test_user

    ret_data = {
        'data_source': data_source,
        'test_time': test_time,
        'test_user': test_user
    }
    return JsonResponse.success(ret_data)


@bp.route('selects', methods=['GET'])
@login_required
@view_exception(fail_msg='get_home_selects failed', db_session=True)
def get_home_selects(se):
    car_infos = se.query(CarInfo).all()
    cars = []
    for car_info in car_infos:
        cars.append({
            'car_name': car_info.car_name,
            'id': car_info.id
        })
    dev_stages = se.query(DevStage).all()
    dev_stage_list = []
    for dev_stage in dev_stages:
        dev_stage_list.append({
            'id': dev_stage.id,
            'name': dev_stage.name
        })
    ret_data = {
        'cars': cars,
        'dev_stages': dev_stage_list
    }
    return JsonResponse.success(ret_data)

