# raspi_info.py
import os
import time

from log_config import logger


class RaspiInfo:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """初始化，可以添加其他必要的初始化内容"""

    @staticmethod
    def get_cpu_temperature():
        """获取 CPU 温度"""
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                # 转为摄氏度并保留整数
                return int(float(f.read().strip()) / 1000.0)
        except FileNotFoundError:
            logger.error("未找到 CPU 温度文件")
            return None

    @staticmethod
    def get_cpu_usage():
        """获取 CPU 使用率"""
        try:
            load = os.getloadavg()[0]  # 获取 1 分钟平均负载
            return int(load * 100)  # 转为整数百分比
        except Exception as e:
            logger.error(f"获取 CPU 使用率时出错: {e}")
            return None

    @staticmethod
    def get_ram_usage():
        """获取 RAM 使用率"""
        try:
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
            mem_info = {}
            for line in lines:
                parts = line.split(":")
                if len(parts) == 2:
                    mem_info[parts[0].strip()] = int(parts[1].strip().split()[0])  # 提取数值，单位为 KB

            total = mem_info.get("MemTotal", 0)
            free = mem_info.get("MemFree", 0) + mem_info.get("Buffers", 0) + mem_info.get("Cached", 0)
            used = total - free

            return int((used / total) * 100) if total > 0 else None  # 转为整数百分比
        except Exception as e:
            logger.error(f"获取 RAM 使用率时出错: {e}")
            return None

    def get_system_info(self):
        """获取系统信息"""
        # 当前时间
        time_current = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 获取信息
        cpu_temp = self.get_cpu_temperature()
        cpu_usage = self.get_cpu_usage()
        ram_usage = self.get_ram_usage()

        # 汇总信息
        system_info = {
            # "Time": time_current,
            "CpuTemp": cpu_temp,
            "CpuUsedPer": cpu_usage,
            "MemUsedPer": ram_usage,
        }

        return system_info
