#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 00:14:08 2021

@author: liangdongkai
"""
# import pandas as pd
# target = pd.read_excel('/Users/liangdongkai/python_project/auto/0605/权系数/DSTIFF_目标转换字段判断依据.xlsx')
# distiff_target_map = {}
# for index, item in target.iterrows():
#     distiff_target_map[item['动刚度DSTIFF目标'] + item['dim']] = item['Target'] 

dstiff_target_map = {'前悬左塔座接附点X': 10,
                     '前悬左塔座接附点Y': 10,
                     '前悬左塔座接附点Z': 20,
                     '前悬左控制臂前接附点X': 12,
                     '前悬左控制臂前接附点Y': 12,
                     '前悬左控制臂前接附点Z': 7,
                     '前悬左控制臂后接附点X': 10,
                     '前悬左控制臂后接附点Y': 5,
                     '前悬左控制臂后接附点Z': 5,
                     '左刀锋臂接附点X': 15,
                     '左刀锋臂接附点Y': 5,
                     '左刀锋臂接附点Z': 15,
                     '后悬左减震接附点X': 10,
                     '后悬左减震接附点Y': 5,
                     '后悬左减震接附点Z': 15,
                     '后悬左弹簧接附点X': 15,
                     '后悬左弹簧接附点Y': 5,
                     '后悬左弹簧接附点Z': 6,
                     '后悬左上控制臂接附点X': 5,
                     '后悬左上控制臂接附点Y': 15,
                     '后悬左上控制臂接附点Z': 5,
                     '后悬左下拉杆接附点X': 5,
                     '后悬左下拉杆接附点Y': 15,
                     '后悬左下拉杆接附点Z': 5,
                     '后悬左弹簧臂内接附点X': 5,
                     '后悬左弹簧臂内接附点Y': 15,
                     '后悬左弹簧臂内接附点Z': 5}

def dstiff_score(x, target):
    if x > 2000*target:
        return 10
    elif 1500*target < x <= 2000*target:
        return 9
    elif 1000*target < x <= 1500*target:
        return 8
    elif 900*target< x <= 1000*target:
        return 7
    elif 800*target < x <= 900*target:
        return 6
    elif 700*target < x <= 800*target:
        return 5
    elif 600*target < x <= 700*target:
        return 4
    elif 500*target < x <= 600*target:
        return 3
    elif 400*target < x <= 500*target:
        return 2
    elif 0 < x <= 400*target:
        return 1
       
    
def ntf_score(x):
    if x < 45:
        return 10
    elif 45 <= x < 48:
        return 9
    elif 48 <= x < 50:
        return 8
    elif 50 <= x < 55:
        return 7
    elif 55 <= x < 60:
        return 6
    elif 60 <= x < 65:
        return 5
    elif 65 <= x < 70:
        return 4
    elif x >= 70 :
        return 1


def spindle_ntf_score(x):
    if x < 30:
        return 10
    elif 30 <= x < 33:
        return 9
    elif 33 <= x < 36:
        return 8
    elif 36 <= x < 40:
        return 7
    elif 40 <= x < 42:
        return 6
    elif 42 <= x < 45:
        return 5
    elif 45 <= x < 50:
        return 4
    elif 50 <= x < 55 :
        return 3
    elif x >= 55:
        return 1

