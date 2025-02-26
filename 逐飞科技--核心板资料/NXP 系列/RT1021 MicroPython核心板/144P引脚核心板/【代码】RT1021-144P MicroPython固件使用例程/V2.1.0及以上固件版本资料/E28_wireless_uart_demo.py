
# 本示例程序演示如何使用 seekfree 库的 WIRELESS_UART 类接口
# 使用 RT1021-MicroPython 核心板搭配对应拓展学习板与无线串口模块测试
# 当 D9 引脚电平出现变化时退出测试程序

# 示例程序运行效果是通过无线串口模块接收逐飞助手下发的调参数据
# 显示在 Thonny Shell 控制台并发送回逐飞助手的虚拟示波器显示
# 如果看到 Thonny Shell 控制台输出 ValueError: Module init fault. 报错
# 就证明 无线串口 模块连接异常 或者模块型号不对 或者模块损坏
# 请检查模块型号是否正确 接线是否正常 线路是否导通 无法解决时请联系技术支持

# 默认使用虚拟示波器的快速数据发送接口节约发送时间

# 需要连接对应 COM 口后打开 逐飞助手-虚拟示波器 界面！！！
# 需要连接对应 COM 口后打开 逐飞助手-虚拟示波器 界面！！！
# 需要连接对应 COM 口后打开 逐飞助手-虚拟示波器 界面！！！

# 如果想同时在串口助手串口能看到数据
# 可以选择使用虚拟示波器的 printf 协议
# 在 逐飞助手-虚拟示波器 界面的右下角有一个 printf 的开关
# 打开它后 使用 WIRELESS_UART.send_str 发送数据

# 从 machine 库包含所有内容
from machine import *

# 从 seekfree 库包含 WIRELESS_UART
from seekfree import WIRELESS_UART

# 包含 gc time 类
import gc
import time

# 核心板上 C4 是 LED
# 学习板上 D9 对应二号拨码开关
led     = Pin('C4' , Pin.OUT, value = True)
switch2 = Pin('D9' , Pin.IN , pull = Pin.PULL_UP_47K)
state2  = switch2.value()

# 显示帮助信息
WIRELESS_UART.help()
time.sleep_ms(500)

# 构造接口 用于构建一个 WIRELESS_UART 对象
#   WIRELESS_UART([baudrate])
#   baudrate    波特率 |   可选参数 默认 460800
wireless = WIRELESS_UART(460800)

# 其余接口：
# WIRELESS_UART.send_str(str)           # 发送字符串
#   str     字符数据    |   必要参数
# WIRELESS_UART.send_oscilloscope(d1,[d2, d3, d4, d5, d6, d7, d8])  # 逐飞助手虚拟示波器数据上传
#   dx      波形数据    |   至少一个数据 最多可以填八个数据 数据类型支持浮点数
# WIRELESS_UART.send_ccd_image(index)   # 逐飞助手 CCD 显示数据上传
#   index   接口编号    |   参数 [  CCD1_BUFFER_INDEX,      CCD2_BUFFER_INDEX, 
#                       |           CCD3_BUFFER_INDEX,      CCD4_BUFFER_INDEX, 
#                       |           CCD1_2_BUFFER_INDEX,    CCD3_4_BUFFER_INDEX] 
#                       |   分别代表 仅显示 CCD1 图像 、 仅显示 CCD2 图像 、 选择两个 CCD 图像一起显示
# WIRELESS_UART.data_analysis()         # 逐飞助手调参数据解析 会返回八个标志位的列表 标识各通道是否有数据更新
# WIRELESS_UART.get_data()              # 逐飞助手调参数据获取 会返回八个数据的列表

wireless.info()
time.sleep_ms(500)

# data_analysis 数据解析接口 适配逐飞助手的无线调参功能
data_flag = wireless.data_analysis()
data_wave = [0,0,0,0,0,0,0,0]
for i in range(0,8):
    # get_data 获取调参通道数据 只有一个参数范围 [0, 7]
    data_wave[i] = wireless.get_data(i)

while True:
    time.sleep_ms(50)
    led.toggle()
    
    # 定期进行数据解析
    data_flag = wireless.data_analysis()
    for i in range(0,8):
        # 判断哪个通道有数据更新
        if (data_flag[i]):
            # 数据更新到缓冲
            data_wave[i] = wireless.get_data(i)
            # 将更新的通道数据输出到 Thonny 的控制台
            print("Data[{:<6}] updata : {:<.3f}.\r\n".format(i,data_wave[i]))
            
    # send_oscilloscope 将最多八个通道虚拟示波器数据上传到逐飞助手
    # 不需要这么多数据的话就只填自己需要的 只有两个数据就只填两个参数
    wireless.send_oscilloscope(
        data_wave[0],data_wave[1],data_wave[2],data_wave[3],
        data_wave[4],data_wave[5],data_wave[6],data_wave[7])

    # 如果想同时在串口助手串口能看到数据
    # 可以选择使用虚拟示波器的 printf 协议
    # 在 逐飞助手-虚拟示波器 界面的右下角有一个 printf 的开关
    # 打开它后 使用 WIRELESS_UART.send_str 发送数据
    # wireless.send_str("Data:{:<f},{:<f},{:<f},{:<f},{:<f},{:<f},{:<f},{:<f}\n".format(
    #     data_wave[0],data_wave[1],data_wave[2],data_wave[3],
    #     data_wave[4],data_wave[5],data_wave[6],data_wave[7]))
    
    # 如果拨码开关打开 对应引脚拉低 就退出循环
    # 这么做是为了防止写错代码导致异常 有一个退出的手段
    if switch2.value() != state2:
        print("Test program stop.")
        break
    
    # 回收内存
    gc.collect()
