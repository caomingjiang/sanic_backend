from db import Session, Role, User, DevStage
from common.common import get_md5
from datetime import datetime


def init_user():
    se = Session()
    try:
        now = datetime.now()
        role_data = {
            1: '普通管理员',
            2: '超级管理员'
        }
        for code, name in role_data.items():
            role = se.query(Role).filter(Role.code == code).first()
            if not role:
                new_role = Role(
                    name=name, code=code, update_time=now, create_time=now
                )
                se.add(new_role)
        se.commit()

        user_data = [
            {
                'account': 'luzao123',
                'username': '管理员',
                'password': 'test123',
                'role_code': 1
            }
        ]
        for user_dic in user_data:
            user = se.query(User).filter(User.account == user_dic['account']).first()
            role = se.query(Role).filter(Role.code == user_dic['role_code']).first()
            if not user:
                new_user = User(
                    account=user_dic['account'], username=user_dic['username'],
                    password=get_md5(user_dic['password']), role=role,
                    update_time=now, create_time=now
                )
                se.add(new_user)
        se.commit()
    finally:
        se.close()


def init_dev_stage():
    se = Session()
    try:
        dev_stages = [
            'Mule', 'Simu', 'EP1', 'EP2', 'P', 'PP', 'SOP'
        ]
        now = datetime.now()
        for dev_stage in dev_stages:
            dev_stage_obj = se.query(DevStage).filter(DevStage.name == dev_stage).first()
            if not dev_stage_obj:
                se.add(
                    DevStage(
                        name=dev_stage, update_time=now, create_time=now
                    )
                )
        se.commit()
    finally:
        se.close()


def init_main():
    init_user()
    init_dev_stage()


if __name__ == '__main__':
    init_user()
    init_dev_stage()

