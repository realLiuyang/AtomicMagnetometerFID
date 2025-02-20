# data_log.py
import os

# 创建数据日志目录
DATA_LOG_DIR = "data_logs"
os.makedirs(DATA_LOG_DIR, exist_ok=True)

# 数据日志文件路径
DATA_LOG_FILE = os.path.join(DATA_LOG_DIR, "received_data.log")


def get_data_log_file():
    """返回数据日志文件路径"""
    return DATA_LOG_FILE
