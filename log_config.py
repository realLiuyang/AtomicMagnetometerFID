# log_config.py
import logging
import os
from logging.handlers import TimedRotatingFileHandler

# 创建 logs 目录
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 日志文件路径
APP_LOG_FILE = os.path.join(LOG_DIR, "app.log")

logger = logging.getLogger("AppLogger")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s"
)

app_log_handler = TimedRotatingFileHandler(
    APP_LOG_FILE, when="midnight", interval=1, backupCount=7, encoding="utf-8"
)
app_log_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(app_log_handler)
logger.addHandler(console_handler)

logger.info("日志系统初始化完成")
