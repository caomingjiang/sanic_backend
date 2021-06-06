import logging
import os
import platform
from confs.config import BASE_DIR

if str(platform.system()) == "Windows":
    from logging.handlers import RotatingFileHandler as LogHandler
else:
    from cloghandler import ConcurrentRotatingFileHandler as LogHandler

_log_file_size = 1 * 1024 * 1024 * 1024  # 1G

_log_path = os.path.join(BASE_DIR, 'logs')

if not os.path.exists(_log_path):
    os.mkdir(_log_path)

# -------------------------------运行日志（代码运行记录）-------------------------------
_code_log_file = os.path.join(_log_path, 'code.log')
_code_log_handler = LogHandler(_code_log_file, "a", _log_file_size, 1000, encoding='utf-8')
_code_log_formatter = logging.Formatter('%(levelname)s %(asctime)s %(pathname)s %(funcName)s '
                                        'line:%(lineno)d %(message)s')
_code_log_handler.setFormatter(_code_log_formatter)
# 此处设置logger名称
code_log = logging.getLogger('ikd-code-log')
code_log.setLevel(logging.INFO)
code_log.addHandler(_code_log_handler)


# -------------------------------访问日志（记录访问的url和body）----------------------------------------
_access_log_file = os.path.join(_log_path, 'access.log')
_access_log_handler = LogHandler(_access_log_file, "a", _log_file_size, 1000, encoding='utf-8')
_access_log_formatter = logging.Formatter('%(asctime)s:%(message)s')
_access_log_handler.setFormatter(_access_log_formatter)
access_log = logging.getLogger('ikd-access-log')
access_log.setLevel(logging.INFO)
access_log.addHandler(_access_log_handler)
