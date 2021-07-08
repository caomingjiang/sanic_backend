import os
from db import ModalMap, Dstiff, NtfDr, NtfRr, SpindleNtfDr, SpindleNtfRr, ActualTestData, CarExcelData, \
    ColorMapDstiff, ColorMapNtfDr, ColorMapNtfRr, ColorMapSpindleNtfDr, ColorMapSpindleNtfRr, \
    ColorMapActualTestData, WCarExcelData, Session, TotalColorMapData
from confs.config import UPLOAD_DIR, CommonThreadPool
import pandas as pd
from datetime import datetime
from common.common import get_orm_comment_dic
from common.loggers import code_log
import json
from collections import defaultdict
from ai.noise_algo_func import dstiff_colourmap, ntf_colourmap, realcapture_colourmap, Multi_Score_Predict
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


class SaveExcelData(object):
    def __init__(self, excel_path, car_id, bs_type, se):
        self.full_excel_path = os.path.join(UPLOAD_DIR, excel_path)
        self.car_id = car_id
        self.bs_type = bs_type
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
        new_ret_df = ret_df.set_index('频率')
        comment_dic = table_model.comment_dic()
        insert_list = []
        now = datetime.now()
        for index in new_ret_df.index:
            for type_name, value in new_ret_df.loc[index].to_dict().items():
                single_add = {
                    'car_info_id': self.car_id, 'frequency_range': index, 'data_type': comment_dic[type_name],
                    'value': int(value), 'update_time': now, 'create_time': now
                }
                insert_list.append(table_model(**single_add))
        self.se.query(table_model).filter(table_model.car_info_id == self.car_id).delete()
        self.se.add_all(insert_list)
        self.se.commit()
        return ret_df

    def save_actual_color_map(self):
        df = realcapture_colourmap(pd.read_excel(self.full_excel_path))
        now = datetime.now()
        insert_list = []
        for df_index in df.index:
            row_dic = df.loc[df_index].to_dict()
            insert_list.append(ColorMapActualTestData(
                car_info_id=self.car_id, frequency_range=row_dic['频率'],
                dr_value=float(round(row_dic['实测_Driver'], 2)),
                rr_value=float(round(row_dic['实测_RR-Passenger'], 2)),
                update_time=now, create_time=now
            ))
        self.se.query(ColorMapActualTestData).filter(ColorMapActualTestData.car_info_id == self.car_id).delete()
        self.se.add_all(insert_list)
        self.se.commit()

    @staticmethod
    def cal_total_color_map(car_id, save_type, color_map_df, bs_type):
        se = Session()
        try:
            data_types = ['dstiff', 'ntf_dr', 'ntf_rr', 'spindle_ntf_dr', 'spindle_ntf_rr']
            new_data_types = copy.deepcopy(data_types)
            new_data_types.remove(save_type)
            car_files = se.query(CarExcelData).filter(
                CarExcelData.car_info_id == car_id,
                CarExcelData.data_type.in_(new_data_types),
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
            colourmap_dict.update({save_type: color_map_df})
            if len(data_types) != len(list(colourmap_dict.keys())):
                raise Exception('原始输入文件不足')
            w_car_files = se.query(WCarExcelData).filter(WCarExcelData.bs_type == bs_type)
            weights_dict = {}
            for w_car_file in w_car_files:
                excel_path = w_car_file.excel_path
                if excel_path:
                    weights_dict[w_car_file.data_type.code] = pd.read_excel(os.path.join(UPLOAD_DIR, excel_path))
            if len(data_types) != len(list(weights_dict.keys())):
                raise Exception('专家设定权重文件不足')
            dr_score, rr_score = Multi_Score_Predict(colourmap_dict, weights_dict)
            frequency_range_list = color_map_df['频率'].to_list()
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
            code_log.exception('cal_total_color_map failed')
        finally:
            se.close()

    def save_dstiff(self):
        self.common_method(Dstiff)
        color_map_df = self.save_color_map(ColorMapDstiff, dstiff_colourmap, dstiff=True)
        CommonThreadPool.submit(
            self.cal_total_color_map, self.car_id, 'dstiff', color_map_df, self.bs_type
        )

    def save_ntf_dr(self):
        self.common_method(NtfDr)
        color_map_df = self.save_color_map(ColorMapNtfDr, ntf_colourmap, ntf_str='ntf')
        CommonThreadPool.submit(
            self.cal_total_color_map, self.car_id, 'ntf_dr', color_map_df, self.bs_type
        )

    def save_ntf_rr(self):
        self.common_method(NtfRr)
        color_map_df = self.save_color_map(ColorMapNtfRr, ntf_colourmap, ntf_str='ntf')
        CommonThreadPool.submit(
            self.cal_total_color_map, self.car_id, 'ntf_rr', color_map_df, self.bs_type
        )

    def save_spindle_ntf_dr(self):
        self.common_method(SpindleNtfDr)
        color_map_df = self.save_color_map(ColorMapSpindleNtfDr, ntf_colourmap, ntf_str='spindle_ntf')
        CommonThreadPool.submit(
            self.cal_total_color_map, self.car_id, 'spindle_ntf_dr', color_map_df, self.bs_type
        )

    def save_spindle_ntf_rr(self):
        self.common_method(SpindleNtfRr)
        color_map_df = self.save_color_map(ColorMapSpindleNtfRr, ntf_colourmap, ntf_str='spindle_ntf')
        CommonThreadPool.submit(
            self.cal_total_color_map, self.car_id, 'spindle_ntf_rr', color_map_df, self.bs_type
        )

    def save_actual_test_data(self):
        self.common_method(ActualTestData)
        self.save_actual_color_map()


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
