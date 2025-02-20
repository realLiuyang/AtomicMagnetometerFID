# serial_reader.py

import serial

from log_config import logger


class MagnetometerReader:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.serial_port = self.config_manager.serial_port
        self.baudrate = self.config_manager.baudrate
        self.rb87_ggr = self.config_manager.rb87_ggr
        self.filer_types = self.config_manager.filter_types
        self.serial_connection = None

        self.initialize_serial()

    def initialize_serial(self):
        """初始化串口连接"""
        try:
            self.serial_connection = serial.Serial(
                port=self.serial_port,
                baudrate=self.baudrate,
                timeout=0.02
            )
            logger.info(f"串口 {self.serial_port} 已打开，波特率 {self.baudrate}")
        except serial.SerialException as e:
            logger.exception(f"无法打开串口：{e}")
            exit(1)

    def read_data(self):
        """读取串口数据，并确保数据完整"""
        try:
            line = ""
            while True:
                chunk = self.serial_connection.read(1).decode("utf-8", errors="ignore")  # 逐字符读取
                line += chunk
                if chunk == "\n":  # 只有遇到换行符，才认为是完整行
                    break

            line = line.strip().replace("\x00", "")  # 去掉空字符
            return line

        except Exception as e:
            logger.error(f"读取串口数据失败: {e}")
            return None

    def close(self):
        """关闭串口"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            logger.info("串口已关闭")
