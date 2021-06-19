from db import CarBody
import xlwt
from io import BytesIO


class ExportCarBodyData(object):
    def __init__(self, se, car_info):
        self.se = se
        self.car_info = car_info
        self.wb = xlwt.Workbook(encoding='utf8')

    def write_car_body(self):
        car_body_data = self.se.query(CarBody).filter(CarBody.car_info == self.car_info)
        ws = self.wb.add_sheet('sheet1')
        titles = ['零部件/位置', '评价指标', '数据输入', '分值']
        for col_num, title in enumerate(titles):
            ws.write(0, col_num, title)
        data_type_dic = dict(CarBody.DATA_TYPE_CHOICES)
        for row_num, car_body in enumerate(car_body_data):
            data_type = car_body.data_type
            col1_col2 = data_type_dic.get(data_type)
            col1, col2 = col1_col2.split(' -- ')
            ws.write(row_num + 1, 0, col1)
            ws.write(row_num + 1, 1, col2)
            ws.write(row_num + 1, 2, car_body.value or '')
            ws.write(row_num + 1, 3, car_body.score)

    def export(self):
        self.write_car_body()
        bio = BytesIO()
        self.wb.save(bio)
        return bio.getvalue()
