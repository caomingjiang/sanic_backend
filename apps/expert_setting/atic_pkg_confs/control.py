import os
from db import SCarFileData, AticPkgConfs
from confs.config import UPLOAD_DIR
import pandas as pd
from datetime import datetime
from collections import defaultdict
import json


class AticPkgConfsData(object):
    def __init__(self, file_path, car_id, se):
        self.full_excel_path = os.path.join(UPLOAD_DIR, file_path)
        self.car_id = car_id
        self.se = se

    def common_method(self, table_model):
        now = datetime.now()
        apc_objs = self.se.query(AticPkgConfs).filter(
            AticPkgConfs.car_info_id == self.car_id, AticPkgConfs.is_active == 1
        )
        apc_obj_dic = {
            apc_obj.data_type: apc_obj.conf_item for apc_obj in apc_objs
        }
        comment_dic = table_model.comment_dic()
        with open(self.full_excel_path, 'rb+') as f:
            source_data = json.loads(f.read())
        insert_list = []
        for type_name, conf_dic in source_data.items():
            data_type = comment_dic.get(type_name)
            active_conf_item = apc_obj_dic.get(data_type)
            active_conf_item = active_conf_item or list(conf_dic.keys())[0]
            for conf_item, value_list in conf_dic.items():
                weight, score, cost = value_list
                is_active = True if conf_item == active_conf_item else False
                save_dic = {
                    "car_info_id": self.car_id, "data_type": data_type, "conf_item": conf_item,
                    "weight": weight, "score": score, "cost": cost, "is_active": is_active,
                    "update_time": now, "create_time": now
                }
                insert_list.append(AticPkgConfs(**save_dic))
        self.se.query(AticPkgConfs).filter(AticPkgConfs.car_info_id == self.car_id).delete()
        self.se.add_all(insert_list)
        self.se.commit()

    def save_data(self):
        self.common_method(AticPkgConfs)


def get_current_car_file_data(se, car_info):
    car_file = se.query(SCarFileData).filter(SCarFileData.car_info == car_info).first()

    file_name, file_path = None, None
    if car_file:
        file_name = car_file.file_name or ''
        file_path = car_file.file_path or ''
    ret_data = [{'name': file_name, 'url': file_path}] if file_name else []
    return ret_data

