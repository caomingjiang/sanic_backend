import os
from db import ModalMap, Dstiff, NtfDr, NtfRr, SpindleNtfDr, SpindleNtfRr, ActualTestData, CarExcelData, \
    ColorMapDstiff, ColorMapNtfDr, ColorMapNtfRr, ColorMapSpindleNtfDr, ColorMapSpindleNtfRr
from confs.config import UPLOAD_DIR
import pandas as pd
from datetime import datetime
from common.common import get_orm_comment_dic
import json
from collections import defaultdict
from ai.noise_algo_func import dstiff_colourmap, ntf_colourmap

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)
# 设置value的显示长度为100，默认为50
pd.set_option('max_colwidth', 100)
# pd.set_option('display.unicode.ambiguous_as_wide', True)
# pd.set_option('display.unicode.east_asian_width', True)


class SaveExcelData(object):
    def __init__(self, excel_path, car_id, se):
        self.full_excel_path = os.path.join(UPLOAD_DIR, excel_path)
        self.car_id = car_id
        self.se = se

    def common_update(self, df, table_model):
        now = datetime.now()
        insert_list = []
        for index in df.index:
            single_data = json.loads(json.dumps(df.loc[index].to_dict()))
            single_data.update({
                'car_info_id': self.car_id, 'update_time': now, 'create_time': now
            })
            insert_list.append(table_model(**single_data))
        self.se.query(table_model).filter(table_model.car_info_id == self.car_id).delete()
        self.se.add_all(insert_list)
        self.se.commit()

    def common_method(self, table_model):
        df = pd.read_excel(self.full_excel_path)
        df = df.round(2)
        df = df.astype(float)
        df = df.where(df.notnull(), None)
        df.rename(columns=get_orm_comment_dic(table_model), inplace=True)
        self.common_update(df, table_model)

    def save_modal_map(self):
        df = pd.read_excel(self.full_excel_path)
        df['Unnamed: 1'] = df['Unnamed: 1'].ffill()
        df['row_index'] = df['Unnamed: 1'] + '-' + df['Unnamed: 2']
        df.drop(labels=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2'], axis=1, inplace=True)
        df.set_index('row_index', inplace=True)
        df = df.round(2)
        df = df.astype(float)
        df = df.where(df.notnull(), None)
        df = df.T.reset_index()
        comment_dic = get_orm_comment_dic(ModalMap)
        comment_dic['index'] = 'value_range'
        df.rename(columns=comment_dic, inplace=True)
        self.common_update(df, ModalMap)

    def save_color_map(self, table_model, ai_method, ntf_str='ntf', dstiff=False):
        df = pd.read_excel(self.full_excel_path)
        if dstiff:
            ret_df = ai_method(df)
        else:
            ret_df = ai_method(df, ntf_str)
        ret_df.set_index('频率', inplace=True)
        comment_dic = table_model.comment_dic()
        insert_list = []
        now = datetime.now()
        for index in ret_df.index:
            for type_name, value in ret_df.loc[index].to_dict().items():
                single_add = {
                    'car_info_id': self.car_id, 'frequency_range': index, 'data_type': comment_dic[type_name],
                    'value': int(value), 'update_time': now, 'create_time': now
                }
                insert_list.append(table_model(**single_add))
        self.se.query(table_model).filter(table_model.car_info_id == self.car_id).delete()
        self.se.add_all(insert_list)
        self.se.commit()

    def save_dstiff(self):
        self.common_method(Dstiff)
        self.save_color_map(ColorMapDstiff, dstiff_colourmap, dstiff=True)

    def save_ntf_dr(self):
        self.common_method(NtfDr)
        self.save_color_map(ColorMapNtfDr, ntf_colourmap, ntf_str='ntf')

    def save_ntf_rr(self):
        self.common_method(NtfRr)
        self.save_color_map(ColorMapNtfRr, ntf_colourmap, ntf_str='ntf')

    def save_spindle_ntf_dr(self):
        self.common_method(SpindleNtfDr)
        self.save_color_map(ColorMapSpindleNtfDr, ntf_colourmap, ntf_str='spindle_ntf')

    def save_spindle_ntf_rr(self):
        self.common_method(SpindleNtfRr)
        self.save_color_map(ColorMapSpindleNtfRr, ntf_colourmap, ntf_str='spindle_ntf')

    def save_actual_test_data(self):
        self.common_method(ActualTestData)


def get_current_car_excel_data(se, car_info):
    car_excels = se.query(CarExcelData).filter(CarExcelData.car_info == car_info).all()
    car_excels_dic = {data.data_type: data for data in car_excels}

    ret_data = {}
    for data_type, type_name in CarExcelData.DATA_TYPE_CHOICES:
        car_excel_data = car_excels_dic.get(data_type)
        excel_name, excel_path = None, None
        if car_excel_data:
            excel_name = car_excel_data.excel_name or ''
            excel_path = car_excel_data.excel_path or ''
        ret_data[data_type] = [{'name': excel_name, 'url': excel_path}] if excel_name else []
    return ret_data


def get_freq_data_car_selects(se):
    car_excels = se.query(CarExcelData).all()
    ret_data = defaultdict(list)
    for car_excel in car_excels:
        ret_data[f'{car_excel.data_type.code}_car_list'].append({
            'id': car_excel.car_info_id,
            'car_name': car_excel.car_info.car_name
        })
    ret_data = dict(ret_data)
    return ret_data
