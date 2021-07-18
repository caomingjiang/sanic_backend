import os
from db import ColorMapDstiff, ColorMapNtfDr, ColorMapNtfRr, ColorMapSpindleNtfDr, ColorMapSpindleNtfRr, ModalMap
from collections import defaultdict
from common.common import get_orm_comment_dic
from confs.config import BASE_DIR
import xlsxwriter


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

    def modal_map_data(self):
        comment_dic = get_orm_comment_dic(ModalMap)
        [comment_dic.pop(key) for key in ['车型', '值范围', '更新时间', '创建时间']]
        sort_comment_list = list(comment_dic.items())[::-1]
        y_axis = [y[0] for y in sort_comment_list]
        x_axis = []
        color_data = []
        modal_map_objs = list(self.se.query(ModalMap).filter(
            ModalMap.car_info == self.car_info
        ).order_by(ModalMap.id.asc()))
        for x_index, modal_map in enumerate(modal_map_objs):
            x_axis.append(modal_map.value_range)
            for y_index, y_list in enumerate(sort_comment_list):
                value = getattr(modal_map, y_list[1]) or '-'
                color_data.append([
                    x_index, y_index, value
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
        modal_map = self.modal_map_data()
        dstiff = self.dstiff_data()
        ntf_dr = self.ntf_dr_data()
        ntf_rr = self.ntf_rr_data()
        spindle_ntf_dr = self.spindle_ntf_dr_data()
        spindle_ntf_rr = self.spindle_ntf_rr_data()

        ret_data = {
            'modal_map': modal_map,
            'dstiff': dstiff,
            'ntf_dr': ntf_dr,
            'ntf_rr': ntf_rr,
            'spindle_ntf_dr': spindle_ntf_dr,
            'spindle_ntf_rr': spindle_ntf_rr,
        }
        return ret_data

    def reset_data(self, x_axis, y_axis, color_data):
        ret_data = defaultdict(dict)
        for x_index, y_index, value in color_data:
            value = '' if value == '-' else value
            ret_data[y_axis[y_index]][x_axis[x_index]] = value
        return ret_data

    def export_excel(self):
        xlsx_path = os.path.join(BASE_DIR, 'tmp_color_map.xlsx')
        wb = xlsxwriter.Workbook(xlsx_path, {'constant_memory': True})
        ws = wb.add_worksheet('color_map')
        ws.set_column(0, 0, 35)
        base_data = self.get_data()
        row_num = 0
        common_style = self.get_cell_style(wb, 10, '#FFFFFF', bold=True)
        for data_type, data_dic in base_data.items():
            x_axis = data_dic['x_axis']
            y_axis = data_dic['y_axis']
            color_data = data_dic['color_data']
            tmp_rst_data = self.reset_data(x_axis, y_axis, color_data)
            ws.write(row_num, 0, '', common_style)
            for col, x in enumerate(x_axis):
                ws.write(row_num, col + 1, x, common_style)
            row_num += 1
            y_axis = y_axis[::-1]
            for y in y_axis:
                ws.write(row_num, 0, y, common_style)
                for col, x in enumerate(x_axis):
                    tmp_value = tmp_rst_data[y][x]
                    tmp_style = self.get_cell_style(wb, 10, self.get_color_str(tmp_value), bold=False)
                    ws.write(row_num, col + 1, tmp_value, tmp_style)
                row_num += 1
            row_num += 3
        wb.close()
        with open(xlsx_path, 'rb+') as f:
            ret_data = f.read()
        os.remove(xlsx_path)
        return ret_data

    @staticmethod
    def get_color_str(value):
        if value == '':
            return '#FFFFFF'
        if 0 <= value <= 5:
            color = '#FF0000'
        elif 5 < value <= 6:
            color = '#FFFF00'
        elif 6 < value <= 7:
            color = '#92D050'
        elif 7 < value <= 8:
            color = '#1A6DB2'
        elif 8 < value <= 10:
            color = '#003B68'
        else:
            color = '#FF0000'
        return color

    @staticmethod
    def get_cell_style(wb, font_size, back_color, bold=False):
        style = wb.add_format({
            'bold': bold,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': back_color,
            'text_wrap': True,
            'font_size': font_size
        })

        return style



