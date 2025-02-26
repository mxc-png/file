
# 本示例程序演示如何使用 seekfree 库的 BLDC_CONTROLLER 类接口
# 使用 RT1021-MicroPython 核心板搭配 STC 无刷电调测试

# 示例程序运行效果为按一次 C15 按键后启动
# 随后无刷电机加减速转动
# C4 LED 会不间断闪烁
# 当 C14 引脚电平出现变化时退出测试程序

# 从 machine 库包含所有内容
from machine import *

# 从 seekfree 库包含 BLDC_CONTROLLER
from seekfree import BLDC_CONTROLLER

# 包含 gc time 类
import gc
import time

# 核心板上 C4 是 LED
# 学习板上 C14  对应二号拨码开关
# 核心板上 C15 是按键

# 调用 machine 库的 Pin 类实例化一个引脚对象
# 配置参数为 引脚名称 引脚方向 模式配置 默认电平
# 详细内容参考 固件接口说明
led     = Pin('C4' , Pin.OUT, pull = Pin.PULL_UP_47K, value = True)
switch2 = Pin('C14' , Pin.IN , pull = Pin.PULL_UP_47K, value = True)
key1    = Pin('C15', Pin.IN , pull = Pin.PULL_UP_47K, value = True)

state2  = switch2.value()

# 初始 1.1ms 高电平 确保能够起转
high_level_us = 1100
# 动作方向
dir = 1
# 学习板上 BLDC 电调接口为 C25/C27
# index - 对应接口 [PWM_C25,PWM_C27]
# freq - 可选参数 PWM 频率 范围 50-300 默认 50
# highlevel_us - 可选参数 初始的高电平时长 范围 1000-2000 默认 1000
bldc1 = BLDC_CONTROLLER(BLDC_CONTROLLER.PWM_C25, freq=300, highlevel_us = 1000)
bldc2 = BLDC_CONTROLLER(BLDC_CONTROLLER.PWM_C27, freq=300, highlevel_us = 1000)

# 电调一般起转需要在 1.1ms 高电平时间比较保险
# 因为 电机各不一样 会有一些死区差异 同时安装后有负载差异

# 需要按一次按键启动
print("Wait for KEY-C15 to be pressed.\r\n")
while True:
    time.sleep_ms(100)
    led.toggle()
    if 0 == key1.value():
        print("BLDC Controller test running.\r\n")
        print("Press KEY-C15 to suspend the program.\r\n")
        time.sleep_ms(300)
        break

while True:
    time.sleep_ms(100)
    led.toggle()
    # 往复计算 BLDC 电调速度
    if dir:
        high_level_us = high_level_us + 5
        if high_level_us >= 1250:
            dir = 0
    else:
        high_level_us = high_level_us - 5
        if high_level_us <= 1100:
            dir = 1
    
    # 设置更新高电平时间输出
    bldc1.highlevel_us(high_level_us)
    bldc2.highlevel_us(high_level_us)
    
    if 0 == key1.value():
        print("Suspend.\r\n")
        print("Wait for KEY-C15 to be pressed.\r\n")
        bldc1.highlevel_us(1000)
        bldc2.highlevel_us(1000)
        time.sleep_ms(300)
        while True:
            if 0 == key1.value():
                print("BLDC Controller test running.\r\n")
                print("Press KEY-C15 to suspend the program.\r\n")
                high_level_us = 1100
                dir = 1
                time.sleep_ms(300)
                break
    
    # 如果拨码开关打开 对应引脚拉低 就退出循环
    # 这么做是为了防止写错代码导致异常 有一个退出的手段
    if switch2.value() != state2:
        print("Test program stop.")
        break
    
    # 回收内存
    gc.collect()
