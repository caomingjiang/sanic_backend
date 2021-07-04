

def get_risk_tik_list(se, table_model, car_info):
    datas = se.query(table_model).filter(table_model.car_info == car_info, table_model.value < 2)
    data_comment_dic = dict(table_model.DATA_TYPE_CHOICES)
    ret_list = []
    for data in datas:
        tmp_content = f'[{data.frequency_range}]Hz频段 “{data_comment_dic[data.data_type]}” 有路噪超标风险！'
        ret_list.append(tmp_content)
    return ret_list

