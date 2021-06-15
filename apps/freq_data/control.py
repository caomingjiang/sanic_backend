import os
from db import ModalMap, Dstiff, NtfDr, NtfRr, SpindleNtfDr, SpindleNtfRr, ActualTestData, Session as db_session
from confs.config import UPLOAD_DIR
import pandas as pd
from datetime import datetime
from sqlalchemy.dialects.mysql import insert
from common.common import get_orm_comment_dic
from common.loggers import code_log
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
    def __init__(self, excel_path, car_id):
        self.full_excel_path = os.path.join(UPLOAD_DIR, excel_path)
        self.car_id = car_id

    def save_modal_map(self):
        se = db_session()
        try:
            now = datetime.now()
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
            for index in df.index:
                single_data = json.loads(json.dumps(df.loc[index].to_dict()))
                single_data.update({
                    'car_info_id': self.car_id, 'update_time': now, 'create_time': now
                })
                stmt = insert(ModalMap).values(**single_data)
                stmt = stmt.on_duplicate_key_update(**single_data)
                se.execute(stmt)
            se.commit()
        except Exception as e:
            code_log.exception('save_modal_map failed')
        finally:
            se.close()

    def save_dstiff(self):
        se = db_session()
        try:
            df = pd.read_excel(self.full_excel_path)
            df = df.round(2)
            df = df.astype(float)
            df = df.where(df.notnull(), None)
            df.rename(columns=get_orm_comment_dic(Dstiff), inplace=True)
            now = datetime.now()
            for index in df.index:
                single_data = json.loads(json.dumps(df.loc[index].to_dict()))
                single_data.update({
                    'car_info_id': self.car_id, 'update_time': now, 'create_time': now
                })
                stmt = insert(Dstiff).values(**single_data)
                stmt = stmt.on_duplicate_key_update(**single_data)
                se.execute(stmt)
            se.commit()
        except Exception as e:
            code_log.exception('save_dstiff failed')
        finally:
            se.close()

    def save_ntf_dr(self):
        se = db_session()
        try:
            df = pd.read_excel(self.full_excel_path)
            df = df.round(2)
            df = df.astype(float)
            df = df.where(df.notnull(), None)
            df.rename(columns=get_orm_comment_dic(NtfDr), inplace=True)
            now = datetime.now()
            for index in df.index:
                single_data = json.loads(json.dumps(df.loc[index].to_dict()))
                single_data.update({
                    'car_info_id': self.car_id, 'update_time': now, 'create_time': now
                })
                stmt = insert(NtfDr).values(**single_data)
                stmt = stmt.on_duplicate_key_update(**single_data)
                se.execute(stmt)
            se.commit()
        except Exception as e:
            code_log.exception('save_dstiff failed')
        finally:
            se.close()

    def save_ntf_rr(self):
        se = db_session()
        try:
            df = pd.read_excel(self.full_excel_path)
            df = df.round(2)
            df = df.astype(float)
            df = df.where(df.notnull(), None)
            df.rename(columns=get_orm_comment_dic(NtfRr), inplace=True)
            now = datetime.now()
            for index in df.index:
                single_data = json.loads(json.dumps(df.loc[index].to_dict()))
                single_data.update({
                    'car_info_id': self.car_id, 'update_time': now, 'create_time': now
                })
                stmt = insert(NtfRr).values(**single_data)
                stmt = stmt.on_duplicate_key_update(**single_data)
                se.execute(stmt)
            se.commit()
        except Exception as e:
            code_log.exception('save_ntf_rr failed')
        finally:
            se.close()

    def save_spindle_ntf_dr(self):
        se = db_session()
        try:
            df = pd.read_excel(self.full_excel_path)
            df = df.round(2)
            df = df.astype(float)
            df = df.where(df.notnull(), None)
            df.rename(columns=get_orm_comment_dic(SpindleNtfDr), inplace=True)
            now = datetime.now()
            for index in df.index:
                single_data = json.loads(json.dumps(df.loc[index].to_dict()))
                single_data.update({
                    'car_info_id': self.car_id, 'update_time': now, 'create_time': now
                })
                stmt = insert(SpindleNtfDr).values(**single_data)
                stmt = stmt.on_duplicate_key_update(**single_data)
                se.execute(stmt)
            se.commit()
        except Exception as e:
            code_log.exception('save_spindle_ntf_dr failed')
        finally:
            se.close()

    def save_spindle_ntf_rr(self):
        se = db_session()
        try:
            df = pd.read_excel(self.full_excel_path)
            df = df.round(2)
            df = df.astype(float)
            df = df.where(df.notnull(), None)
            df.rename(columns=get_orm_comment_dic(SpindleNtfRr), inplace=True)
            now = datetime.now()
            for index in df.index:
                single_data = json.loads(json.dumps(df.loc[index].to_dict()))
                single_data.update({
                    'car_info_id': self.car_id, 'update_time': now, 'create_time': now
                })
                stmt = insert(SpindleNtfRr).values(**single_data)
                stmt = stmt.on_duplicate_key_update(**single_data)
                se.execute(stmt)
            se.commit()
        except Exception as e:
            code_log.exception('save_spindle_ntf_rr failed')
        finally:
            se.close()

    def save_actual_test_data(self):
        se = db_session()
        try:
            df = pd.read_excel(self.full_excel_path)
            df = df.round(2)
            df = df.astype(float)
            df = df.where(df.notnull(), None)
            df.rename(columns=get_orm_comment_dic(ActualTestData), inplace=True)
            now = datetime.now()
            for index in df.index:
                single_data = json.loads(json.dumps(df.loc[index].to_dict()))
                single_data.update({
                    'car_info_id': self.car_id, 'update_time': now, 'create_time': now
                })
                stmt = insert(ActualTestData).values(**single_data)
                stmt = stmt.on_duplicate_key_update(**single_data)
                se.execute(stmt)
            se.commit()
        except Exception as e:
            code_log.exception('save_actual_test_data failed')
        finally:
            se.close()