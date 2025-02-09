import os
from confs.config import env_config
from common.common import get_orm_comment_dic
from flask import request
import zipfile
from datetime import datetime
from db import WDesignLibrary
import json


class AnalysisDesignLibraryZip(object):
    def __init__(self, se, zip_url):
        self.se = se
        today = datetime.now().strftime('%Y%m%d')
        user_id = getattr(request, 'user_id')
        self.zip_url = zip_url
        zip_name = os.path.basename(zip_url).rsplit('.', maxsplit=1)[0]
        self.extract_path = os.path.join(env_config.UPLOAD_DIR, str(user_id), today, zip_name)
        if not os.path.exists(self.extract_path):
            os.makedirs(self.extract_path)

    def save_zip(self):
        zip_path = os.path.join(env_config.UPLOAD_DIR, self.zip_url)
        zf = zipfile.ZipFile(zip_path, 'r')
        zf.extractall(self.extract_path)
        col_dic = get_orm_comment_dic(WDesignLibrary)
        type_dic = {
            value: key for key, value in WDesignLibrary.DATA_TYPE_CHOICES
        }
        for root, dirs, files in os.walk(self.extract_path):
            col_name = os.path.basename(root)
            data_type = os.path.basename(os.path.dirname(root)).replace('_', ' ')
            for img_file in files:
                image_dic = {
                    'name': img_file, 'url': os.path.join(root, img_file).replace(UPLOAD_DIR, '').lstrip('/')
                }
                self.save_design_lib_data(type_dic[data_type], col_dic[col_name], image_dic)
        self.se.commit()
        os.remove(zip_path)

    def save_design_lib_data(self, data_type, col, image_dic):
        dl_obj = self.se.query(WDesignLibrary).filter(
            WDesignLibrary.data_type == data_type
        ).first()
        now = datetime.now()
        save_data = json.dumps([image_dic], ensure_ascii=False)
        if dl_obj:
            setattr(dl_obj, col, save_data)
            dl_obj.update_time = now
        else:
            save_dic = {
                'data_type': data_type, col: save_data,
                'update_time': now, 'create_time': now
            }
            self.se.add(WDesignLibrary(**save_dic))

