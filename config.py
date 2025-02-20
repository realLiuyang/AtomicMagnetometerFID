# config.py
import statistics

from log_config import logger


class ConfigManager:
    def __init__(self):
        # 配置相关的属性初始化
        self.product_key = "k291qaoBsS7"
        self.device_name = "sensor1"
        self.device_secret = "fafe84e0870e64734b02d0f1d6caaf40"
        self.client_id = "210.45.127.191"

        self.post_thing_topic = f"/sys/{self.product_key}/{self.device_name}/thing/event/property/post"
        self.post_reply_thing_topic = f"/sys/{self.product_key}/{self.device_name}/thing/event/property/post_reply"
        self.set_thing_topic = f"/sys/{self.product_key}/{self.device_name}/thing/service/property/set"
        self.set_reply_thing_topic = f"/sys/{self.product_key}/{self.device_name}/thing/service/property/set_reply"

        self.host = "iot-06z00c11889tiw2.mqtt.iothub.aliyuncs.com"
        self.port = 1883

        self.serial_port = "/dev/ttyUSB0"
        self.baudrate = 115200
        self.rb87_ggr = 7.0

        self.filter_types = [0, 1, 2, 3]

        self.output_json_path = "output.json"

        self.tls_crt = "root.crt"
        self.keep_alive = 300


class VariableManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialize_variables()
        return cls._instance

    def initialize_variables(self):
        """初始化变量相关设置"""
        self.variables = {
            "Switch": 0,
            "WorkMode": 0,
            "FilterType": 0,  # 修正 typo
        }
        self.switch_table = [False, True]
        self.work_mode_table = [1000, 200]
        self.filter_type_functions = [
            statistics.mean,
            max,
            min,
            self.last
        ]

    def is_variable_present(self, name):
        """检查变量是否存在"""
        return name in self.variables

    def get_variable_value(self, name):
        """获取变量值"""
        if self.is_variable_present(name):
            return self.variables[name]
        logger.exception(f"变量 {name} 不存在")
        raise KeyError(f"变量 {name} 不存在")

    def set_variable_value(self, name, value):
        """设置变量值"""
        if self.is_variable_present(name):
            self.variables[name] = value
        else:
            logger.exception(f"变量 {name} 不存在")
            raise KeyError(f"变量 {name} 不存在")

    def get_converted_value(self, name):
        """获取变量的转换值"""
        if not self.is_variable_present(name):
            logger.exception(f"变量 {name} 不存在")
            raise KeyError(f"变量 {name} 不存在")

        value = self.variables[name]
        if name == "Switch":
            return self.switch_table[value]
        if name == "WorkMode":
            return self.work_mode_table[value]
        if name == "FilterType":
            return self.filter_type_functions[value]
        logger.exception(f"变量 {name} 不支持转换")
        raise ValueError(f"变量 {name} 不支持转换")

    @staticmethod
    def last(data):
        """返回列表中的最后一个值"""
        if not data:
            logger.exception("输入列表为空")
            raise ValueError("输入列表为空")
        return data[-1]
