import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MYSQL_CONFIG = {
    'db': 'luzao',
    'user': 'root',
    'password': 'root',
    'host': '127.0.0.1',
    'port': 3306,
}

SECRET_KEY = '123123213213'
TOKEN_EXPIRES = 8 * 60 * 60  # 秒

# 文件上传的文件夹路径
UPLOAD_DIR = os.path.join(BASE_DIR, 'upload')
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

EXCEL_MODAL_DIR = os.path.join(BASE_DIR, 'excel_modal')



