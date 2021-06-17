#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 23:41:12 2021

@author: liangdongkai
"""

import pandas as pd 
import numpy as np
from ai.map_dict_utils import *
from ai.hyper_parmas import div_hyper_params
from ai.single_params import fuchejia, xiabaibi, cheshen
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

def single_fuchejia_func(key, value):
    '''
    key: name1_name2
    value: input value
    '''

    thres_array = fuchejia[key][0]
    score = fuchejia[key][1]
    # index = get_loc(value, thres_array)

    index = bisect_left(thres_array, value)
    # index = bisect_right(thres_array, value)

    if index < len(score):
        return score[index]
    else:
        return 'error'


def single_xiabaibi_func(key, value):
    '''
    key: name1_name2
    value: input value
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

def single_cheshen_func(key, value):
    '''
    key: name1_name2
    value: input value
    '''

    thres_array = cheshen[key][0]
    score = cheshen[key][1]
    # index = get_loc(value, thres_array)

    index = bisect_left(thres_array, value)
    # index = bisect_right(thres_array, value)

    if index < len(score):
        return score[index]
    else:
        return 'error'
def single_predict_func(data_map):
    '''
    data_map: dict
              {'key1':'value1','key2':'value2', ...}
    '''
    score = 0.0
    for key, value in data_map.items():
        score += 0.2 * float(value)
        
    return score

def dstiff_colourmap(ori_df):
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
    
def Multi_Score_Predict(colourmap_dict, weights_dict, adjust_value=115):
    '''
    colourmap_dict : dstff_df, ntf_df, spindle_ntf_df, 
    weights_map : weights_df
    '''
    
    x = colourmap_dict['dstiff'].drop('频率',1).T.as_matrix()
    y = weights_dict['dstiff'].drop('name',1).drop('dim',1).as_matrix()
    dstff_matrix =  x * y
    
    x = colourmap_dict['ntf_dr'].drop('频率',1).T.as_matrix()
    y = weights_dict['ntf_dr'].drop('name',1).drop('dim',1).as_matrix()
    ntf_dr_matrix =  x * y
    
    x = colourmap_dict['ntf_rr'].drop('频率',1).T.as_matrix()
    y = weights_dict['ntf_rr'].drop('name',1).drop('dim',1).as_matrix()
    ntf_rr_matrix =  x * y
    
    x = colourmap_dict['spindle_dr'].drop('频率',1).T.as_matrix()
    y = weights_dict['spindle_dr'].drop('name',1).drop('dim',1).as_matrix()
    spindle_dr_matrix =  x * y
    
    x = colourmap_dict['spindle_rr'].drop('频率',1).T.as_matrix()
    y = weights_dict['spindle_rr'].drop('name',1).drop('dim',1).as_matrix()
    spindle_rr_matrix =  x * y
    
    DR_score = []
    for index, (d, ntf, spin) in enumerate(zip(dstff_matrix.T, ntf_dr_matrix.T, spindle_dr_matrix.T)):
        aggregate = sum(d) + sum(ntf) + sum(spin)
        DR_score.append(adjust_value - aggregate/div_hyper_params[index])
        
    RR_score = []
    for index, (d, ntf, spin) in enumerate(zip(dstff_matrix.T, ntf_rr_matrix.T, spindle_rr_matrix.T)):
        aggregate = sum(d) + sum(ntf) + sum(spin)
        RR_score.append(adjust_value - aggregate/div_hyper_params[index])
        
        
    return DR_score, RR_score


if __name__ == "__main__":
    
    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_Dstiff.xlsx')
    dstiff_colourmap = dstiff_colourmap(ori_df)
    
    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_NTF-DR.xlsx')
    ntf_dr_colourmap = ntf_colourmap(ori_df, 'ntf')
    
    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_NTF-RR.xlsx')
    ntf_rr_colourmap = ntf_colourmap(ori_df, 'ntf')
    
    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_SpindleNTF-DR.xlsx')
    spindle_dr_colourmap = ntf_colourmap(ori_df, 'spindle_ntf')
    
    ori_df = pd.read_excel('./最新输入模板，以此为准/原始输入_SpindleNTF-RR.xlsx')
    spindle_rr_colourmap = ntf_colourmap(ori_df, 'spindle_ntf')
    
    colourmap_dict = {}
    colourmap_dict['dstiff'] = dstiff_colourmap
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
    
    
    DR_score, RR_score = Multi_Score_Predict(colourmap_dict, weights_dict)

