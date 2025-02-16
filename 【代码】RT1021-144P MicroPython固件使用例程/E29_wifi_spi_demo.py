
# 本示例程序演示如何使用 seekfree 库的 WIFI_SPI 类接口
# 使用 RT1021-MicroPython 核心板搭配对应拓展学习板与 WIFI_SPI 模块测试
# 当 D9 引脚电平出现变化时退出测试程序

# 示例程序运行效果是通过无线串口模块接收逐飞助手下发的调参数据
# 显示在 Thonny Shell 控制台并发送回逐飞助手的虚拟示波器显示
# 如果看到 Thonny Shell 控制台输出 ValueError: Module init fault. 报错
# 就证明 WIFI_SPI 模块连接异常 或者模块型号不对 或者模块损坏
# 请检查模块型号是否正确 接线是否正常 线路是否导通 无法解决时请联系技术支持

# 从 machine 库包含所有内容
from machine import *

# 从 seekfree 库包含 WIFI_SPI
from seekfree import WIFI_SPI

# 包含 gc time 类
import gc
import time

# 核心板上 C4 是 LED
# 学习板上 D9  对应二号拨码开关

# 调用 machine 库的 Pin 类实例化一个引脚对象
# 配置参数为 引脚名称 引脚方向 模式配置 默认电平
# 详细内容参考 固件接口说明
led     = Pin('C4' , Pin.OUT, pull = Pin.PULL_UP_47K, value = True)
switch2 = Pin('D9' , Pin.IN , pull = Pin.PULL_UP_47K, value = True)

state2  = switch2.value()

# 实例化 WIFI_SPI 模块
# wifi_ssid     WiFi 名称 字符串
# pass_word     WiFi 密码 字符串
# connect_type  连接类型 WIFI_SPI.TCP_CONNECT / WIFI_SPI.UDP_CONNECT
# ip_addr       目标连接地址 字符串
# connect_port  目标连接端口 字符串
# wifi = WIFI_SPI("WIFI_NAME", "WIFI_PASSWORD", WIFI_SPI.TCP_CONNECT, "192.168.1.13", "8086")
wifi = WIFI_SPI("SEEKFREE_2.4G", "SEEKFREEV2", WIFI_SPI.TCP_CONNECT, "192.168.2.72", "8086")
print("Test start.\r\n")

# 发送字符串的函数
wifi.send_str("Hello World.\r\n")
time.sleep_ms(500)

# data_analysis 数据解析接口 适配逐飞助手的无线调参功能
data_flag = wifi.data_analysis()
data_wave = [0,0,0,0,0,0,0,0]
for i in range(0,8):
    # get_data 获取调参通道数据 只有一个参数范围 [0-7]
    data_wave[i] = wifi.get_data(i)

while True:
    time.sleep_ms(50)
    led.toggle()
    
    # 定期进行数据解析
    data_flag = wifi.data_analysis()
    for i in range(0,8):
        # 判断哪个通道有数据更新
        if (data_flag[i]):
            # 数据更新到缓冲
            data_wave[i] = wifi.get_data(i)
            # 将更新的通道数据输出到 Thonny 的控制台
            print("Data[{:<6}] updata : {:<.3f}.\r\n".format(i,data_wave[i]))
            
    # send_oscilloscope 将最多八个通道虚拟示波器数据上传到逐飞助手
    # 不需要这么多数据的话就只填自己需要的 只有两个数据就只填两个参数
    wifi.send_oscilloscope(
        data_wave[0],data_wave[1],data_wave[2],data_wave[3],
        data_wave[4],data_wave[5],data_wave[6],data_wave[7])
    
    # 如果拨码开关打开 对应引脚拉低 就退出循环
    # 这么做是为了防止写错代码导致异常 有一个退出的手段
    if switch2.value() != state2:
        print("Test program stop.")
        break
    
    # 回收内存
    gc.collect()
