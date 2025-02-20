# data_process.py
from init import config_manager
from log_config import logger


def clean_value(value):
    # 去除空字符和其他可能的控制字符
    return value.replace('\x00', '').strip()


def process_line(line):
    """解析一行数据并计算磁场值"""
    try:
        parts = line.split("\t")
        if not (len(parts) == 4 or len(parts) == 5):
            logger.exception(f"数据格式错误: {line}")
            raise ValueError("数据格式错误")

        # 使用辅助函数清洗数据字段
        mag1_fre = float(clean_value(parts[0]))
        mag2_fre = float(clean_value(parts[1]))
        voltage1 = float(clean_value(parts[2]))
        voltage2 = float(clean_value(parts[3]))

        if len(parts) == 5:
            serial_number = int(clean_value(parts[4]))
        else:
            serial_number = 0

        mag1 = mag1_fre / config_manager.rb87_ggr
        mag2 = mag2_fre / config_manager.rb87_ggr

        return {
            "Mag1": mag1,
            "Mag2": mag2,
            "Voltage1": voltage1,
            "Voltage2": voltage2,
            "SerialNumber": serial_number
        }
    except ValueError as e:
        logger.exception(f"解析数据失败: {e}, 数据行: {line}")
    return None


def process_period_data(data, func):
    """
    对一个时间段的数据列表进行统计处理。

    参数:
        data (list): 包含多个 JSON 数据的列表，每个元素是字典，键为 'Mag1', 'Mag2', 'Voltage1', 'Voltage2', 'SerialNumber'。
        func (callable): 一个函数，可以是 max, min, statistics.mean 或其他函数。

    返回:
        dict: 包含处理结果的 JSON 数据。
    """
    if not data:
        logger.info("数据列表为空，无法处理")
        return {}

    try:
        result = {}
        for key in ["Mag1", "Mag2", "Voltage1", "Voltage2"]:
            values = [entry[key] for entry in data]
            result[key] = func(values)

        result["SerialNumber"] = data[-1]["SerialNumber"]

        return result
    except Exception as e:
        logger.exception(f"处理数据时出现错误: {e}")
        return {}
