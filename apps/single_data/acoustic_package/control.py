from db import AticPkgConfs
import xlwt
from collections import defaultdict
from io import BytesIO


class ExportAcousticPackage(object):
    def __init__(self, se, car_info):
        self.se = se
        self.car_info = car_info
        self.wb = xlwt.Workbook(encoding='utf8')

    def write_atic_pkg_data(self):
        apc_objs = self.se.query(AticPkgConfs).filter(
            AticPkgConfs.car_info == self.car_info
        )
        apc_dic = defaultdict(dict)
        data_type_dic = dict(AticPkgConfs.DATA_TYPE_CHOICES)
        for apc_obj in apc_objs:
            data_type = apc_obj.data_type
            col1_col2 = data_type_dic.get(data_type)
            col1, col2 = col1_col2.split('_', maxsplit=1)
            apc_dic[col1].update({
                col2: {
                    'conf_item': apc_obj.conf_item,
                    'weight': apc_obj.weight,
                    'score': apc_obj.score,
                    'cost': apc_obj.cost,
                }
            })
        ws = self.wb.add_sheet('sheet1')

        titles = ['位置', '组成', '策略选型', '重量', '分值', '成本']
        for col_num, title in enumerate(titles):
            ws.write(0, col_num, title)

        row_num = 1
        total_weight, total_cost = 0, 0
        for k1, v1 in apc_dic.items():
            ws.write_merge(row_num, row_num + len(v1) - 1, 0, 0, k1)
            for k2, v2 in v1.items():
                weight = v2['weight']
                cost = v2['cost']
                total_weight += weight
                total_cost += cost
                ws.write(row_num, 1, k2)
                ws.write(row_num, 2, v2['conf_item'])
                ws.write(row_num, 3, weight)
                ws.write(row_num, 4, v2['score'])
                ws.write(row_num, 5, cost)
                row_num += 1
        ws.write_merge(row_num, row_num, 0, 1, '')
        ws.write(row_num, 2, '总重量')
        ws.write(row_num, 3, total_weight)
        ws.write(row_num, 4, '总成本')
        ws.write(row_num, 5, total_cost)

    def export(self):
        self.write_atic_pkg_data()
        bio = BytesIO()
        self.wb.save(bio)
        return bio.getvalue()
