import os
from db import Session, CarExcelData, WCarExcelData, TotalColorMapData, SubsystemScoring, \
    ColorMapActualTestData, DataConfigs
from ai.noise_algo_func import ntf_colourmap, dstiff_colourmap, Multi_Score_Predict
from apps.state_conclusion.color_map.control import ColorMapData
from confs.config import UPLOAD_DIR, CommonThreadPool
from datetime import datetime
from common.loggers import code_log
import pandas as pd
import xlwt
from io import BytesIO


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
                data_type = data_type.replace('ntf_', '') if 'spindle' in data_type else data_type
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
            data_type = w_car_file.data_type.code
            data_type = data_type.replace('ntf_', '') if 'spindle' in data_type else data_type
            if excel_path:
                weights_dict[data_type] = pd.read_excel(os.path.join(UPLOAD_DIR, excel_path))
        if len(data_types) != len(list(weights_dict.keys())):
            raise Exception('专家设定权重文件不足')
        frequency_range_list = colourmap_dict['dstiff']['频率'].to_list()
        dr_score, rr_score, sub_score = Multi_Score_Predict(colourmap_dict, weights_dict)
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

        insert_list = []
        for key, value in sub_score.items():
            insert_list.append(SubsystemScoring(
                car_info_id=car_id, data_type=key, value=round(float(value), 2), update_time=now, create_time=now
            ))
        se.query(SubsystemScoring).filter(SubsystemScoring.car_info_id == car_id).delete()
        se.add_all(insert_list)
        se.commit()
    except Exception as e:
        code_log.exception('sound_predict cal_total_color_map failed')
    finally:
        se.close()


def get_base_data(se, car_info):
    cma_datas = se.query(ColorMapActualTestData).filter(
        ColorMapActualTestData.car_info == car_info
    ).order_by(ColorMapActualTestData.id.asc())
    tcm_datas = se.query(TotalColorMapData).filter(
        TotalColorMapData.car_info == car_info
    ).order_by(TotalColorMapData.id.asc()).all()

    if not tcm_datas:
        backend_suspension = car_info.backend_suspension
        bs_type = DataConfigs.BACKEND_SUSPENSION_CONFS[backend_suspension]
        CommonThreadPool.submit(cal_total_color_map, car_info.id, bs_type)

    xaxis_list = []
    cma_dr_list, cma_rr_list = [], []
    for cma_data in cma_datas:
        xaxis_list.append(cma_data.frequency_range)
        cma_dr_list.append(cma_data.dr_value)
        cma_rr_list.append(cma_data.rr_value)
    tcm_dr_list, tcm_rr_list = [], []
    new_xaxis_list = []
    for tcm_data in tcm_datas:
        new_xaxis_list.append(tcm_data.frequency_range)
        tcm_dr_list.append(tcm_data.dr_value)
        tcm_rr_list.append(tcm_data.rr_value)

    sub_score_objs = se.query(SubsystemScoring).filter(SubsystemScoring.car_info_id == car_info.id)
    sub_score_data = []
    sub_comment_dic = dict(SubsystemScoring.DATA_TYPE_CHOICES)
    for sub_score_obj in sub_score_objs:
        sub_score_data.append({
            'data_type': sub_comment_dic[sub_score_obj.data_type.code],
            'value': sub_score_obj.value
        })
    ret_data = {
        'xaxis_list': xaxis_list or new_xaxis_list,
        'cma_dr_list': cma_dr_list,
        'cma_rr_list': cma_rr_list,
        'tcm_dr_list': tcm_dr_list,
        'tcm_rr_list': tcm_rr_list,
        'sub_score_data': sub_score_data
    }
    return ret_data


def export_excel(se, car_info):
    base_data = get_base_data(se, car_info)
    wb = xlwt.Workbook(encoding='utf8')
    ws = wb.add_sheet('声压预测')
    ws.col(0).width = 256 * 20
    row_num = 0
    xaxis = base_data['xaxis_list']
    ws.write_merge(row_num, row_num, 0, 28, 'Driver', ColorMapData.get_cell_style(11, 57, bold=True))
    row_num += 1
    ws.write(row_num, 0, '', ColorMapData.get_cell_style(11, 1, bold=True))
    for col, x in enumerate(xaxis):
        ws.write(row_num, col + 1, x, ColorMapData.get_cell_style(11, 1, bold=True))
    row_num += 1
    ws.write(row_num, 0, '实测值_DR', ColorMapData.get_cell_style(11, 1, bold=True))
    for col, value in enumerate(base_data['cma_dr_list']):
        ws.write(row_num, col + 1, value, ColorMapData.get_cell_style(11, 1, bold=False))
    row_num += 1
    ws.write(row_num, 0, '识别声压_DR', ColorMapData.get_cell_style(11, 1, bold=True))
    for col, value in enumerate(base_data['tcm_dr_list']):
        ws.write(row_num, col + 1, value, ColorMapData.get_cell_style(11, 1, bold=False))

    row_num += 3
    xaxis = base_data['xaxis_list']
    ws.write_merge(row_num, row_num, 0, 28, 'RR passenger', ColorMapData.get_cell_style(11, 57, bold=True))
    row_num += 1
    ws.write(row_num, 0, '', ColorMapData.get_cell_style(11, 1, bold=True))
    for col, x in enumerate(xaxis):
        ws.write(row_num, col + 1, x, ColorMapData.get_cell_style(11, 1, bold=True))
    row_num += 1
    ws.write(row_num, 0, '实测值_RR', ColorMapData.get_cell_style(11, 1, bold=True))
    for col, value in enumerate(base_data['cma_rr_list']):
        ws.write(row_num, col + 1, value, ColorMapData.get_cell_style(11, 1, bold=False))
    row_num += 1
    ws.write(row_num, 0, '识别声压_RR', ColorMapData.get_cell_style(11, 1, bold=True))
    for col, value in enumerate(base_data['tcm_rr_list']):
        ws.write(row_num, col + 1, value, ColorMapData.get_cell_style(11, 1, bold=False))

    row_num += 3
    ws.write_merge(row_num, row_num, 0, 1, '子系统评分', ColorMapData.get_cell_style(11, 57, bold=True))
    row_num += 1
    ws.write(row_num, 0, '四连杆', ColorMapData.get_cell_style(11, 1, bold=True))
    ws.write(row_num, 1, '分数', ColorMapData.get_cell_style(11, 1, bold=True))
    row_num += 1
    for data in base_data['sub_score_data']:
        ws.write(row_num, 0, data['data_type'], ColorMapData.get_cell_style(11, 1, bold=True))
        ws.write(row_num, 1, data['value'], ColorMapData.get_cell_style(11, 1, bold=False))
        row_num += 1

    bio = BytesIO()
    wb.save(bio)
    return bio.getvalue()

