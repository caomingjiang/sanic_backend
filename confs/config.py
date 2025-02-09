import os
from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseSettings

CommonThreadPool = ThreadPoolExecutor(4)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config(BaseSettings):
    MYSQL_HOST: str
    MYSQL_PASSWORD: str
    MYSQL_USER: str
    MYSQL_DB: str
    MYSQL_PORT: int

    SECRET_KEY: str = "123123213213"
    TOKEN_EXPIRES: int = 8 * 60 * 60  # 秒

    UPLOAD_DIR: str = os.path.join(BASE_DIR, 'upload')
    EXCEL_MODAL_DIR: str = os.path.join(BASE_DIR, 'excel_modal')


env_config = Config(
    _env_file=os.path.join(BASE_DIR, ".env"),
    _env_file_encoding="utf-8",
)  # 环境变量中读取配置(Config类中可小写, 但设置的环境变量需大写)，变量生效优先级： 系统环境变量 -> .env文件 -> 默认


# 文件上传的文件夹路径
if not os.path.exists(env_config.UPLOAD_DIR):
    os.makedirs(env_config.UPLOAD_DIR)



