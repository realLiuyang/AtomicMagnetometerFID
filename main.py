# main.py
import time
import data_process
from data_log import get_data_log_file
from init import sys_variables, device, serial_reader, raspi
from log_config import logger


def main():
    """主函数"""
    logger.info("进入主函数...")

    # 获取数据日志文件路径
    data_log_file_path = get_data_log_file()

    with open(data_log_file_path, "a", encoding="utf-8") as data_log_file:
        try:
            start_time = time.time()
            data_buffer = []

            while True:
                switch_status = sys_variables.get_converted_value("Switch")

                if switch_status:
                    try:
                        line = serial_reader.read_data()
                    except Exception as e:
                        logger.error(f"串口读取失败: {e}")
                        continue  # 继续下一次循环

                    if line:
                        logger.debug(f"接收到数据: {repr(line)}")

                        # 记录到日志文件
                        data_log_file.write(line + "\n")
                        data_log_file.flush()

                        # 解析数据
                        parsed_data = data_process.process_line(line)
                        if parsed_data:
                            logger.debug(f"处理后的数据: {parsed_data}")
                            data_buffer.append(parsed_data)

                    # 达到周期时间，处理数据
                    if (time.time() - start_time) * 1000 >= sys_variables.get_converted_value("WorkMode") and len(data_buffer) > 0:
                        processed_data = data_process.process_period_data(
                            data_buffer, sys_variables.get_converted_value("FilterType")
                        )

                        if processed_data:
                            system_info = raspi.get_system_info()

                            # 组合系统信息和传感器数据
                            payload = {**system_info, **processed_data}

                            logger.info(f"发布数据: {payload}")
                            device.publish_post_message(payload)

                            # 重置计时器 & 清空数据缓存
                            start_time = time.time()
                            data_buffer.clear()

                time.sleep(0.002)  # 适当延时，减少 CPU 负荷

        except KeyboardInterrupt:
            logger.info("系统关闭中...")
        except Exception as e:
            logger.exception(f"运行时错误: {e}")
        finally:
            try:
                if serial_reader.is_open:
                    serial_reader.close()
                    logger.info("串口已关闭")
            except Exception as e:
                logger.error(f"关闭串口时发生错误: {e}")

            logger.info(f"串口数据已保存至 {data_log_file_path}")
            logger.info("系统已安全退出")


if __name__ == "__main__":
    main()
