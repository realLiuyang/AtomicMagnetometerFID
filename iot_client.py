# iot_client.py
import json
import time
from typing import Optional

import paho.mqtt.client as mqtt

from log_config import logger
from mqtt_paras import Connect_Params, Post_Params, Set_Reply_Params


class IoTClientManager:
    """IoT 客户端管理器（单例模式）"""
    _instance: Optional["IoTClientManager"] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_manager, sys_vars):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        self.config_manager = config_manager
        self.sys_vars = sys_vars
        self.client: Optional[mqtt.Client] = None
        self.auth_info: Optional[Connect_Params] = None
        self.time_stamp = str(int(time.time() * 1000))
        self.post_payload = Post_Params()
        self.set_reply_payload = Set_Reply_Params()

        self._initialize_mqtt_client()

    def _initialize_mqtt_client(self):
        """完成 MQTT 客户端的初始化。"""
        self.auth_info = Connect_Params()
        self.auth_info.calculate_sign(
            self.config_manager.product_key,
            self.config_manager.device_name,
            self.config_manager.device_secret,
            self.config_manager.client_id,
            self.time_stamp,
        )
        self.client = mqtt.Client(self.auth_info.mqttClientId)
        self.client.username_pw_set(self.auth_info.mqttUsername, self.auth_info.mqttPassword)
        self.client.tls_set(self.config_manager.tls_crt)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        self._connect_to_mqtt()
        self.subscribe_topic(self.config_manager.set_thing_topic)

    def _connect_to_mqtt(self):
        """建立 MQTT 连接"""
        try:
            logger.info("尝试连接到 MQTT 服务器...")
            self.client.connect(self.config_manager.host, self.config_manager.port, self.config_manager.keep_alive)
            self.client.loop_start()
            logger.info("MQTT 服务器连接已启动")
        except Exception as e:
            logger.error(f"MQTT 连接失败：{e}")
            raise Exception("无法连接到 MQTT 服务器") from e

    def _on_connect(self, client: mqtt.Client, userdata, flags, rc: int) -> None:
        if rc == 0:
            logger.info("MQTT 连接成功")
        else:
            logger.error(f"MQTT 连接失败，错误代码：{rc}")

    def _on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
        topic = msg.topic
        payload = msg.payload.decode()
        logger.info(f"收到消息 - 主题：{topic}, 内容：{payload}")
        if self.config_manager.set_thing_topic in topic:
            self._process_property_change(payload)

    def _process_property_change(self, payload: str) -> None:
        try:
            msg = json.loads(payload)
            params = msg["params"]

            for key, value in params.items():
                if self.sys_vars.is_variable_present(key):
                    self.sys_vars.set_variable_value(key, value)

            # 直接传递 params 字典，而非重新序列化
            self.publish_set_reply_message(msg["id"])
            self.publish_post_message(params)  # 直接传递 params 数据
        except json.JSONDecodeError:
            logger.error(f"无效的 JSON 格式：{payload}")
        except Exception as e:
            logger.exception(f"处理设备属性变更时发生错误：{e}")

    def subscribe_topic(self, topic: Optional[str] = None) -> None:
        topic = topic or self.config_manager.post_reply_thing_topic
        self.client.subscribe(topic)
        logger.info(f"订阅主题：{topic}")

    def publish_post_message(self, params) -> None:
        try:
            topic = self.config_manager.post_thing_topic

            payload = self.post_payload.package_payload(params)
            self.client.publish(topic, payload)
            logger.info(f"上传属性消息 - 主题： {topic}, 内容：{payload}")
        except Exception as e:
            logger.error(f"上传属性消息失败：{e}")

    def publish_set_reply_message(self, id) -> None:
        try:
            topic = self.config_manager.set_reply_thing_topic
            payload = self.set_reply_payload.package_payload(id)
            self.client.publish(topic, payload)
            logger.info(f"发布确认消息 - 主题： {topic}, 内容：{payload}")
        except Exception as e:
            logger.error(f"发布确认消息失败：{e}")

    def get_client(self) -> mqtt.Client:
        return self.client
