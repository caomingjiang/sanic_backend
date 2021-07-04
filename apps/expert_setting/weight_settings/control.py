import os
from db import WCarExcelData, WDstiff, WNtfDr, WNtfRr, WSpindleNtfDr, WSpindleNtfRr, Session, CarExcelData, \
    TotalColorMapData
from ai.noise_algo_func import dstiff_colourmap, ntf_colourmap, Multi_Score_Predict
from confs.config import UPLOAD_DIR, CommonThreadPool
import pandas as pd
from datetime import datetime
from collections import defaultdict
from common.loggers import code_log
import copy


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

    @staticmethod
    def cal_total_color_map(car_id, save_type, weight_df):
        se = Session()
        try:
            data_types = ['dstiff', 'ntf_dr', 'ntf_rr', 'spindle_ntf_dr', 'spindle_ntf_rr']
            car_files = se.query(CarExcelData).filter(
                CarExcelData.car_info_id == car_id,
                CarExcelData.data_type.in_(data_types),
            )
            colourmap_dict = {}
            for car_file in car_files:
                excel_path = car_file.excel_path
                if excel_path:
                    excel_df = pd.read_excel(os.path.join(UPLOAD_DIR, excel_path))
                    data_type = car_file.data_type.code
                    if data_type == 'dstiff':
                        single_color_map_df = dstiff_colourmap(excel_df)
                    else:
                        cal_str = 'spindle_ntf' if 'spindle' in data_type else 'ntf'
                        single_color_map_df = ntf_colourmap(excel_df, cal_str)
                    colourmap_dict[data_type] = single_color_map_df
            if len(data_types) != len(list(colourmap_dict.keys())):
                raise Exception('原始输入文件不足')

            new_data_types = copy.deepcopy(data_types)
            new_data_types.remove(save_type)
            w_car_files = se.query(WCarExcelData).filter(
                WCarExcelData.car_info_id == car_id, WCarExcelData.data_type.in_(new_data_types)
            )
            weights_dict = {}
            for w_car_file in w_car_files:
                excel_path = w_car_file.excel_path
                if excel_path:
                    weights_dict[w_car_file.data_type.code] = pd.read_excel(os.path.join(UPLOAD_DIR, excel_path))
            weights_dict.update({save_type: weight_df})
            if len(data_types) != len(list(weights_dict.keys())):
                raise Exception('专家设定权重文件不足')
            dr_score, rr_score = Multi_Score_Predict(colourmap_dict, weights_dict)
            frequency_range_list = colourmap_dict['dstiff']['频率'].to_list()
            insert_list = []
            now = datetime.now()
            for index, frequency_range in enumerate(frequency_range_list):
                insert_list.append(TotalColorMapData(
                    car_info_id=car_id, frequency_range=frequency_range,
                    dr_value=float(round(dr_score[index], 2)), rr_value=float(round(rr_score[index], 2)),
                    update_time=now, create_time=now
                ))
            se.query(TotalColorMapData).filter(TotalColorMapData.car_info_id == car_id).delete()
            se.add_all(insert_list)
            se.commit()
        except Exception as e:
            code_log.exception('expert cal_total_color_map failed')
        finally:
            se.close()

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
        CommonThreadPool.submit(self.cal_total_color_map, self.car_id, 'dstiff', pd.read_excel(self.full_excel_path))

    def save_ntf_dr(self):
        self.common_method(WNtfDr)
        CommonThreadPool.submit(self.cal_total_color_map, self.car_id, 'ntf_dr', pd.read_excel(self.full_excel_path))

    def save_ntf_rr(self):
        self.common_method(WNtfRr)
        CommonThreadPool.submit(self.cal_total_color_map, self.car_id, 'ntf_rr', pd.read_excel(self.full_excel_path))

    def save_spindle_ntf_dr(self):
        self.common_method(WSpindleNtfDr)
        CommonThreadPool.submit(self.cal_total_color_map, self.car_id, 'spindle_ntf_dr', pd.read_excel(self.full_excel_path))

    def save_spindle_ntf_rr(self):
        self.common_method(WSpindleNtfRr)
        CommonThreadPool.submit(self.cal_total_color_map, self.car_id, 'spindle_ntf_rr', pd.read_excel(self.full_excel_path))


def get_current_car_excel_data(se, car_info):
    car_excels = se.query(WCarExcelData).filter(WCarExcelData.car_info == car_info).all()
    car_excels_dic = {data.data_type: data for data in car_excels}

    ret_data = {}
    for data_type, type_name in WCarExcelData.DATA_TYPE_CHOICES:
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
