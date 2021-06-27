import os
from confs.config import UPLOAD_DIR
from datetime import datetime
from db import WChassisBase, WChassisDetail, WCarBody, WCarFileData
import json
import copy


class SingleDataConfsMethods(object):
    def __init__(self, excel_path, car_id, se):
        self.full_file_path = os.path.join(UPLOAD_DIR, excel_path)
        self.car_id = car_id
        self.se = se

    def save_subframe(self):
        now = datetime.now()
        with open(self.full_file_path, 'rb+') as f:
            data = json.loads(f.read())
        comment_dic = WChassisBase.comment_dic()
        insert_list = []
        for type_name, value_list in data.items():
            data_type = comment_dic[type_name.replace('_', ' -- ')]
            save_dic = {
                'car_info_id': self.car_id, 'data_type': data_type, 'value': value_list[0][0],
                'score': value_list[1][0], 'update_time': now, 'create_time': now
            }
            insert_list.append(WChassisBase(**save_dic))
        self.se.query(WChassisBase).filter(WChassisBase.car_info_id == self.car_id).delete()
        self.se.add_all(insert_list)
        self.se.commit()

    def save_lower_arm(self):
        now = datetime.now()
        with open(self.full_file_path, 'rb+') as f:
            data = json.loads(f.read())
        comment_dic = WChassisDetail.comment_dic()
        insert_list = []
        for type_name, value_list in data.items():
            data_type = comment_dic[type_name.replace('_', ' -- ')]
            save_dic = {
                'car_info_id': self.car_id, 'data_type': data_type, 'stiffness_ratio': value_list[0][0],
                'score': value_list[1][0], 'update_time': now, 'create_time': now
            }
            insert_list.append(WChassisDetail(**save_dic))
        self.se.query(WChassisDetail).filter(WChassisDetail.car_info_id == self.car_id).delete()
        self.se.add_all(insert_list)
        self.se.commit()

    def save_car_body(self):
        now = datetime.now()
        with open(self.full_file_path, 'rb+') as f:
            data = json.loads(f.read())
        comment_dic = WCarBody.comment_dic()
        insert_list = []
        for type_name, value_list in data.items():
            data_type = comment_dic[type_name.replace('_', ' -- ')]
            save_dic = {
                'car_info_id': self.car_id, 'data_type': data_type,
                'update_time': now, 'create_time': now
            }
            if isinstance(value_list, list):
                save_dic.update({
                    'value': value_list[0][0], 'score': value_list[1][0],
                })
                insert_list.append(WCarBody(**save_dic))
            elif isinstance(value_list, dict):
                for value, score in value_list.items():
                    tmp_save_dic = copy.deepcopy(save_dic)
                    tmp_save_dic.update({
                        'value': value, 'score': score,
                    })
                    insert_list.append(WCarBody(**tmp_save_dic))
        self.se.query(WCarBody).filter(WCarBody.car_info_id == self.car_id).delete()
        self.se.add_all(insert_list)
        self.se.commit()


def get_current_car_file_data(se, car_info):
    car_files = se.query(WCarFileData).filter(WCarFileData.car_info == car_info).all()
    car_files_dic = {data.data_type: data for data in car_files}

    ret_data = {}
    for data_type, type_name in WCarFileData.DATA_TYPE_CHOICES:
        car_file_data = car_files_dic.get(data_type)
        file_name, file_path = None, None
        if car_file_data:
            file_name = car_file_data.file_name or ''
            file_path = car_file_data.file_path or ''
        ret_data[data_type] = [{'name': file_name, 'url': file_path}] if file_name else []
    return ret_data

