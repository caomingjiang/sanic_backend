#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 23:41:12 2021

@author: liangdongkai
"""

import pandas as pd 
import numpy as np
from ai.map_dict_utils import *
from bisect import bisect_left, bisect_right

def single_fuchejia_all_func(data_map):
    '''
    data_map: dict
              {'key1':'value1','key2':'value2', ...}
    '''
    score = 0.0
    for key, value in data_map.items():
        score += 0.2 * float(value)

    return score

def get_loc(i, li):
    for index, value in enumerate(li):
        if i < value:
            return index
        else:
            return index + 1

def single_fuchejia_func(key, value, fuchejia):
    '''
    key: name1_name2
    value: input value
    fuchejia: fuchejia single parmas
    '''

    thres_array = fuchejia[key][0]
    score = fuchejia[key][1]

    index = bisect_left(thres_array, value)
    # index = bisect_right(thres_array, value)

    if index < len(score):
        if key in ['轮胎_胎面辐射声（轮胎选型）', '轮胎_力传递峰值', '轮胎_力传递峰值频率']:
            return 10 - score[index]
        else:
            return score[index]
    else:
        return 'error'


def single_xiabaibi_func(key, value, xiabaibi):
    '''
    key: name1_name2
    value: input value
    xiabaibi: xiabaibi single params
    '''

    thres_array = xiabaibi[key][0]
    score = xiabaibi[key][1]
    # index = get_loc(value, thres_array)

    index = bisect_left(thres_array, value)
    # index = bisect_right(thres_array, value)

    if index < len(score):
        return score[index]
    else:
        return 'error'

def single_cheshen_func(key, value, cheshen):
    '''
    key: name1_name2
    value: input value
    cheshen: cheshen single params
    '''
    if 'Check' in key:
        if value in cheshen[key].keys():
            return cheshen[key][value]
        else:
            return 'error'
    else:
        thres_array = cheshen[key][0]
        score = cheshen[key][1]
        # index = get_loc(value, thres_array)

        index = bisect_left(thres_array, value)
        # index = bisect_right(thres_array, value)

        if index < len(score):
            return score[index]
        else:
            return 'error'

def dstiff_colourmap(ori_df, dstiff_target_map):
    '''
    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_Dstiff.xlsx')
    '''
    ori_df.drop(ori_df.index[-1],inplace=True)
    frequency = ori_df['频率'].apply(lambda x:int(x/10))
    ori_df = ori_df.drop('频率', axis=1).apply(np.square)
    ori_df['频率'] = frequency
    
    rms_df = ori_df.groupby("频率").sum().apply(lambda x:x/10).apply(np.sqrt)
    frequency = rms_df.reset_index()['频率'].apply(lambda x:str(x*10)+'-'+str((x+1)*10))
    
    score_df = pd.DataFrame()
    score_df['频率'] = frequency
    for column in rms_df.columns:
        target = dstiff_target_map[column]
        score_ = rms_df[column].apply(lambda x: dstiff_score(x, target))
        score_df[column] = score_.tolist()
        
    return score_df

######ntf
def ntf_colourmap(ori_df, type_name):
    '''
    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_NTF-DR.xlsx')
    type_name: [ntf, spindle_ntf]
    '''
    ori_df.drop(ori_df.index[-1],inplace=True)
    frequency = ori_df['频率'].apply(lambda x:int(x/10))
    ori_df = ori_df.drop('频率', axis=1).apply(np.square)
    ori_df['频率'] = frequency
    
    rms_df = ori_df.groupby("频率").sum().apply(lambda x:x/10).apply(np.sqrt)
    frequency = rms_df.reset_index()['频率'].apply(lambda x:str(x*10)+'-'+str((x+1)*10))
    
    score_df = pd.DataFrame()
    score_df['频率'] = frequency
    for column in rms_df.columns:
        if type_name == 'ntf':
            score_ = rms_df[column].apply(lambda x: ntf_score(x))
        elif type_name == 'spindle_ntf':
            score_ = rms_df[column].apply(lambda x: spindle_ntf_score(x))
        score_df[column] = score_.tolist()
        
    return score_df

######real_colourmap
def realcapture_colourmap(ori_df):
    '''
    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_实测曲线.xlsx')
    '''
    ori_df.drop(ori_df.index[-1], inplace=True)
    frequency = ori_df['频率'].apply(lambda x: int(x / 10))
    ori_df = ori_df.drop('频率', axis=1).apply(np.square)
    ori_df['频率'] = frequency

    rms_df = ori_df.groupby("频率").sum().apply(lambda x: x / 10).apply(np.sqrt)
    frequency = rms_df.reset_index()['频率'].apply(lambda x: str(x * 10) + '-' + str((x + 1) * 10))

    score_df = pd.DataFrame()
    score_df['频率'] = frequency
    for column in rms_df.columns:
        score_df[column] = rms_df[column].tolist()  ####主意tolist的坑

    return score_df

def sum_matrix(matrix):
    return sum(np.sum(matrix,axis=0))


def Multi_Score_Predict(colourmap_dict, weights_dict, artifical_params):
    '''
    colourmap_dict : dstff_df, ntf_df, spindle_ntf_df,
    weights_map : weights_df，
    artifical_params：人工系数包含调整因子adjust_value和除以系数div_hyper_params(list)
    '''
    sub_score = {}
    x = colourmap_dict['dstiff'].drop('频率', 1).T.values
    y = weights_dict['dstiff'].drop('name', 1).drop('dim', 1).values
    dstff_matrix = x * y

    full_score = np.array([[10] * len(x[0])] * len(x))
    sub_dstff = full_score * y
    sub_score['dstiff'] = sum_matrix(dstff_matrix) / sum_matrix(sub_dstff) * 100

    ##########################################################
    x = colourmap_dict['ntf_dr'].drop('频率', 1).T.values
    y = weights_dict['ntf_dr'].drop('name', 1).drop('dim', 1).values
    ntf_dr_matrix = x * y

    full_score = np.array([[10] * len(x[0])] * len(x))
    sub_ntf_dr = full_score * y
    sub_score['ntf_dr'] = sum_matrix(ntf_dr_matrix) / sum_matrix(sub_ntf_dr) * 100

    ##########################################################
    x = colourmap_dict['ntf_rr'].drop('频率', 1).T.values
    y = weights_dict['ntf_rr'].drop('name', 1).drop('dim', 1).values
    ntf_rr_matrix = x * y

    full_score = np.array([[10] * len(x[0])] * len(x))
    sub_ntf_rr = full_score * y
    sub_score['ntf_rr'] = sum_matrix(ntf_rr_matrix) / sum_matrix(sub_ntf_rr) * 100

    ##########################################################
    x = colourmap_dict['spindle_dr'].drop('频率', 1).T.values
    y = weights_dict['spindle_dr'].drop('name', 1).drop('dim', 1).values
    spindle_dr_matrix = x * y

    full_score = np.array([[10] * len(x[0])] * len(x))
    sub_spindle_dr = full_score * y
    sub_score['spindle_dr'] = sum_matrix(spindle_dr_matrix) / sum_matrix(sub_spindle_dr) * 100

    ##########################################################
    x = colourmap_dict['spindle_rr'].drop('频率', 1).T.values
    y = weights_dict['spindle_rr'].drop('name', 1).drop('dim', 1).values
    spindle_rr_matrix = x * y

    full_score = np.array([[10] * len(x[0])] * len(x))
    sub_spindle_rr = full_score * y
    sub_score['sub_spindle_rr'] = sum_matrix(spindle_rr_matrix) / sum_matrix(sub_spindle_rr) * 100

    DR_score = []
    for index, (d, ntf, spin) in enumerate(zip(dstff_matrix.T, ntf_dr_matrix.T, spindle_dr_matrix.T)):
        aggregate = sum(d) + sum(ntf) + sum(spin)
        DR_score.append(artifical_params['adjust_value'] - aggregate / artifical_params['div_hyper_params'][index])

    RR_score = []
    for index, (d, ntf, spin) in enumerate(zip(dstff_matrix.T, ntf_rr_matrix.T, spindle_rr_matrix.T)):
        aggregate = sum(d) + sum(ntf) + sum(spin)
        RR_score.append(artifical_params['adjust_value'] - aggregate / artifical_params['div_hyper_params'][index])

    return DR_score, RR_score, sub_score

def test():
    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_Dstiff.xlsx')
    dstiff_colourmap_data = dstiff_colourmap(ori_df)

    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_NTF-DR.xlsx')
    ntf_dr_colourmap = ntf_colourmap(ori_df, 'ntf')

    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_NTF-RR.xlsx')
    ntf_rr_colourmap = ntf_colourmap(ori_df, 'ntf')

    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_SpindleNTF-DR.xlsx')
    spindle_dr_colourmap = ntf_colourmap(ori_df, 'spindle_ntf')

    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_SpindleNTF-RR.xlsx')
    spindle_rr_colourmap = ntf_colourmap(ori_df, 'spindle_ntf')

    colourmap_dict = {}
    colourmap_dict['dstiff'] = dstiff_colourmap_data
    colourmap_dict['ntf_dr'] = ntf_dr_colourmap
    colourmap_dict['ntf_rr'] = ntf_rr_colourmap
    colourmap_dict['spindle_dr'] = spindle_dr_colourmap
    colourmap_dict['spindle_rr'] = spindle_rr_colourmap

    weights_dstiff = pd.read_excel('./权系数/专家权重-DSTIFF.xlsx')
    weights_ntf_dr = pd.read_excel('./权系数/专家权重-NTF-DR.xlsx')
    weights_ntf_rr = pd.read_excel('./权系数/专家权重-NTF-RR.xlsx')
    weights_spindle_dr = pd.read_excel('./权系数/专家权重-Spindle-NTF-DR.xlsx')
    weights_spindle_rr = pd.read_excel('./权系数/专家权重-Spindle-NTF-RR.xlsx')

    weights_dict = {}
    weights_dict['dstiff'] = weights_dstiff
    weights_dict['ntf_dr'] = weights_ntf_dr
    weights_dict['ntf_rr'] = weights_ntf_rr
    weights_dict['spindle_dr'] = weights_spindle_dr
    weights_dict['spindle_rr'] = weights_spindle_rr

    DR_score, RR_score, sub_score = Multi_Score_Predict(colourmap_dict, weights_dict)

if __name__ == "__main__":
    
    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_实测曲线.xlsx')
    real_colourmap = realcapture_colourmap(ori_df)

    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_Dstiff.xlsx')
    dstiff_colourmap_data = dstiff_colourmap(ori_df)

    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_NTF-DR.xlsx')
    ntf_dr_colourmap = ntf_colourmap(ori_df, 'ntf')

    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_NTF-RR.xlsx')
    ntf_rr_colourmap = ntf_colourmap(ori_df, 'ntf')

    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_SpindleNTF-DR.xlsx')
    spindle_dr_colourmap = ntf_colourmap(ori_df, 'spindle_ntf')

    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_SpindleNTF-RR.xlsx')
    spindle_rr_colourmap = ntf_colourmap(ori_df, 'spindle_ntf')

    colourmap_dict = {}
    colourmap_dict['dstiff'] = dstiff_colourmap_data
    colourmap_dict['ntf_dr'] = ntf_dr_colourmap
    colourmap_dict['ntf_rr'] = ntf_rr_colourmap
    colourmap_dict['spindle_dr'] = spindle_dr_colourmap
    colourmap_dict['spindle_rr'] = spindle_rr_colourmap

    weights_dstiff = pd.read_excel('./权系数/专家权重-DSTIFF.xlsx')
    weights_ntf_dr = pd.read_excel('./权系数/专家权重-NTF-DR.xlsx')
    weights_ntf_rr = pd.read_excel('./权系数/专家权重-NTF-RR.xlsx')
    weights_spindle_dr = pd.read_excel('./权系数/专家权重-Spindle-NTF-DR.xlsx')
    weights_spindle_rr = pd.read_excel('./权系数/专家权重-Spindle-NTF-RR.xlsx')

    weights_dict = {}
    weights_dict['dstiff'] = weights_dstiff
    weights_dict['ntf_dr'] = weights_ntf_dr
    weights_dict['ntf_rr'] = weights_ntf_rr
    weights_dict['spindle_dr'] = weights_spindle_dr
    weights_dict['spindle_rr'] = weights_spindle_rr

    DR_score, RR_score, sub_score = Multi_Score_Predict(colourmap_dict, weights_dict)
    
    fuchejia = {
	"轮胎_胎面辐射声（轮胎选型）":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"轮胎_力传递峰值频率":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"轮胎_力传递峰值":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"轮胎_操稳性能":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"轮胎_耐久性能":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"轮辋刚度_16-17’":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"轮辋刚度_18-19’":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"前副车架（自由-自由）_全副车架(bend)模态":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"前副车架（自由-自由）_半副车架(bend)模态":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"后副车架（自由-自由）_类型一：扭转梁(bend)模态":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"后副车架（自由-自由）_类型二：多连杆(横梁弯曲)模态":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]]
}

    a = {
	"前下摆臂handling衬套_X向静刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"前下摆臂handling衬套_Y向静刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"前下摆臂handling衬套_Z向静刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"前下摆臂handling衬套_操稳性能":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"前下摆臂handling衬套_耐久性能":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"前下摆臂ride衬套_X向静刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"前下摆臂ride衬套_Y向静刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"前下摆臂ride衬套_Z向静刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"前下摆臂ride衬套_操稳性能":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"前下摆臂ride衬套_耐久性能":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"后副车架前衬套_X向静刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"后副车架前衬套_Y向静刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"后副车架前衬套_Z向静刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"后副车架前衬套_操稳性能":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"后副车架前衬套_耐久性能":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"后副车架后衬套_X向静刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"后副车架后衬套_Y向静刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"后副车架后衬套_Z向静刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"后副车架后衬套_操稳性能":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"后副车架后衬套_耐久性能":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"刀锋臂衬套_X向静刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"刀锋臂衬套_Y向静刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"刀锋臂衬套_Z向静刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"刀锋臂衬套_操稳性能":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"刀锋臂衬套_耐久性能":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]]
}


    b = {
	"白车身_全局扭转模态频率":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"白车身_全局弯曲模态频率":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"C ring_Visual Check":{"A":10,"B":8,"C":6,"D":4},
	"前围_大板刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"一号梁_Visual Check":{"A":10,"B":8,"C":6,"D":4},
	"地板_大板刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"地板无支撑板面积_Visual Check":{"A":10,"B":8,"C":6,"D":4},
	"备胎舱地板_大板刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"备胎舱加强板设计_Visual Check":{"A":10,"B":8,"C":6,"D":4},
	"顶棚_大板刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"顶棚结构_Visual Check":{"A":10,"B":8,"C":6,"D":4},
	"左轮罩内板_大板刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"后减震器加强板_Visual Check":{"A":10,"B":8,"C":6,"D":4},
	"右轮罩内板_大板刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"后侧围外板_大板刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"衣帽架_大板刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"落水槽_大板刚度":[[0,10,20,35,50,60], [0, 1,2,4,6,8,10]],
	"落水槽支架设计_Visual Check":{"A":10,"B":8,"C":6,"D":4}
}

