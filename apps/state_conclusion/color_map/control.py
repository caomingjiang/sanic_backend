from db import ColorMapDstiff, ColorMapNtfDr, ColorMapNtfRr, ColorMapSpindleNtfDr, ColorMapSpindleNtfRr
from collections import defaultdict


class ColorMapData(object):
    def __init__(self, se, car_info):
        self.se = se
        self.car_info = car_info

    def search_data(self, table_model):
        all_data = self.se.query(table_model).filter(table_model.car_info == self.car_info)
        map_data = defaultdict(dict)
        y_axis_dic = dict(table_model.DATA_TYPE_CHOICES)
        x_axis = set()
        for single_data in all_data:
            x_axis.add(single_data.frequency_range)
            y_axis_name = y_axis_dic[single_data.data_type]
            map_data[y_axis_name][single_data.frequency_range] = int(single_data.value)
        x_axis = list(sorted(list(x_axis), key=lambda x: int(x.split('-')[0]), reverse=False))
        y_axis = list(map_data.keys())
        y_axis.sort(reverse=True)
        color_data = []
        for y_index, y_name in enumerate(y_axis):
            single_y_data = map_data[y_name]
            for x_index, x_name in enumerate(x_axis):
                color_data.append([
                    x_index, y_index, single_y_data[x_name]
                ])
        ret_data = {
            'x_axis': x_axis,
            'y_axis': y_axis,
            'color_data': color_data,
        }
        return ret_data

    def dstiff_data(self):
        ret_data = self.search_data(ColorMapDstiff)
        return ret_data

    def ntf_dr_data(self):
        ret_data = self.search_data(ColorMapNtfDr)
        return ret_data

    def ntf_rr_data(self):
        ret_data = self.search_data(ColorMapNtfRr)
        return ret_data

    def spindle_ntf_dr_data(self):
        ret_data = self.search_data(ColorMapSpindleNtfDr)
        return ret_data

    def spindle_ntf_rr_data(self):
        ret_data = self.search_data(ColorMapSpindleNtfRr)
        return ret_data

    def get_data(self):
        dstiff = self.dstiff_data()
        ntf_dr = self.ntf_dr_data()
        ntf_rr = self.ntf_rr_data()
        spindle_ntf_dr = self.spindle_ntf_dr_data()
        spindle_ntf_rr = self.spindle_ntf_rr_data()

        ret_data = {
            'dstiff': dstiff,
            'ntf_dr': ntf_dr,
            'ntf_rr': ntf_rr,
            'spindle_ntf_dr': spindle_ntf_dr,
            'spindle_ntf_rr': spindle_ntf_rr,
        }
        return ret_data


