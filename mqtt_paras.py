# mqtt_paras.py
import hmac
import json
import random
from hashlib import sha1


class Connect_Params:
    def __init__(self):
        self.mqttClientId = ''
        self.mqttUsername = ''
        self.mqttPassword = ''

    def calculate_sign(self, productKey, deviceName, deviceSecret, clientId, timeStamp):
        """
        计算 MQTT 客户端连接所需的签名。
        :param productKey: 产品标识
        :param deviceName: 设备名称
        :param deviceSecret: 设备密钥
        :param clientId: 客户端ID
        :param timeStamp: 时间戳
        """
        # 设置客户端ID和用户名
        self.mqttClientId = f"{clientId}|securemode=2,signmethod=hmacsha1,timestamp={timeStamp}|"
        self.mqttUsername = f"{deviceName}&{productKey}"

        # 构建签名内容
        content = f"clientId{clientId}deviceName{deviceName}productKey{productKey}timestamp{timeStamp}"

        # 使用 HMAC-SHA1 进行签名
        self.mqttPassword = hmac.new(deviceSecret.encode(), content.encode(), sha1).hexdigest()


class Post_Params:
    def __init__(self):
        self.PostJson = {}

    def package_payload(self, params):
        """
        打包数据为阿里云 IoT 平台所需的消息格式。
        :param params: 设备属性数据
        :return: JSON 格式的字符串
        """
        # 使用随机数生成唯一的请求 ID
        self.PostJson["id"] = random.randint(0, 999999)
        self.PostJson["version"] = "1.0"
        self.PostJson["params"] = params
        self.PostJson["method"] = "thing.event.property.post"

        # 返回 JSON 字符串
        return json.dumps(self.PostJson)


class Set_Reply_Params:
    def __init__(self):
        self.SetReplyJson = {}

    def package_payload(self, ID):
        """
        打包数据为阿里云 IoT 平台所需的消息格式。
        :return: JSON 格式的字符串
        """
        self.SetReplyJson["id"] = ID
        self.SetReplyJson["code"] = 200
        self.SetReplyJson["data"] = {}
        self.SetReplyJson["message"] = "success"
        self.SetReplyJson["version"] = "1.0"

        # 返回 JSON 字符串
        return json.dumps(self.SetReplyJson)
