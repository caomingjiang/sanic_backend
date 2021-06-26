import os
from db import WCarExcelData, WDstiff, WNtfDr, WNtfRr, WSpindleNtfDr, WSpindleNtfRr
from confs.config import UPLOAD_DIR
import pandas as pd
from datetime import datetime
from collections import defaultdict


# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)
# 设置value的显示长度为100，默认为50
pd.set_option('max_colwidth', 100)
# pd.set_option('display.unicode.ambiguous_as_wide', True)
# pd.set_option('display.unicode.east_asian_width', True)


class WSaveExcelData(object):
    def __init__(self, excel_path, car_id, se):
        self.full_excel_path = os.path.join(UPLOAD_DIR, excel_path)
        self.car_id = car_id
        self.se = se

    def common_update(self, df, table_model):
        comment_dic = table_model.comment_dic()
        insert_list = []
        now = datetime.now()
        for index in df.index:
            for type_name, value in df.loc[index].to_dict().items():
                single_add = {
                    'car_info_id': self.car_id, 'frequency_range': index, 'data_type': comment_dic[type_name],
                    'value': round(float(value), 2), 'update_time': now, 'create_time': now
                }
                insert_list.append(table_model(**single_add))
        self.se.query(table_model).filter(table_model.car_info_id == self.car_id).delete()
        self.se.add_all(insert_list)
        self.se.commit()

    def common_method(self, table_model):
        df = pd.read_excel(self.full_excel_path)
        df['name'] = df['name'] + df['dim']
        df.drop('dim', axis=1, inplace=True)
        df.set_index('name', inplace=True)
        df = df.round(2)
        df = df.astype(float)
        df = df.where(df.notnull(), None)
        df = df.T
        self.common_update(df, table_model)

    def save_dstiff(self):
        self.common_method(WDstiff)

    def save_ntf_dr(self):
        self.common_method(WNtfDr)

    def save_ntf_rr(self):
        self.common_method(WNtfRr)

    def save_spindle_ntf_dr(self):
        self.common_method(WSpindleNtfDr)

    def save_spindle_ntf_rr(self):
        self.common_method(WSpindleNtfRr)


def get_current_car_excel_data(se, car_info):
    car_excels = se.query(WCarExcelData).filter(WCarExcelData.car_info == car_info).all()
    car_excels_dic = {data.data_type: data for data in car_excels}

    ret_data = {}
    for data_type, type_name in WCarExcelData.DATA_TYPE_ITEMS:
        car_excel_data = car_excels_dic.get(data_type)
        excel_name, excel_path = None, None
        if car_excel_data:
            excel_name = car_excel_data.excel_name or ''
            excel_path = car_excel_data.excel_path or ''
        ret_data[data_type] = [{'name': excel_name, 'url': excel_path}] if excel_name else []
    return ret_data


def get_freq_data_car_selects(se):
    car_excels = se.query(WCarExcelData).all()
    ret_data = defaultdict(list)
    for car_excel in car_excels:
        ret_data[f'{car_excel.data_type.code}_car_list'].append({
            'id': car_excel.car_info_id,
            'car_name': car_excel.car_info.car_name
        })
    ret_data = dict(ret_data)
    return ret_data
