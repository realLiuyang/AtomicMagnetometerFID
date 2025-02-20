# 原子磁力仪数据采集与可视化系统

## **项目简介**

本项目旨在实现 **原子磁力仪数据的采集、传输、处理及可视化展示**。
 原子磁力仪通过 **USB 串口** 连接至 **树莓派**，树莓派接收数据后进行 **解析、处理** 并打包成 **JSON 格式**，
 随后利用 **4G 模块（USB 连接）** 上传至 **阿里云物联网平台**，数据进一步流转至 **IoT Studio 可视化平台**，
 最终通过 **Web 端 & 移动端** 进行显示，方便用户查看与分析数据。

此外，可视化平台提供了 **数据上传频率设定、滤波方式选择、数据上传启停等功能**，
 提升了数据管理的灵活性和易用性。

------

## **系统架构**

本项目包含以下核心组件：

1. **数据采集**
   - **原子磁力仪** 通过 **USB 串口** 发送磁场数据
   - **树莓派** 通过 **`serial_reader.py`** 读取串口数据
2. **数据处理**
   - 解析数据：去除异常字符，并转换为标准格式
   - 计算磁场强度、电压等信息
   - 支持 **滤波处理（均值、最大值、最小值）**
3. **数据上传**
   - 通过 **4G 模块（USB 连接）** 上传至 **阿里云 IoT**
   - 采用 **MQTT 协议** 进行数据推送
4. **数据可视化**
   - 阿里云 **IoT Studio** 用于数据存储 & 展示
   - **Web 端 & 移动端** 实时显示磁力仪数据

------

## **硬件连接**

本系统运行于 **树莓派**，并连接以下设备：

| 设备名称        | 连接方式 | 说明         |
| --------------- | -------- | ------------ |
| **原子磁力仪**  | USB 串口 | 采集磁场数据 |
| **4G 通信模块** | USB 连接 | 远程上传数据 |

------

## **环境依赖**

本项目基于 **Python 3.11** 开发，依赖以下库：

```bash
pip install paho-mqtt pyserial statistics
```

此外，建议使用 **虚拟环境** 进行管理：

```bash
# 创建虚拟环境
python3 -m venv myvenv

# 激活虚拟环境
source myvenv/bin/activate  # Linux/macOS
myvenv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

------

## **文件结构**

```
├── config.py             # 配置管理（MQTT、串口参数等）
├── data_log.py           # 记录串口数据日志
├── data_process.py       # 解析 & 处理数据
├── iot_client.py         # MQTT 通信管理
├── log_config.py         # 日志管理
├── main.py               # 主程序
├── mqtt_paras.py         # MQTT 认证参数
├── raspi_info.py         # 采集树莓派系统信息（CPU 温度、负载等）
├── serial_reader.py      # 串口数据读取
├── init.py               # 初始化各模块
└── README.md             # 项目文档
```

------

## **配置说明**

### **1. MQTT 设备参数 (`config.py`)**

在 `ConfigManager` 中，设置阿里云 MQTT 相关参数：

```python
self.product_key = "your_product_key"
self.device_name = "your_device_name"
self.device_secret = "your_device_secret"
self.client_id = "your_client_id"
self.host = "your_mqtt_host"
self.port = 1883
self.tls_crt = "root.crt"
```

### **2. 串口参数**

确保 `config.py` 中的 **串口参数** 设置正确：

```python
self.serial_port = "/dev/ttyUSB0"  # 磁力仪 USB 串口
self.baudrate = 115200
```

------

## **运行方式**

### **1. 手动启动**

确保 **树莓派连接了磁力仪和 4G 模块**，然后执行：

```bash
source myvenv/bin/activate  # 激活虚拟环境
python3 main.py             # 运行主程序
```

### **2. 开机自动运行**

编辑 `/etc/rc.local` 文件，在 `exit 0` 前添加：

```bash
cd /home/pi/Aliyun_Raspi_Mag
source myvenv/bin/activate
python3 main.py >> /var/log/mag_data.log 2>&1 &
```

------

## **日志 & 数据存储**

1. **日志文件**
   - 存储在 `logs/LOG_YYYYMMDD_HHMMSS.log`
   - 运行 `tail -f logs/LOG_*.log` 监控日志
2. **数据日志**
   - 记录原始串口数据到 `data_logs/received_data.log`
   - 运行 `cat data_logs/received_data.log` 查看数据

------

## **系统信息监控**

树莓派采集 **CPU 温度、使用率、内存占用**：

```python
system_info = raspi.get_system_info()
```

示例输出：

```json
{
    "CpuTemp": 55,
    "CpuUsedPer": 32,
    "MemUsedPer": 45
}
```

------

## **数据格式**

### **1. 串口原始数据格式**

磁力仪数据按 **行** 发送，每行包含 5 个字段：

```txt
Mag1_Fre    Mag2_Fre    Voltage1    Voltage2    SerialNumber
```

示例：

```txt
50.00       -50.00      4.95        5.47        1108
```

### **2. 解析后数据格式**

处理后数据以 **JSON** 格式上传：

```json
{
    "Mag1": 7.14,
    "Mag2": -7.14,
    "Voltage1": 4.95,
    "Voltage2": 5.47,
    "SerialNumber": 1108,
    "CpuTemp": 55,
    "CpuUsedPer": 32,
    "MemUsedPer": 45
}
```

------

## **故障排查**

### **1. 串口无法读取数据**

**检查串口设备是否连接：**

```bash
ls /dev/ttyUSB*
```

如果没有设备，尝试重新插拔 **磁力仪 USB 线**。

### **2. 4G 模块无法上传数据**

**检查 4G 设备是否正常识别：**

```bash
lsusb | grep 4G
```

### **3. 日志报错 `Permission Denied`**

如果 `logs/app.log` 目录 **无写入权限**：

```bash
sudo chmod -R 777 logs/
```

------

## **结论**

本项目实现了 **磁力仪数据采集、解析、上传与可视化**，
 结合 **树莓派 + 4G 模块 + 阿里云 IoT**，打造了一套完整的 **远程磁场监测系统**。

**🎯 主要功能：** 

**支持 USB 串口数据采集** 

**支持 MQTT 上传阿里云 IoT**

**实时监测树莓派状态**

**提供 Web & 移动端可视化展示**

------

## **TODO**

-  支持 **断点续传**
-  优化 **异常处理机制**
-  增加 **本地数据缓存