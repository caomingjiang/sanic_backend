from db import ChassisBase, ChassisDetail
import xlwt
from collections import defaultdict
from io import BytesIO


class ExportSingleData(object):
    def __init__(self, se, car_info):
        self.se = se
        self.car_info = car_info
        self.wb = xlwt.Workbook(encoding='utf8')

    def write_chassis_base(self):
        chassis_bases = self.se.query(ChassisBase).filter(ChassisBase.car_info == self.car_info)
        chassis_base_dic = defaultdict(dict)
        data_type_dic = dict(ChassisBase.DATA_TYPE_CHOICES)
        data_type_dic.pop('tire_score')
        tire_score = 0
        for chassis_base in chassis_bases:
            data_type = chassis_base.data_type
            if data_type == 'tire_score':
                tire_score = chassis_base.value
                continue
            else:
                col1_col2 = data_type_dic.get(data_type)
                col1, col2 = col1_col2.split(' -- ')
                chassis_base_dic[col1].update({
                    col2: {
                        'value': chassis_base.value,
                        'score': chassis_base.score
                    }
                })
        ws = self.wb.add_sheet('sheet1')

        titles = ['零部件', '指标', '数据输入', '分值']
        for col_num, title in enumerate(titles):
            ws.write(0, col_num, title)

        row_num = 1
        for k1, v1 in chassis_base_dic.items():
            ws.write_merge(row_num, row_num + len(v1) - 1, 0, 0, k1)
            for k2, v2 in v1.items():
                ws.write(row_num, 1, k2)
                ws.write(row_num, 2, v2['value'])
                ws.write(row_num, 3, v2['score'])
                row_num += 1
        ws.write_merge(row_num, row_num, 0, 3, f'轮胎总分：{tire_score}分')

    def write_chassis_detail(self):
        chassis_details = self.se.query(ChassisDetail).filter(ChassisDetail.car_info == self.car_info)
        chassis_detail_dic = defaultdict(dict)
        data_type_dic = dict(ChassisDetail.DATA_TYPE_CHOICES)
        for chassis_detail in chassis_details:
            data_type = chassis_detail.data_type
            col1_col2 = data_type_dic.get(data_type)
            col1, col2 = col1_col2.split(' -- ')
            chassis_detail_dic[col1].update({
                col2: {
                    'molecule': chassis_detail.molecule,
                    'denominator': chassis_detail.denominator,
                    'stiffness_ratio': chassis_detail.stiffness_ratio,
                    'score': chassis_detail.score,
                }
            })
        ws = self.wb.add_sheet('sheet2')
        titles = ['零部件', '指标', '数据输入', '刚度比', '分值']
        for col_num, title in enumerate(titles):
            ws.write(0, col_num, title)

        row_num = 1
        for k1, v1 in chassis_detail_dic.items():
            ws.write_merge(row_num, row_num + len(v1) - 1, 0, 0, k1)
            for k2, v2 in v1.items():
                ws.write(row_num, 1, k2)
                ws.write(row_num, 2, f'{v2["molecule"]}/{v2["denominator"]}')
                ws.write(row_num, 3, v2['stiffness_ratio'])
                ws.write(row_num, 4, v2['score'])
                row_num += 1

    def export(self):
        self.write_chassis_base()
        self.write_chassis_detail()
        bio = BytesIO()
        self.wb.save(bio)
        return bio.getvalue()
