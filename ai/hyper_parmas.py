#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 22:13:40 2021

@author: liangdongkai
"""

div_hyper_params = [2.6, 2.6, 2.2, 2.8, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1]

artifical_params = {
    "div_hyper_params": [2.6, 2.6, 2.2, 2.8, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1],
    "adjust_value": 115
}
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