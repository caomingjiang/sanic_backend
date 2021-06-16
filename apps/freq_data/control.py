import os
from db import ModalMap, Dstiff, NtfDr, NtfRr, SpindleNtfDr, SpindleNtfRr, ActualTestData
from confs.config import UPLOAD_DIR
import pandas as pd
from datetime import datetime
from common.common import get_orm_comment_dic
import json

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

    def save_dstiff(self):
        self.common_method(Dstiff)

    def save_ntf_dr(self):
        self.common_method(NtfDr)

    def save_ntf_rr(self):
        self.common_method(NtfRr)

    def save_spindle_ntf_dr(self):
        self.common_method(SpindleNtfDr)

    def save_spindle_ntf_rr(self):
        self.common_method(SpindleNtfRr)

    def save_actual_test_data(self):
        self.common_method(ActualTestData)