import os
from db import Session, CarExcelData, WCarExcelData, TotalColorMapData
from ai.noise_algo_func import ntf_colourmap, dstiff_colourmap, Multi_Score_Predict
from confs.config import UPLOAD_DIR
from datetime import datetime
from common.loggers import code_log
import pandas as pd


def cal_total_color_map(car_id, bs_type):
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
        w_car_files = se.query(WCarExcelData).filter(WCarExcelData.bs_type == bs_type)
        weights_dict = {}
        for w_car_file in w_car_files:
            excel_path = w_car_file.excel_path
            if excel_path:
                weights_dict[w_car_file.data_type.code] = pd.read_excel(os.path.join(UPLOAD_DIR, excel_path))
        if len(data_types) != len(list(weights_dict.keys())):
            raise Exception('专家设定权重文件不足')
        frequency_range_list = colourmap_dict['dstiff']['频率'].to_list()
        dr_score, rr_score = Multi_Score_Predict(colourmap_dict, weights_dict)
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
        code_log.exception('sound_predict cal_total_color_map failed')
    finally:
        se.close()