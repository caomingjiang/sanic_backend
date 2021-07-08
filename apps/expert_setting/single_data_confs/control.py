import os
from confs.config import UPLOAD_DIR
from datetime import datetime
from db import WChassisBase, WChassisDetail, WCarBody, WCarFileData
import json


class SingleDataConfsMethods(object):
    def __init__(self, excel_path, bs_type, se):
        self.full_file_path = os.path.join(UPLOAD_DIR, excel_path)
        self.bs_type = bs_type
        self.se = se

    def common_save(self, table_model):
        now = datetime.now()
        with open(self.full_file_path, 'rb+') as f:
            data = json.loads(f.read())
        comment_dic = table_model.comment_dic()
        insert_list = []
        for type_name, value_list in data.items():
            data_type = comment_dic[type_name.replace('_', ' -- ')]
            save_dic = {
                'bs_type': self.bs_type, 'data_type': data_type,
                'value': json.dumps(value_list, ensure_ascii=False),
                'update_time': now, 'create_time': now
            }
            insert_list.append(table_model(**save_dic))
        self.se.query(table_model).filter(table_model.bs_type == self.bs_type).delete()
        self.se.add_all(insert_list)
        self.se.commit()

    def save_subframe(self):
        self.common_save(WChassisBase)

    def save_lower_arm(self):
        self.common_save(WChassisDetail)

    def save_car_body(self):
        self.common_save(WCarBody)


def get_current_car_file_data(se, bs_type):
    car_files = se.query(WCarFileData).filter(WCarFileData.bs_type == bs_type).all()
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

