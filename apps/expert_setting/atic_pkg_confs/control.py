import os
from db import WSCarFileData, WAticPkgConfs
from confs.config import UPLOAD_DIR
from datetime import datetime
import json


class AticPkgConfsData(object):
    def __init__(self, file_path, bs_type, se):
        self.full_excel_path = os.path.join(UPLOAD_DIR, file_path)
        self.bs_type = bs_type
        self.se = se

    def common_method(self, table_model):
        now = datetime.now()
        comment_dic = table_model.comment_dic()
        with open(self.full_excel_path, 'rb+') as f:
            source_data = json.loads(f.read())
        insert_list = []
        for type_name, conf_dic in source_data.items():
            data_type = comment_dic.get(type_name)
            for conf_item, value_list in conf_dic.items():
                weight, score, cost = value_list
                save_dic = {
                    "bs_type": self.bs_type, "data_type": data_type, "conf_item": conf_item,
                    "weight": weight, "score": score, "cost": cost,
                    "update_time": now, "create_time": now
                }
                insert_list.append(WAticPkgConfs(**save_dic))
        self.se.query(WAticPkgConfs).filter(WAticPkgConfs.bs_type == self.bs_type).delete()
        self.se.add_all(insert_list)
        self.se.commit()

    def save_data(self):
        self.common_method(WAticPkgConfs)


def get_current_car_file_data(se, bs_type):
    car_files = se.query(WSCarFileData).filter(WSCarFileData.bs_type == bs_type)

    ret_data = {}
    for car_file in car_files:
        file_name, file_path = None, None
        if car_file:
            file_name = car_file.file_name or ''
            file_path = car_file.file_path or ''
        ret_data[car_file.data_type.code] = [{'name': file_name, 'url': file_path}] if file_name else []
    return ret_data

