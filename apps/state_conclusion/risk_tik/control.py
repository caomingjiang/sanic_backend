from collections import defaultdict
from common.common import get_orm_comment_dic
from db import ModalMap


def get_risk_tik_dict(se, table_model, car_info):
    datas = se.query(table_model).filter(table_model.car_info == car_info, table_model.value <= 3)
    data_comment_dic = dict(table_model.DATA_TYPE_CHOICES)
    ret_dic = defaultdict(list)
    for data in datas:
        tmp_content = f'[{data.frequency_range}]Hz频段 “{data_comment_dic[data.data_type]}” 有路噪超标风险！'
        ret_dic[data.frequency_range].append(tmp_content)
    return dict(ret_dic)


def get_modal_map_risk_dic(se, car_info):
    comment_dic = get_orm_comment_dic(ModalMap)
    [comment_dic.pop(key) for key in ['车型', '值范围', '更新时间', '创建时间']]
    modal_map_objs = se.query(ModalMap).filter(
        ModalMap.car_info == car_info
    )
    ret_dic = defaultdict(list)
    for modal_map in modal_map_objs:
        value_range = modal_map.value_range
        for type_name, data_type in comment_dic.items():
            value = getattr(modal_map, data_type)
            if value:
                tmp_content = f'[{value_range}]Hz频段 “{type_name}” 有路噪超标风险！'
                ret_dic[value_range].append(tmp_content)
    return dict(ret_dic)


def get_dr_risk(modal_map_dic, dstiff_dic, ntf_dr_dic, spindle_ntf_dr_dic):
    frequency_ranges = set(list(modal_map_dic.keys()) + list(dstiff_dic.keys()) +
                           list(ntf_dr_dic.keys()) + list(spindle_ntf_dr_dic.keys()))
    frequency_ranges = sorted(frequency_ranges, key=lambda x: int(x.split('-')[0]), reverse=False)
    modal_map, dstiff, ntf_dr, spindle_ntf_dr = [], [], [], []
    for frequency_range in frequency_ranges:
        tmp_modal_map_list = modal_map_dic.get(frequency_range, [])
        tmp_dstiff_dic_list = dstiff_dic.get(frequency_range, [])
        tmp_ntf_dr_dic_list = ntf_dr_dic.get(frequency_range, [])
        tmp_spindle_ntf_dr_dic_list = spindle_ntf_dr_dic.get(frequency_range, [])
        tmp_list = tmp_modal_map_list + tmp_dstiff_dic_list + \
                   tmp_ntf_dr_dic_list + tmp_spindle_ntf_dr_dic_list
        if len(tmp_list) >= 5:
            modal_map.extend(tmp_modal_map_list)
            dstiff.extend(tmp_dstiff_dic_list)
            ntf_dr.extend(tmp_ntf_dr_dic_list)
            spindle_ntf_dr.extend(tmp_spindle_ntf_dr_dic_list)
    ret_data = {
        'modal_map': modal_map,
        'dstiff': dstiff,
        'ntf_dr': ntf_dr,
        'spindle_ntf_dr': spindle_ntf_dr,
    }
    return ret_data


def get_rr_risk(modal_map_dic, dstiff_dic, ntf_rr_dic, spindle_ntf_rr_dic):
    frequency_ranges = set(list(modal_map_dic.keys()) + list(dstiff_dic.keys()) +
                           list(ntf_rr_dic.keys()) + list(ntf_rr_dic.keys()))
    frequency_ranges = sorted(frequency_ranges, key=lambda x: int(x.split('-')[0]), reverse=False)
    modal_map, dstiff, ntf_rr, spindle_ntf_rr = [], [], [], []
    for frequency_range in frequency_ranges:
        tmp_modal_map_list = modal_map_dic.get(frequency_range, [])
        tmp_dstiff_dic_list = dstiff_dic.get(frequency_range, [])
        tmp_ntf_dr_dic_list = ntf_rr_dic.get(frequency_range, [])
        tmp_spindle_ntf_dr_dic_list = spindle_ntf_rr_dic.get(frequency_range, [])
        tmp_list = tmp_modal_map_list + tmp_dstiff_dic_list + \
                   tmp_ntf_dr_dic_list + tmp_spindle_ntf_dr_dic_list
        if len(tmp_list) >= 5:
            modal_map.extend(tmp_modal_map_list)
            dstiff.extend(tmp_dstiff_dic_list)
            ntf_rr.extend(tmp_ntf_dr_dic_list)
            spindle_ntf_rr.extend(tmp_spindle_ntf_dr_dic_list)
    ret_data = {
        'modal_map': modal_map,
        'dstiff': dstiff,
        'ntf_rr': ntf_rr,
        'spindle_ntf_rr': spindle_ntf_rr,
    }
    return ret_data


